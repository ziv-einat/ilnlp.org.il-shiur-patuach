"""Shared utilities — lessons, admins, backup, log, validation, export."""
import json, os, uuid, csv, io, re, secrets
from datetime import datetime, timedelta
from urllib.parse import quote

BASE          = os.path.dirname(os.path.abspath(__file__))
DATA_FILE     = os.path.join(BASE, "lessons_data.json")
CONFIG_FILE   = os.path.join(BASE, "admin_config.json")
SETTINGS_FILE = os.path.join(BASE, "settings.json")
LOG_FILE      = os.path.join(BASE, "activity_log.json")
BACKUP_DIR    = os.path.join(BASE, "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

SETTINGS_KEYS = ["subscription_enabled", "display_from_lesson", "display_to_lesson"]

def _load_settings_file():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_settings_file(config):
    try:
        settings = {k: config.get(k) for k in SETTINGS_KEYS}
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

HEBREW_MONTHS = {1:"ינואר",2:"פברואר",3:"מרץ",4:"אפריל",5:"מאי",6:"יוני",
                 7:"יולי",8:"אוגוסט",9:"ספטמבר",10:"אוקטובר",11:"נובמבר",12:"דצמבר"}
HEBREW_DAYS   = {0:"שני",1:"שלישי",2:"רביעי",3:"חמישי",4:"שישי",5:"שבת",6:"ראשון"}

STATUS_OPTIONS = {
    "planned":   "בקרוב",
    "open":      "ההרשמה פתוחה",
    "postponed": "נדחה",
    "cancelled": "בוטל",
    "completed": "התקיים",
}
STATUS_COLORS = {
    "planned":   "#6b42b8",
    "open":      "#1a7f37",
    "postponed": "#e09d0a",
    "cancelled": "#cf222e",
    "completed": "#666",
}

VISIBILITY_OPTIONS = {
    "published": "פורסם",
    "draft":     "טיוטה",
    "hidden":    "מוסתר",
}
VISIBILITY_COLORS = {
    "published": "#1a7f37",
    "draft":     "#e09d0a",
    "hidden":    "#cf222e",
}

# ─────────────────────────────────────────
# LESSONS
# ─────────────────────────────────────────
def load_lessons():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return sorted(data, key=lambda l: (l.get("date_iso") or "9999-99-99", l.get("time_start") or ""))
    except Exception:
        return []

def save_lessons(lessons, actor_email="", actor_name=""):
    auto_backup()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(lessons, f, ensure_ascii=False, indent=2)

def renumber_lessons_by_date(start=2):
    """Renumber all lessons chronologically (lessons with dates first, undated last)."""
    auto_backup()
    lessons = load_lessons()
    dated   = sorted([l for l in lessons if l.get("date_iso")], key=lambda l: l["date_iso"])
    undated = [l for l in lessons if not l.get("date_iso")]
    for i, l in enumerate(dated + undated):
        l["num"] = start + i
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dated + undated, f, ensure_ascii=False, indent=2)

def validate_lesson(l):
    errors = []
    if not (l.get("topic") or "").strip():
        errors.append("נושא השיעור הוא שדה חובה")
    if not (l.get("teacher") or "").strip():
        errors.append("שם המרצה הוא שדה חובה")
    if l.get("date_iso"):
        try:
            datetime.strptime(l["date_iso"], "%Y-%m-%d")
        except ValueError:
            errors.append("תאריך לא תקין")
    if l.get("time_start"):
        if not re.match(r"^\d{2}:\d{2}$", l["time_start"]):
            errors.append("שעת התחלה לא תקינה — פורמט HH:MM")
        else:
            h, m = map(int, l["time_start"].split(":"))
            if not (0 <= h <= 23 and 0 <= m <= 59):
                errors.append("שעת התחלה לא תקינה")
    dur = l.get("duration_minutes")
    if dur is not None:
        try:
            d = int(dur)
            if not (30 <= d <= 480):
                errors.append("משך השיעור חייב להיות בין 30 ל-480 דקות")
        except (ValueError, TypeError):
            errors.append("משך השיעור לא תקין")
    url_pattern = re.compile(r"^https?://", re.IGNORECASE)
    for field, label in [("zoom_link","קישור Zoom"),("registration_link","קישור הרשמה"),
                         ("recording_link","קישור הקלטה"),("files_link","קישור חומרים")]:
        url = l.get(field, "")
        if url and not url_pattern.match(url):
            errors.append(f"{label} לא תקין — חייב להתחיל ב-https://")
    return errors

