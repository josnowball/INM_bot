"""
CAPTCHA solving via Telegram forwarding.

Flow:
1. Playwright detects a CAPTCHA on the government site
2. Takes a screenshot of the CAPTCHA element
3. Sends the screenshot to the user's Telegram chat
4. Waits for the user to reply with the solution (2-min timeout)
5. Returns the solution to the caller

Uses an asyncio.Queue per session to relay solutions from the bot handler
back to the Playwright automation.
"""

import asyncio
import base64
import uuid
from dataclasses import dataclass, field
from typing import Optional

import httpx

from app.config import get_settings


@dataclass
class CaptchaChallenge:
    captcha_id: str
    chat_id: str
    image_base64: str
    captcha_type: str  # "image", "recaptcha_v2", "hcaptcha", "turnstile"
    solution_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    solved: bool = False
    solution: Optional[str] = None


# In-memory store of pending CAPTCHA challenges
_pending: dict[str, CaptchaChallenge] = {}
# Also index by chat_id for the bot handler to find
_pending_by_chat: dict[str, CaptchaChallenge] = {}


async def detect_captcha_type(page) -> Optional[str]:
    """Auto-detect what type of CAPTCHA is on the page."""
    checks = [
        ("iframe[src*='google.com/recaptcha']", "recaptcha_v2"),
        ("iframe[src*='hcaptcha.com']", "hcaptcha"),
        (".cf-turnstile", "turnstile"),
        ("img[src*='captcha']", "image"),
        ("img[alt*='captcha' i]", "image"),
        ("#captcha", "image"),
        (".captcha-image", "image"),
    ]
    for selector, captcha_type in checks:
        try:
            el = await page.query_selector(selector)
            if el:
                return captcha_type
        except Exception:
            continue
    return None


async def screenshot_captcha(page, captcha_type: str) -> bytes:
    """Take a screenshot of the CAPTCHA element."""
    selectors_by_type = {
        "recaptcha_v2": "iframe[src*='google.com/recaptcha']",
        "hcaptcha": "iframe[src*='hcaptcha.com']",
        "turnstile": ".cf-turnstile",
        "image": "img[src*='captcha'], img[alt*='captcha' i], #captcha, .captcha-image",
    }
    selector = selectors_by_type.get(captcha_type, "body")

    try:
        el = await page.query_selector(selector)
        if el:
            return await el.screenshot()
    except Exception:
        pass

    # Fallback: screenshot the whole page
    return await page.screenshot()


async def send_captcha_to_telegram(chat_id: str, image_bytes: bytes,
                                    captcha_type: str) -> str:
    """Send CAPTCHA screenshot to user's Telegram and return captcha_id."""
    settings = get_settings()
    captcha_id = str(uuid.uuid4())

    bot_token = settings.telegram_bot_token
    if not bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not configured — cannot forward CAPTCHA")

    messages = {
        "image": "Please type the text you see in this CAPTCHA image:",
        "recaptcha_v2": "Please solve this reCAPTCHA. Describe what you see or type the answer:",
        "hcaptcha": "Please solve this hCaptcha challenge:",
        "turnstile": "Please complete this Cloudflare verification:",
    }
    caption = messages.get(captcha_type, "Please solve this CAPTCHA:")
    caption += "\n\n(Reply to this message with your answer. You have 2 minutes.)"

    # Send photo via Telegram Bot API
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://api.telegram.org/bot{bot_token}/sendPhoto",
            data={"chat_id": chat_id, "caption": caption},
            files={"photo": ("captcha.png", image_bytes, "image/png")},
        )
        resp.raise_for_status()

    # Store the challenge
    challenge = CaptchaChallenge(
        captcha_id=captcha_id,
        chat_id=chat_id,
        image_base64=base64.b64encode(image_bytes).decode(),
        captcha_type=captcha_type,
    )
    _pending[captcha_id] = challenge
    _pending_by_chat[chat_id] = challenge

    return captcha_id


async def wait_for_solution(captcha_id: str, timeout: float = 120.0) -> Optional[str]:
    """Wait for the user to reply with the CAPTCHA solution."""
    challenge = _pending.get(captcha_id)
    if not challenge:
        return None

    try:
        solution = await asyncio.wait_for(
            challenge.solution_queue.get(),
            timeout=timeout,
        )
        challenge.solved = True
        challenge.solution = solution
        return solution
    except asyncio.TimeoutError:
        return None
    finally:
        # Cleanup
        _pending.pop(captcha_id, None)
        _pending_by_chat.pop(challenge.chat_id, None)


def submit_solution(chat_id: str, solution: str) -> bool:
    """Called by the bot handler when user replies with CAPTCHA answer."""
    challenge = _pending_by_chat.get(chat_id)
    if not challenge:
        return False

    challenge.solution_queue.put_nowait(solution)
    return True


def get_pending_for_chat(chat_id: str) -> Optional[CaptchaChallenge]:
    """Check if there's a pending CAPTCHA for this chat."""
    return _pending_by_chat.get(chat_id)


async def solve_captcha(page, chat_id: str) -> bool:
    """
    Full CAPTCHA solving pipeline:
    1. Detect type
    2. Screenshot
    3. Send to Telegram
    4. Wait for user solution
    5. Inject solution into page
    Returns True if solved, False if failed/timeout.
    """
    captcha_type = await detect_captcha_type(page)
    if not captcha_type:
        return True  # No CAPTCHA detected — proceed

    # Screenshot it
    image_bytes = await screenshot_captcha(page, captcha_type)

    # Send to Telegram
    captcha_id = await send_captcha_to_telegram(chat_id, image_bytes, captcha_type)

    # Wait for user's answer
    solution = await wait_for_solution(captcha_id, timeout=120.0)
    if not solution:
        return False  # Timeout

    # Inject the solution based on CAPTCHA type
    if captcha_type == "image":
        # Find the text input near the CAPTCHA image
        input_selectors = [
            "input[name*='captcha' i]",
            "input[id*='captcha' i]",
            "input[placeholder*='captcha' i]",
            "input[type='text']:near(img)",
        ]
        for sel in input_selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    await el.fill(solution)
                    return True
            except Exception:
                continue
        # Last resort: try typing into the focused element
        await page.keyboard.type(solution)
        return True

    elif captcha_type == "recaptcha_v2":
        # Inject the token into the hidden textarea
        await page.evaluate(f"""
            document.querySelector('#g-recaptcha-response').value = '{solution}';
            document.querySelector('#g-recaptcha-response').dispatchEvent(new Event('input'));
        """)
        return True

    elif captcha_type == "hcaptcha":
        await page.evaluate(f"""
            document.querySelector('[name="h-captcha-response"]').value = '{solution}';
        """)
        return True

    return False
