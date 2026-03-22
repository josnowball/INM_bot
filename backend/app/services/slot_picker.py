"""
Calendar slot detection and selection for government appointment sites.
Parses rendered calendar pages to find available date/time slots.
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class TimeSlot:
    date: str       # YYYY-MM-DD
    time: str       # HH:MM
    availability: str  # "high", "medium", "low"


async def parse_sre_calendar(page) -> list[TimeSlot]:
    """
    Parse the SRE appointment calendar page.
    The calendar typically shows a month view with color-coded dates:
    - Green cells = many slots available
    - Yellow/Orange = some slots
    - Red/Gray = no slots or fully booked

    After clicking a date, time slots appear as a list or grid.
    """
    slots = []

    # Wait for calendar to render
    try:
        await page.wait_for_selector(
            ".calendar, .datepicker, [class*='calendar'], table.month, #calendar",
            timeout=10000,
        )
    except Exception:
        # Try broader selectors
        try:
            await page.wait_for_selector("td[class], .day, .date-cell", timeout=5000)
        except Exception:
            return slots

    # Find all clickable date cells that indicate availability
    available_selectors = [
        "td.available",
        "td.active",
        "td[class*='available']",
        "td[class*='green']",
        "td[class*='yellow']",
        "td[class*='open']",
        ".day.available",
        ".day.active:not(.disabled)",
        "td:not(.disabled):not(.past):not(.unavailable) a",
        "td:not(.disabled):not(.past):not(.unavailable) button",
    ]

    date_elements = []
    for sel in available_selectors:
        try:
            elements = await page.query_selector_all(sel)
            if elements:
                date_elements = elements
                break
        except Exception:
            continue

    # Extract date info from each available cell
    for el in date_elements[:20]:  # Cap at 20 dates
        try:
            text = await el.text_content()
            text = text.strip() if text else ""

            # Try to get date from data attributes
            date_str = (
                await el.get_attribute("data-date")
                or await el.get_attribute("data-day")
                or await el.get_attribute("data-value")
                or ""
            )

            # Classify availability by CSS class
            class_attr = await el.get_attribute("class") or ""
            if any(c in class_attr.lower() for c in ["green", "high", "many"]):
                avail = "high"
            elif any(c in class_attr.lower() for c in ["yellow", "medium", "some"]):
                avail = "medium"
            else:
                avail = "low"

            if date_str:
                slots.append(TimeSlot(date=date_str, time="", availability=avail))
            elif text and text.isdigit():
                # Just a day number — we'll need the month/year context
                slots.append(TimeSlot(date=text, time="", availability=avail))

        except Exception:
            continue

    return slots


async def get_time_slots_for_date(page, date_element) -> list[TimeSlot]:
    """
    After clicking a date on the calendar, parse the available time slots.
    """
    # Click the date
    try:
        await date_element.click()
        await page.wait_for_timeout(2000)  # Wait for time slots to load
    except Exception:
        return []

    time_slots = []
    time_selectors = [
        ".time-slot",
        ".hora",
        "[class*='time']",
        "[class*='hora']",
        "input[type='radio'][name*='time']",
        "input[type='radio'][name*='hora']",
        "button[class*='time']",
        "li.available-time",
    ]

    for sel in time_selectors:
        try:
            elements = await page.query_selector_all(sel)
            if elements:
                for el in elements:
                    text = await el.text_content()
                    text = text.strip() if text else ""
                    # Extract time pattern HH:MM
                    time_match = re.search(r'(\d{1,2}:\d{2})', text)
                    if time_match:
                        time_slots.append(TimeSlot(
                            date="",  # Caller knows the date
                            time=time_match.group(1),
                            availability="high",
                        ))
                break
        except Exception:
            continue

    return time_slots


async def select_slot(page, target_date: str, target_time: str) -> bool:
    """
    Click a specific date and time on the calendar.
    Used when the user selects a slot from the bot's inline keyboard.
    """
    # Find and click the date
    date_selectors = [
        f"td[data-date='{target_date}']",
        f"td[data-day='{target_date}']",
        f"[data-value='{target_date}']",
    ]

    date_clicked = False
    for sel in date_selectors:
        try:
            el = await page.query_selector(sel)
            if el:
                await el.click()
                await page.wait_for_timeout(2000)
                date_clicked = True
                break
        except Exception:
            continue

    if not date_clicked:
        # Try clicking by text content (day number)
        day_num = target_date.split("-")[-1].lstrip("0") if "-" in target_date else target_date
        try:
            await page.click(f"td:has-text('{day_num}')")
            await page.wait_for_timeout(2000)
            date_clicked = True
        except Exception:
            return False

    # Now find and click the time
    if target_time:
        time_selectors = [
            f"[data-time='{target_time}']",
            f"[data-hora='{target_time}']",
            f"button:has-text('{target_time}')",
            f"label:has-text('{target_time}')",
        ]
        for sel in time_selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    await el.click()
                    await page.wait_for_timeout(1000)
                    return True
            except Exception:
                continue

        # Try radio button with time value
        try:
            await page.click(f"input[value*='{target_time}']")
            return True
        except Exception:
            pass

    return date_clicked


async def parse_inm_calendar(page) -> list[TimeSlot]:
    """Parse INM appointment calendar. Similar structure to SRE."""
    # INM uses a similar calendar component
    return await parse_sre_calendar(page)
