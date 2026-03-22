"""
Trilingual translations for CitaFacil bot — English, Chinese, Spanish.
Usage: t(key, lang) returns the string in the user's language.
"""

STRINGS = {
    # ── Language picker ──────────────────────────────────────────────
    "pick_lang": {
        "en": "🌐 Choose your language:",
        "zh": "🌐 请选择语言：",
        "es": "🌐 Elige tu idioma:",
    },
    "lang_set": {
        "en": "Language set to English.",
        "zh": "语言已设置为中文。",
        "es": "Idioma configurado a Español.",
    },

    # ── /start welcome ───────────────────────────────────────────────
    "welcome": {
        "en": (
            "🇲🇽 *CitaFacil — Government Appointment Booking*\n\n"
            "Skip the headache of booking Mexican government appointments. "
            "We handle the dozens of clicks and form-filling so you just press one button.\n\n"
            "*Services:*\n"
            "📋 *INM* — Immigration (residencia, cambio de condicion, regularizacion...)\n"
            "🛂 *SRE* — Passport & visa via MiConsulado\n\n"
            "*How it works:*\n"
            "1. Pick your language\n"
            "2. Choose your procedure\n"
            "3. We fill out the forms and book the appointment\n\n"
            "🔒 AES-256 encryption. We never store your MiConsulado password."
        ),
        "zh": (
            "🇲🇽 *CitaFacil — 墨西哥政府预约助手*\n\n"
            "不再为预约墨西哥政府服务而头疼。"
            "我们帮你完成所有繁琐的表格填写和点击，你只需按一个按钮。\n\n"
            "*服务项目：*\n"
            "📋 *INM* — 移民局（临时居留、永久居留、身份变更、合法化...）\n"
            "🛂 *SRE* — 护照与签证（通过 MiConsulado）\n\n"
            "*使用步骤：*\n"
            "1. 选择语言\n"
            "2. 选择办理事项\n"
            "3. 我们自动填表并预约\n\n"
            "🔒 AES-256 加密。我们绝不保存你的 MiConsulado 密码。"
        ),
        "es": (
            "🇲🇽 *CitaFacil — Reserva de Citas del Gobierno*\n\n"
            "Olvida el dolor de cabeza de agendar citas gubernamentales en Mexico. "
            "Nosotros hacemos los docenas de clics y llenamos los formularios, tu solo presionas un boton.\n\n"
            "*Servicios:*\n"
            "📋 *INM* — Migracion (residencia, cambio de condicion, regularizacion...)\n"
            "🛂 *SRE* — Pasaporte y visa por MiConsulado\n\n"
            "*Como funciona:*\n"
            "1. Elige tu idioma\n"
            "2. Selecciona tu tramite\n"
            "3. Llenamos los formularios y agendamos tu cita\n\n"
            "🔒 Cifrado AES-256. Nunca almacenamos tu contrasena de MiConsulado."
        ),
    },

    # ── /start buttons ───────────────────────────────────────────────
    "btn_inm": {
        "en": "📋 Book INM Appointment",
        "zh": "📋 预约 INM 移民局",
        "es": "📋 Agendar Cita INM",
    },
    "btn_sre": {
        "en": "🛂 Book SRE Appointment",
        "zh": "🛂 预约 SRE 护照/签证",
        "es": "🛂 Agendar Cita SRE",
    },
    "btn_profile": {
        "en": "👤 My Profile",
        "zh": "👤 我的资料",
        "es": "👤 Mi Perfil",
    },
    "btn_appointments": {
        "en": "📅 My Appointments",
        "zh": "📅 我的预约",
        "es": "📅 Mis Citas",
    },
    "btn_lang": {
        "en": "🌐 Language",
        "zh": "🌐 语言",
        "es": "🌐 Idioma",
    },
    "btn_website": {
        "en": "🌐 Open Website",
        "zh": "🌐 打开网站",
        "es": "🌐 Abrir Sitio Web",
    },

    # ── /help ─────────────────────────────────────────────────────────
    "help": {
        "en": (
            "*Commands:*\n"
            "/start — Main menu\n"
            "/inm — Book INM appointment\n"
            "/sre — Book SRE appointment\n"
            "/lang — Change language\n"
            "/help — Show this message\n\n"
            "Tap the menu button (☰) next to the message field to see all commands."
        ),
        "zh": (
            "*命令列表：*\n"
            "/start — 主菜单\n"
            "/inm — 预约 INM 移民局\n"
            "/sre — 预约 SRE 护照/签证\n"
            "/lang — 更改语言\n"
            "/help — 显示此帮助\n\n"
            "点击输入框旁的菜单按钮 (☰) 可查看所有命令。"
        ),
        "es": (
            "*Comandos:*\n"
            "/start — Menu principal\n"
            "/inm — Agendar cita INM\n"
            "/sre — Agendar cita SRE\n"
            "/lang — Cambiar idioma\n"
            "/help — Mostrar este mensaje\n\n"
            "Toca el boton de menu (☰) junto al campo de mensaje para ver todos los comandos."
        ),
    },

    # ── Profile (placeholder) ────────────────────────────────────────
    "profile": {
        "en": (
            "👤 *Your Profile*\n\n"
            "Your profile data auto-fills appointment forms.\n"
            "Fill it in once, reuse for every booking.\n\n"
            "🌐 Visit the website to complete your profile."
        ),
        "zh": (
            "👤 *你的资料*\n\n"
            "你的资料会自动填入预约表格。\n"
            "只需填写一次，之后每次预约自动使用。\n\n"
            "🌐 请访问网站完善你的资料。"
        ),
        "es": (
            "👤 *Tu Perfil*\n\n"
            "Tus datos se usan para llenar automaticamente los formularios.\n"
            "Llenarlos una vez, reutilizar en cada cita.\n\n"
            "🌐 Visita el sitio web para completar tu perfil."
        ),
    },

    # ── Appointments (placeholder) ───────────────────────────────────
    "appointments": {
        "en": "📅 *Your Appointments*\n\nNo appointments yet.\nUse /inm or /sre to book one!",
        "zh": "📅 *你的预约*\n\n暂无预约。\n使用 /inm 或 /sre 开始预约！",
        "es": "📅 *Tus Citas*\n\nAun no tienes citas.\nUsa /inm o /sre para agendar una!",
    },

    # ── INM flow ─────────────────────────────────────────────────────
    "inm_title": {
        "en": "📋 *INM Appointment Booking*\n\nSelect the type of procedure:",
        "zh": "📋 *INM 移民局预约*\n\n请选择办理事项：",
        "es": "📋 *Cita INM*\n\nSelecciona el tipo de tramite:",
    },
    "inm_select_office": {
        "en": "Select your preferred INM office:",
        "zh": "请选择 INM 办事处：",
        "es": "Selecciona tu oficina INM preferida:",
    },
    "inm_confirm": {
        "en": (
            "📋 *Confirm INM Appointment*\n\n"
            "*Procedure:* {procedure}\n"
            "*Office:* {office}\n\n"
            "We'll use your profile data to fill out the solicitud.\n"
            "Ready to book?"
        ),
        "zh": (
            "📋 *确认 INM 预约*\n\n"
            "*办理事项：* {procedure}\n"
            "*办事处：* {office}\n\n"
            "我们将使用你的资料填写申请表。\n"
            "确认预约？"
        ),
        "es": (
            "📋 *Confirmar Cita INM*\n\n"
            "*Tramite:* {procedure}\n"
            "*Oficina:* {office}\n\n"
            "Usaremos tus datos para llenar la solicitud.\n"
            "Listo para agendar?"
        ),
    },
    "inm_booking_progress": {
        "en": "⏳ *Booking in progress...*\n\nFilling out your solicitud and searching for available slots.\nThis may take 1-2 minutes.",
        "zh": "⏳ *正在预约...*\n\n正在填写申请表并搜索可用时间。\n可能需要 1-2 分钟。",
        "es": "⏳ *Agendando...*\n\nLlenando tu solicitud y buscando horarios disponibles.\nEsto puede tomar 1-2 minutos.",
    },
    "inm_booking_done": {
        "en": (
            "📋 *Booking submitted!*\n\n"
            "*Procedure:* {procedure}\n"
            "*Office:* {office}\n"
            "*Status:* Pending\n\n"
            "We'll notify you when the appointment is confirmed."
        ),
        "zh": (
            "📋 *预约已提交！*\n\n"
            "*办理事项：* {procedure}\n"
            "*办事处：* {office}\n"
            "*状态：* 待确认\n\n"
            "预约确认后我们会通知你。"
        ),
        "es": (
            "📋 *Cita enviada!*\n\n"
            "*Tramite:* {procedure}\n"
            "*Oficina:* {office}\n"
            "*Estado:* Pendiente\n\n"
            "Te notificaremos cuando la cita este confirmada."
        ),
    },

    # ── SRE flow ─────────────────────────────────────────────────────
    "sre_title": {
        "en": "🛂 *SRE / MiConsulado Appointment*\n\nSelect the service you need:",
        "zh": "🛂 *SRE / MiConsulado 预约*\n\n请选择服务项目：",
        "es": "🛂 *Cita SRE / MiConsulado*\n\nSelecciona el servicio que necesitas:",
    },
    "sre_enter_email": {
        "en": (
            "🔐 *MiConsulado Login*\n\n"
            "Enter your MiConsulado email address.\n\n"
            "_We do NOT store your credentials. They are used once and immediately discarded._"
        ),
        "zh": (
            "🔐 *MiConsulado 登录*\n\n"
            "请输入你的 MiConsulado 邮箱地址。\n\n"
            "_我们不会保存你的登录信息。仅使用一次后立即删除。_"
        ),
        "es": (
            "🔐 *Inicio de Sesion MiConsulado*\n\n"
            "Ingresa tu correo electronico de MiConsulado.\n\n"
            "_NO almacenamos tus credenciales. Se usan una vez y se eliminan inmediatamente._"
        ),
    },
    "sre_enter_password": {
        "en": "Now enter your MiConsulado password.\n\n🔒 _Used once, never stored. Delete this message after sending._",
        "zh": "请输入你的 MiConsulado 密码。\n\n🔒 _仅使用一次，绝不保存。发送后请删除此消息。_",
        "es": "Ahora ingresa tu contrasena de MiConsulado.\n\n🔒 _Se usa una vez, nunca se almacena. Borra este mensaje despues de enviar._",
    },
    "sre_credentials_received": {
        "en": "✅ Credentials received (not stored).\n\nSelect your preferred SRE office:",
        "zh": "✅ 已收到登录信息（不会保存）。\n\n请选择 SRE 办事处：",
        "es": "✅ Credenciales recibidas (no almacenadas).\n\nSelecciona tu oficina SRE preferida:",
    },
    "sre_confirm": {
        "en": (
            "🛂 *Confirm SRE Appointment*\n\n"
            "*Service:* {procedure}\n"
            "*Office:* {office}\n"
            "*MiConsulado:* {email}\n\n"
            "Ready to book?"
        ),
        "zh": (
            "🛂 *确认 SRE 预约*\n\n"
            "*服务项目：* {procedure}\n"
            "*办事处：* {office}\n"
            "*MiConsulado：* {email}\n\n"
            "确认预约？"
        ),
        "es": (
            "🛂 *Confirmar Cita SRE*\n\n"
            "*Servicio:* {procedure}\n"
            "*Oficina:* {office}\n"
            "*MiConsulado:* {email}\n\n"
            "Listo para agendar?"
        ),
    },
    "sre_booking_progress": {
        "en": "⏳ *Booking in progress...*\n\nLogging into MiConsulado and searching for available slots.\nThis may take 1-2 minutes.",
        "zh": "⏳ *正在预约...*\n\n正在登录 MiConsulado 并搜索可用时间。\n可能需要 1-2 分钟。",
        "es": "⏳ *Agendando...*\n\nIniciando sesion en MiConsulado y buscando horarios.\nEsto puede tomar 1-2 minutos.",
    },
    "sre_booking_done": {
        "en": (
            "🛂 *Booking submitted!*\n\n"
            "*Service:* {procedure}\n"
            "*Office:* {office}\n"
            "*Status:* Pending\n\n"
            "We'll notify you when the appointment is confirmed."
        ),
        "zh": (
            "🛂 *预约已提交！*\n\n"
            "*服务项目：* {procedure}\n"
            "*办事处：* {office}\n"
            "*状态：* 待确认\n\n"
            "预约确认后我们会通知你。"
        ),
        "es": (
            "🛂 *Cita enviada!*\n\n"
            "*Servicio:* {procedure}\n"
            "*Oficina:* {office}\n"
            "*Estado:* Pendiente\n\n"
            "Te notificaremos cuando la cita este confirmada."
        ),
    },

    # ── Common buttons ───────────────────────────────────────────────
    "btn_book_now": {
        "en": "✅ Book Now",
        "zh": "✅ 立即预约",
        "es": "✅ Agendar Ahora",
    },
    "btn_cancel": {
        "en": "❌ Cancel",
        "zh": "❌ 取消",
        "es": "❌ Cancelar",
    },
    "cancelled": {
        "en": "Booking cancelled. Use /start for the menu.",
        "zh": "预约已取消。使用 /start 返回菜单。",
        "es": "Cita cancelada. Usa /start para volver al menu.",
    },
}