# ─────────────────────────────────────────
# BACKUP
# ─────────────────────────────────────────
def auto_backup():
    try:
        if not os.path.exists(DATA_FILE):
            return None
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(BACKUP_DIR, f"lessons_{ts}.json")
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = f.read()
        with open(dest, "w", encoding="utf-8") as f:
            f.write(data)
        # Keep latest 30 backups
        all_backups = sorted(f for f in os.listdir(BACKUP_DIR) if f.endswith(".json"))
        for old in all_backups[:-30]:
            try:
                os.remove(os.path.join(BACKUP_DIR, old))
            except Exception:
                pass
        return dest
    except Exception:
        return None

def list_backups():
    try:
        files = sorted(
            [f for f in os.listdir(BACKUP_DIR) if f.endswith(".json")],
            reverse=True
        )
        result = []
        for f in files:
            path = os.path.join(BACKUP_DIR, f)
            ts_str = f.replace("lessons_","").replace(".json","")
            try:
                ts = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
                label = ts.strftime("%d/%m/%Y %H:%M:%S")
            except Exception:
                label = f
            try:
                with open(path, "r", encoding="utf-8") as fp:
                    count = len(json.load(fp))
            except Exception:
                count = 0
            result.append({"filename": f, "path": path, "label": label, "count": count})
        return result
    except Exception:
        return []

def restore_backup(filename):
    path = os.path.join(BACKUP_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return len(data)

# ─────────────────────────────────────────
# EXPORT / IMPORT
# ─────────────────────────────────────────
def export_json():
    lessons = load_lessons()
    return json.dumps(lessons, ensure_ascii=False, indent=2).encode("utf-8")

def export_csv():
    lessons = load_lessons()
    output  = io.StringIO()
    fields  = ["num","status","topic","subtitle","teacher","org","date_iso","day",
               "time_start","duration_minutes","description","process",
               "zoom_link","registration_link","recording_link","files_link"]
    writer  = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(lessons)
    return output.getvalue().encode("utf-8-sig")

def import_json(content_bytes):
    data = json.loads(content_bytes.decode("utf-8"))
    if not isinstance(data, list):
        raise ValueError("הקובץ אינו רשימת שיעורים תקינה")
    for l in data:
        if "id" not in l:
            l["id"] = str(uuid.uuid4())
    return data

# ─────────────────────────────────────────
# ACTIVITY LOG
# ─────────────────────────────────────────
def log_action(actor_email, actor_name, action, details=""):
    try:
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                log = json.load(f)
        except Exception:
            log = []
        log.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "admin_email": actor_email,
            "admin_name": actor_name or actor_email,
            "action": action,
            "details": details,
        })
        log = log[-2000:]
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_log():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return list(reversed(json.load(f)))
    except Exception:
        return []

# ─────────────────────────────────────────
# ADMINS
# ─────────────────────────────────────────
def _migrate_config(config):
    """Migrate old config format to new format with full admin profiles."""
    changed = False
    for a in config.get("admins", []):
        if "id" not in a:
            a["id"] = str(uuid.uuid4()); changed = True
        if "full_name" not in a:
            a["full_name"] = "מנהל ראשי"; changed = True
        if "is_super_admin" not in a:
            a["is_super_admin"] = True; changed = True
        if "created_at" not in a:
            a["created_at"] = datetime.now().isoformat(); changed = True
        for k in ["reset_token", "reset_expires"]:
            if k not in a:
                a[k] = None; changed = True
        if "role" not in a:
            a["role"] = "admin"; changed = True
    if "subscription_enabled" not in config:
        config["subscription_enabled"] = False; changed = True
    if "display_from_lesson" not in config:
        config["display_from_lesson"] = None; changed = True
    if "display_to_lesson" not in config:
        config["display_to_lesson"] = None; changed = True
    return config, changed

def load_config():
    # Cloud deployment: read from Streamlit Secrets if available
    try:
        import streamlit as st
        secret_cfg = st.secrets.get("admin_config")
        if secret_cfg:
            config = json.loads(secret_cfg)
            config, _ = _migrate_config(config)
            config.update(_load_settings_file())
            return config
    except Exception:
        pass
    # Local: read from file
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception:
        config = {"admins": [], "max_attempts": 5, "lockout_minutes": 15}
    config, changed = _migrate_config(config)
    config.update(_load_settings_file())
    if changed:
        save_config(config)
    return config

