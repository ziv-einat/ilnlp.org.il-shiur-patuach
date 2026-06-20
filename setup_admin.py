"""Run once to create lessons_data.json and admin_config.json"""
import bcrypt, json, uuid, os

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Admin credentials ──
password_hash = bcrypt.hashpw(b"1234", bcrypt.gensalt(12)).decode("utf-8")
config = {
    "admins": [{"email": "ziv.einat@gmail.com", "password_hash": password_hash}],
    "max_attempts": 5,
    "lockout_minutes": 15,
}
with open(os.path.join(BASE, "admin_config.json"), "w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
print("admin_config.json created")

# ── Lessons data ──
lessons = [
    {"id": str(uuid.uuid4()), "num": 2,  "date_iso": "2026-07-08", "day": "רביעי",  "time_start": "18:00", "duration_minutes": 150, "topic": "איחוי חלקים",    "subtitle": "", "description": "", "status": "planned", "registration_link": "", "process": "איחוי חלקים בגירסה משודרגת",       "teacher": "טלי בן יעקב",          "org": "NLPSTEPS",                                      "zoom_link": "", "recording_link": "", "files_link": ""},
    {"id": str(uuid.uuid4()), "num": 3,  "date_iso": "2026-08-04", "day": "שלישי",  "time_start": "18:00", "duration_minutes": 150, "topic": "מטא-מודל",       "subtitle": "", "description": "", "status": "planned", "registration_link": "", "process": "תרגול שאלות מטא על פי סוג",           "teacher": "ג'וסלין סבג",           "org": "המרכז להתפתחות אישית",                         "zoom_link": "", "recording_link": "", "files_link": ""},
    {"id": str(uuid.uuid4()), "num": 4,  "date_iso": "2026-09-06", "day": "ראשון",  "time_start": "18:00", "duration_minutes": 150, "topic": "סוויש",           "subtitle": "", "description": "", "status": "planned", "registration_link": "", "process": "סוויש ויזואלי",                       "teacher": "תימורה שפירא",          "org": "תימורה – לבחור ולהגשים",                      "zoom_link": "", "recording_link": "", "files_link": ""},
    {"id": str(uuid.uuid4()), "num": 5,  "date_iso": "2026-10-11", "day": "ראשון",  "time_start": "18:00", "duration_minutes": 150, "topic": "מודל התקשורת",   "subtitle": "", "description": "", "status": "planned", "registration_link": "", "process": "מודל התקשורת",                         "teacher": "רויטל חזות",            "org": "המרכז להתפתחות אישית ומקצועית NLP",            "zoom_link": "", "recording_link": "", "files_link": ""},
    {"id": str(uuid.uuid4()), "num": 6,  "date_iso": "2026-11-01", "day": "ראשון",  "time_start": "18:00", "duration_minutes": 180, "topic": "מילטון מודל",    "subtitle": "", "description": "", "status": "planned", "registration_link": "", "process": "DTT בשפת מילטון",                       "teacher": "נרית רבינר",            "org": "מרכז MNLP",                                    "zoom_link": "", "recording_link": "", "files_link": ""},
    {"id": str(uuid.uuid4()), "num": 7,  "date_iso": "2026-12-17", "day": "חמישי",  "time_start": "10:00", "duration_minutes": 180, "topic": "אקולוגיה",        "subtitle": "", "description": "", "status": "planned", "registration_link": "", "process": "מודל הניצחון של דיסני",                 "teacher": "מור-מלכה בנצ'יק",      "org": "מכללת שלמים",                                  "zoom_link": "", "recording_link": "", "files_link": ""},
    {"id": str(uuid.uuid4()), "num": 8,  "date_iso": "2027-01-05", "day": "חמישי",  "time_start": "10:00", "duration_minutes": 150, "topic": "הנחות יסוד",     "subtitle": "", "description": "", "status": "planned", "registration_link": "", "process": "מעגל הנחות יסוד",                       "teacher": "שרית למפרט שושן",       "org": "קיבוץ משמרות / מכללת אורנים",                  "zoom_link": "", "recording_link": "", "files_link": ""},
    {"id": str(uuid.uuid4()), "num": 9,  "date_iso": "2027-02-03", "day": "רביעי",  "time_start": "10:00", "duration_minutes": 180, "topic": "רמות לוגיות",    "subtitle": "", "description": "", "status": "planned", "registration_link": "", "process": "רמות לוגיות לשינוי אמונה",              "teacher": "בוריס מלצר",            "org": "מכללה לחיים מוצלחים",                          "zoom_link": "", "recording_link": "", "files_link": ""},
    {"id": str(uuid.uuid4()), "num": 10, "date_iso": "2027-03-07", "day": "ראשון",  "time_start": "18:00", "duration_minutes": 150, "topic": "אמונות",          "subtitle": "", "description": "", "status": "planned", "registration_link": "", "process": "מוזאון האמונות העתיקות",                "teacher": "הדס וילף",              "org": "בית הספר ל-NLP של הדס וילף",                   "zoom_link": "", "recording_link": "", "files_link": ""},
    {"id": str(uuid.uuid4()), "num": 11, "date_iso": None,          "day": "",        "time_start": "",      "duration_minutes": 150, "topic": "Outcome",          "subtitle": "", "description": "", "status": "planned", "registration_link": "", "process": "Outcome",                                "teacher": "עידית ג'וס",            "org": "Joss NLP מ א ועד ת",                           "zoom_link": "", "recording_link": "", "files_link": ""},
    {"id": str(uuid.uuid4()), "num": 12, "date_iso": "2027-05-18", "day": "שלישי",  "time_start": "10:00", "duration_minutes": 150, "topic": "מרכיבי חושים",   "subtitle": "", "description": "", "status": "planned", "registration_link": "", "process": "תרגול עם קלפים",                        "teacher": "אלה גבאי ומירי יפרח",  "org": "NLP Creative School",                          "zoom_link": "", "recording_link": "", "files_link": ""},
    {"id": str(uuid.uuid4()), "num": 13, "date_iso": "2027-06-07", "day": "שני",    "time_start": "10:00", "duration_minutes": 150, "topic": "עוגנים",          "subtitle": "", "description": "", "status": "planned", "registration_link": "", "process": "מעגל המצויינות",                        "teacher": "עינת זיו",              "org": "NLPnow",                                       "zoom_link": "", "recording_link": "", "files_link": ""},
]

with open(os.path.join(BASE, "lessons_data.json"), "w", encoding="utf-8") as f:
    json.dump(lessons, f, ensure_ascii=False, indent=2)
print(f"lessons_data.json created with {len(lessons)} lessons")
print("Setup complete!")