# ── Procedure / Office names (trilingual) ─────────────────────────────

INM_PROCEDURES = {
    "residencia_temporal": {
        "en": "Temporary Residency",
        "zh": "临时居留",
        "es": "Residencia Temporal",
    },
    "residencia_permanente": {
        "en": "Permanent Residency",
        "zh": "永久居留",
        "es": "Residencia Permanente",
    },
    "cambio_condicion": {
        "en": "Change of Status",
        "zh": "身份变更",
        "es": "Cambio de Condicion",
    },
    "renovacion_residencia": {
        "en": "Residency Renewal",
        "zh": "居留续签",
        "es": "Renovacion de Residencia",
    },
    "permiso_salida_regreso": {
        "en": "Exit & Re-entry Permit",
        "zh": "出入境许可",
        "es": "Permiso de Salida y Regreso",
    },
    "regularizacion": {
        "en": "Immigration Regularization",
        "zh": "移民合法化",
        "es": "Regularizacion Migratoria",
    },
}

INM_OFFICES = {
    "cdmx_polanco": {"en": "CDMX — Polanco", "zh": "墨城 Polanco", "es": "CDMX — Polanco"},
    "cdmx_centro": {"en": "CDMX — Centro", "zh": "墨城 Centro", "es": "CDMX — Centro"},
    "guadalajara": {"en": "Guadalajara", "zh": "瓜达拉哈拉", "es": "Guadalajara"},
    "monterrey": {"en": "Monterrey", "zh": "蒙特雷", "es": "Monterrey"},
    "cancun": {"en": "Cancun", "zh": "坎昆", "es": "Cancun"},
    "merida": {"en": "Merida", "zh": "梅里达", "es": "Merida"},
    "puebla": {"en": "Puebla", "zh": "普埃布拉", "es": "Puebla"},
    "tijuana": {"en": "Tijuana", "zh": "蒂华纳", "es": "Tijuana"},
    "queretaro": {"en": "Queretaro", "zh": "克雷塔罗", "es": "Queretaro"},
    "playa_del_carmen": {"en": "Playa del Carmen", "zh": "卡门海滩", "es": "Playa del Carmen"},
    "san_miguel_allende": {"en": "San Miguel de Allende", "zh": "圣米格尔德阿连德", "es": "San Miguel de Allende"},
    "puerto_vallarta": {"en": "Puerto Vallarta", "zh": "巴亚尔塔港", "es": "Puerto Vallarta"},
}