def save_config(config):
    _save_settings_file(config)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def get_all_admins():
    return load_config().get("admins", [])

def get_admin_by_email(email):
    return next((a for a in get_all_admins() if a["email"] == email), None)

def get_admin_by_id(aid):
    return next((a for a in get_all_admins() if a["id"] == aid), None)

def upsert_admin(admin_dict):
    config = load_config()
    admins = config.get("admins", [])
    idx = next((i for i, a in enumerate(admins) if a["id"] == admin_dict["id"]), None)
    if idx is not None:
        admins[idx] = admin_dict
    else:
        admins.append(admin_dict)
    config["admins"] = admins
    save_config(config)

def delete_admin_by_id(aid):
    config = load_config()
    config["admins"] = [a for a in config.get("admins", []) if a["id"] != aid]
    save_config(config)

def set_reset_token(email):
    """Generate a password reset token valid for 1 hour. Returns token or None."""
    config = load_config()
    admin = next((a for a in config["admins"] if a["email"] == email), None)
    if not admin:
        return None
    token = secrets.token_urlsafe(32)
    admin["reset_token"] = token
    admin["reset_expires"] = (datetime.now() + timedelta(hours=1)).isoformat()
    save_config(config)
    return token

def verify_reset_token(token):
    """Return admin dict if token is valid and not expired, else None."""
    for admin in get_all_admins():
        if admin.get("reset_token") == token:
            expires = admin.get("reset_expires")
            if expires and datetime.fromisoformat(expires) > datetime.now():
                return admin
    return None

def clear_reset_token(email):
    config = load_config()
    for a in config["admins"]:
        if a["email"] == email:
            a["reset_token"] = None
            a["reset_expires"] = None
    save_config(config)

# ─────────────────────────────────────────
# CALENDAR HELPERS
# ─────────────────────────────────────────
def month_from_iso(date_iso):
    try:
        return HEBREW_MONTHS[datetime.strptime(date_iso, "%Y-%m-%d").month]
    except Exception:
        return ""

def day_from_iso(date_iso):
    try:
        return HEBREW_DAYS[datetime.strptime(date_iso, "%Y-%m-%d").weekday()]
    except Exception:
        return ""

def date_display(date_iso):
    try:
        d = datetime.strptime(date_iso, "%Y-%m-%d")
        return f"{d.day}.{d.month}.{str(d.year)[2:]}"
    except Exception:
        return ""

def time_end(time_start, duration_min):
    try:
        dt = datetime.strptime(time_start, "%H:%M") + timedelta(minutes=int(duration_min))
        return dt.strftime("%H:%M")
    except Exception:
        return ""

def time_range(time_start, duration_min):
    end = time_end(time_start, duration_min)
    return f"{time_start}–{end}" if end else time_start

def cal_title(l):
    topic   = (l.get('topic') or '').strip()
    teacher = (l.get('teacher') or '').strip()
    base = f"לשכת ה־NLP הישראלית, שיעור פתוח, {topic}"
    return f"{base}, {teacher}" if teacher else base

def cal_desc(l):
    parts = [f"מרצה: {l['teacher']}"]
    if l.get("org"): parts[0] += f" | {l['org']}"
    if l.get("process"): parts.append(f"תהליך: {l['process']}")
    if l.get("zoom_link"): parts.append(f"קישור: {l['zoom_link']}")
    return "\n".join(parts)

def _cal_start(l):
    if not l.get("date_iso") or not l.get("time_start"): return None
    d = l["date_iso"].replace("-",""); t = l["time_start"].replace(":","") + "00"
    return f"{d}T{t}"

def _cal_end(l):
    if not l.get("date_iso") or not l.get("time_start"): return None
    dt = datetime.strptime(f"{l['date_iso']} {l['time_start']}", "%Y-%m-%d %H:%M")
    return (dt + timedelta(minutes=int(l.get("duration_minutes",120)))).strftime("%Y%m%dT%H%M00")

def google_url(l):
    s, e = _cal_start(l), _cal_end(l)
    if not s: return None
    p = quote
    return (f"https://calendar.google.com/calendar/render?action=TEMPLATE"
            f"&text={p(cal_title(l))}&dates={s}/{e}&details={p(cal_desc(l))}")