SRE_PROCEDURES = {
    "pasaporte_primera_vez": {
        "en": "Passport — First Time",
        "zh": "护照 — 首次申请",
        "es": "Pasaporte — Primera Vez",
    },
    "pasaporte_renovacion": {
        "en": "Passport — Renewal",
        "zh": "护照 — 续签",
        "es": "Pasaporte — Renovacion",
    },
    "visa_canje": {
        "en": "Visa Exchange",
        "zh": "签证更换",
        "es": "Canje de Visa",
    },
    "carta_naturalizacion": {
        "en": "Naturalization Letter",
        "zh": "入籍证明",
        "es": "Carta de Naturalizacion",
    },
    "apostilla": {
        "en": "Apostille",
        "zh": "海牙认证",
        "es": "Apostilla",
    },
    "legalizacion": {
        "en": "Document Legalization",
        "zh": "文件公证",
        "es": "Legalizacion de Documentos",
    },
}

SRE_OFFICES = {
    "cdmx_tlatelolco": {"en": "CDMX — Tlatelolco", "zh": "墨城 Tlatelolco", "es": "CDMX — Tlatelolco"},
    "cdmx_polanco": {"en": "CDMX — Polanco", "zh": "墨城 Polanco", "es": "CDMX — Polanco"},
    "guadalajara": {"en": "Guadalajara", "zh": "瓜达拉哈拉", "es": "Guadalajara"},
    "monterrey": {"en": "Monterrey", "zh": "蒙特雷", "es": "Monterrey"},
    "puebla": {"en": "Puebla", "zh": "普埃布拉", "es": "Puebla"},
    "cancun": {"en": "Cancun", "zh": "坎昆", "es": "Cancun"},
    "merida": {"en": "Merida", "zh": "梅里达", "es": "Merida"},
    "tijuana": {"en": "Tijuana", "zh": "蒂华纳", "es": "Tijuana"},
    "queretaro": {"en": "Queretaro", "zh": "克雷塔罗", "es": "Queretaro"},
}


def get_lang(context) -> str:
    """Get user's language from context, default to Spanish."""
    return context.user_data.get("lang", "es")


def t(key: str, lang: str = "es") -> str:
    """Get translated string."""
    entry = STRINGS.get(key, {})
    return entry.get(lang, entry.get("es", f"[{key}]"))


def proc_name(collection: dict, key: str, lang: str = "es") -> str:
    """Get localized procedure/office name."""
    entry = collection.get(key, {})
    if isinstance(entry, dict):
        return entry.get(lang, entry.get("es", key))
    return entry  # fallback for plain strings