def outlook_url(l):
    if not l.get("date_iso") or not l.get("time_start"): return None
    dt  = datetime.strptime(f"{l['date_iso']} {l['time_start']}", "%Y-%m-%d %H:%M")
    dte = dt + timedelta(minutes=int(l.get("duration_minutes",120)))
    p   = quote
    return (f"https://outlook.live.com/calendar/0/action/compose"
            f"?subject={p(cal_title(l))}&startdt={dt.strftime('%Y-%m-%dT%H:%M:00')}"
            f"&enddt={dte.strftime('%Y-%m-%dT%H:%M:00')}&body={p(cal_desc(l))}&allday=false")

def generate_ics(l):
    s, e = _cal_start(l), _cal_end(l)
    if not s: return None
    now  = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    desc = cal_desc(l).replace("\n","\\n")
    lines = ["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//שיעור פתוח NLP//IL",
             "CALSCALE:GREGORIAN","METHOD:PUBLISH","BEGIN:VEVENT",
             f"UID:nlp-{l['id']}@shiur-patuach.il", f"DTSTAMP:{now}",
             f"DTSTART;TZID=Asia/Jerusalem:{s}", f"DTEND;TZID=Asia/Jerusalem:{e}",
             f"SUMMARY:{cal_title(l)}", f"DESCRIPTION:{desc}",
             "END:VEVENT","END:VCALENDAR"]
    return "\r\n".join(lines).encode("utf-8")

# ─────────────────────────────────────────
# SUBSCRIBERS
# ─────────────────────────────────────────
SUBSCRIBERS_FILE = os.path.join(BASE, "subscribers.json")
NOTIFY_FIELDS    = {"date_iso","time_start","duration_minutes","teacher","topic","subtitle",
                    "zoom_link","registration_link"}

def load_subscribers():
    try:
        with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_subscribers(subs):
    with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
        json.dump(subs, f, ensure_ascii=False, indent=2)

def add_subscriber(lesson_id, lesson_num, email, first_name="", last_name=""):
    """Add subscriber. Returns True if new, False if already subscribed."""
    subs  = load_subscribers()
    email = email.lower().strip()
    if any(s["lesson_id"]==lesson_id and s["email"]==email and s.get("active",True) for s in subs):
        return False
    subs.append({
        "id":            str(uuid.uuid4()),
        "lesson_id":     lesson_id,
        "lesson_num":    lesson_num,
        "email":         email,
        "first_name":    first_name,
        "last_name":     last_name,
        "subscribed_at": datetime.now().isoformat(),
        "consent":       True,
        "active":        True,
    })
    _save_subscribers(subs)
    return True

def get_subscribers_for_lesson(lesson_id):
    return [s for s in load_subscribers()
            if s["lesson_id"]==lesson_id and s.get("active",True) and s.get("consent",True)]

def count_subscribers(lesson_id):
    return len(get_subscribers_for_lesson(lesson_id))

def total_subscribers():
    return len([s for s in load_subscribers() if s.get("active", True) and s.get("consent", True)])

def export_subscribers_csv_for_lesson(lesson_id, lesson_num=""):
    subs   = get_subscribers_for_lesson(lesson_id)
    output = io.StringIO()
    writer = csv.DictWriter(output,
                            fieldnames=["first_name","last_name","email","subscribed_at","lesson_num","lesson_id"],
                            extrasaction="ignore")
    writer.writeheader()
    writer.writerows(subs)
    return output.getvalue().encode("utf-8-sig")

def export_all_subscribers_csv():
    subs   = load_subscribers()
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["first_name","last_name","email","lesson_num","subscribed_at","lesson_id","consent","active"],
        extrasaction="ignore",
    )
    writer.writeheader()
    writer.writerows(subs)
    return output.getvalue().encode("utf-8-sig")

def lesson_changed_fields(old, new):
    """Return list of NOTIFY_FIELDS that differ between old and new lesson dicts."""
    return [f for f in NOTIFY_FIELDS if str(old.get(f) or "") != str(new.get(f) or "")]

NOTIFY_FIELD_LABELS = {
    "date_iso":         "תאריך",
    "time_start":       "שעה",
    "duration_minutes": "משך",
    "teacher":          "מרצה",
    "topic":            "נושא",
    "subtitle":         "כותרת משנה",
    "zoom_link":        "קישור זום",
    "registration_link":"קישור הרשמה",
}

PUBLIC_URL = "https://shiur-patuach-ilnlp.streamlit.app"

def generate_whatsapp_text(l):
    topic    = l.get('topic', '')
    teacher  = l.get('teacher', '')
    org      = l.get('org', '')
    date_s   = date_display(l.get('date_iso', '')) or ''
    day_s    = l.get('day', '')
    t_rng    = time_range(l.get('time_start', ''), l.get('duration_minutes', 120)) if l.get('time_start') else ''
    reg_link = (l.get('registration_link') or '').strip()
    desc     = (l.get('description') or '').strip()

    lines = ["*שיעור פתוח - לשכת ה NLP הישראלית*", ""]
    lines.append(f"*{topic}*")
    if l.get('subtitle', '').strip():
        lines.append(l['subtitle'])
    lines.append("")
    teacher_line = f"- מרצה: {teacher}"
    if org:
        teacher_line += f" | {org}"
    lines.append(teacher_line)
    if date_s:
        date_line = f"- תאריך: {date_s}"
        if day_s:  date_line += f" {day_s}"
        if t_rng:  date_line += f" | {t_rng}"
        lines.append(date_line)
    if l.get('process', '').strip():
        lines.append(f"- תהליך: {l['process']}")
    if desc:
        lines += ["", desc]
    if reg_link:
        lines += ["", f"להרשמה: {reg_link}"]
    lines += ["", f"לוח השיעורים: {PUBLIC_URL}", "", "מוזמנים להצטרף!"]
    return "\n".join(lines)

def generate_general_email(lesson, to_whom="lesson"):
    """Generate announcement/info email for a lesson (not an update notification)."""
    title = lesson["topic"]
    if lesson.get("subtitle", "").strip():
        title = f"{title} – {lesson['subtitle']}"
    d    = date_display(lesson.get("date_iso") or "") or "יעודכן"
    day  = lesson.get("day", "")
    t    = (time_range(lesson.get("time_start", ""), lesson.get("duration_minutes", 120))
            if lesson.get("time_start") else "יעודכן")
    teacher = lesson.get("teacher", "")
    org     = lesson.get("org", "")
    zoom    = lesson.get("zoom_link", "") or "יעודכן"
    reg     = lesson.get("registration_link", "")
    desc    = (lesson.get("description") or "").strip()

    subject = f'הזמנה לשיעור פתוח: "{title}"'
    body_parts = [
        "שלום,",
        "",
        f'אנו שמחים להזמינך לשיעור פתוח בנושא "{title}".',
        "",
        f"מרצה: {teacher}" + (f" | {org}" if org else ""),
        f"תאריך: {d} {day}",
        f"שעה: {t}",
    ]
    if desc:
        body_parts += ["", desc]
    if reg:
        body_parts += ["", f"להרשמה: {reg}"]
    else:
        body_parts += ["", f"קישור לשיעור: {zoom}"]
    body_parts += [
        "",
        f"לוח השיעורים המלא: {PUBLIC_URL}",
        "",
        "נשמח לראותך,",
        "ועדת בתי הספר – פרויקט ״שיעור פתוח״",
        "",
        "---",
        "להסרה מרשימת תפוצה זו, השב/י למייל זה עם הנושא: הסרה",
    ]
    return subject, "\n".join(body_parts)

def generate_update_email(lesson, schedule_url="https://shiur-patuach-ilnlp.streamlit.app"):
    title = lesson["topic"]
    if lesson.get("subtitle","").strip():
        title = f"{title} – {lesson['subtitle']}"
    d    = date_display(lesson.get("date_iso") or "") or "יעודכן"
    day  = lesson.get("day","")
    t    = (time_range(lesson.get("time_start",""), lesson.get("duration_minutes",120))
            if lesson.get("time_start") else "יעודכן")
    zoom = lesson.get("zoom_link","") or "יעודכן"
    subject = f'עדכון לגבי שיעור פתוח: "{title}"'
    body    = (
        "שלום,\n\n"
        "חל שינוי בפרטי השיעור שאליו נרשמת.\n\n"
        "הפרטים המעודכנים:\n"
        f"תאריך: {d} {day}\n"
        f"שעה: {t}\n"
        f"מרצה: {lesson['teacher']}\n"
        f"נושא: {title}\n"
        f"קישור לשיעור: {zoom}\n\n"
        f"לוח השיעורים המעודכן:\n{schedule_url}\n\n"
        "נשמח לראותך,\n"
        "ועדת בתי הספר – פרויקט ״שיעור פתוח״\n\n"
        "---\n"
        "להסרה מרשימת תפוצה זו, השב/י למייל זה עם הנושא: הסרה"
    )
    return subject, body
