import streamlit as st

st.set_page_config(
    page_title="שיעורים פתוחים – לוח שנה מלא",
    page_icon="📚",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700&display=swap');

* { font-family: 'Heebo', sans-serif !important; }

html, body, [class*="css"] {
    direction: rtl;
    background-color: #f5f3fb;
}

.block-container {
    max-width: 740px;
    padding: 1.5rem 1rem 4rem;
}

/* ── Header ── */
.page-header {
    background: linear-gradient(135deg, #5c3d9e 0%, #9b6fd4 100%);
    border-radius: 20px;
    padding: 2.5rem 2rem 2rem;
    text-align: center;
    color: white;
    margin-bottom: 2.2rem;
    box-shadow: 0 6px 30px rgba(92, 61, 158, 0.25);
}
.page-header h1 {
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0 0 0.4rem;
    letter-spacing: 0.3px;
}
.page-header p {
    margin: 0;
    opacity: 0.8;
    font-size: 0.95rem;
    font-weight: 300;
}

/* ── Card ── */
.lesson-card {
    background: white;
    border-radius: 18px;
    padding: 1.5rem 1.8rem 1.3rem;
    margin-bottom: 1.1rem;
    box-shadow: 0 2px 14px rgba(92, 61, 158, 0.07);
    border-right: 5px solid #7c55c8;
    position: relative;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.lesson-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 24px rgba(92, 61, 158, 0.14);
}

.card-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.9rem;
}
.lesson-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #3d1f7a;
}
.lesson-badge {
    background: #ede7ff;
    color: #6b42b8;
    padding: 0.22rem 0.9rem;
    border-radius: 30px;
    font-size: 0.78rem;
    font-weight: 600;
    white-space: nowrap;
}

.lesson-date {
    font-size: 0.9rem;
    color: #666;
    margin-bottom: 0.75rem;
}

.card-divider {
    border: none;
    border-top: 1px solid #f0eaff;
    margin: 0.6rem 0 0.85rem;
}

.lesson-topic {
    font-size: 1rem;
    font-weight: 600;
    color: #2e1760;
    margin-bottom: 0.25rem;
}
.lesson-process {
    font-size: 0.88rem;
    color: #777;
    margin-bottom: 0.7rem;
}
.lesson-teacher {
    font-size: 0.87rem;
    color: #7c55c8;
    font-weight: 500;
    margin-bottom: 1rem;
}

/* ── Calendar button ── */
.cal-btn {
    display: inline-block;
    background: linear-gradient(135deg, #5c3d9e, #9b6fd4);
    color: white !important;
    text-decoration: none !important;
    padding: 0.45rem 1.4rem;
    border-radius: 30px;
    font-size: 0.85rem;
    font-weight: 600;
    box-shadow: 0 3px 10px rgba(92, 61, 158, 0.3);
    transition: opacity 0.2s, transform 0.15s;
}
.cal-btn:hover {
    opacity: 0.88;
    transform: translateY(-1px);
    color: white !important;
    text-decoration: none !important;
}

.no-link {
    font-size: 0.82rem;
    color: #bbb;
    font-style: italic;
}

/* hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

lessons = [
    {
        "num": 2, "month": "יולי",
        "date": "8.7", "day": "רביעי", "time": "18:00–20:30",
        "topic": "איחוי חלקים",
        "process": "איחוי חלקים בגירסה משודרגת",
        "teacher": "טלי בן יעקב", "org": "NLPSTEPS",
        "url": "https://l1nk.dev/5h3fz14",
    },
    {
        "num": 3, "month": "אוגוסט",
        "date": "4.8", "day": "שלישי", "time": "18:00–20:30",
        "topic": "מטא-מודל",
        "process": "תרגול שאלות מטא על פי סוג",
        "teacher": "ג'וסלין סבג", "org": "המרכז להתפתחות אישית",
        "url": "https://acesse.one/l6tl6js",
    },
    {
        "num": 4, "month": "ספטמבר",
        "date": "6.9.26", "day": "ראשון", "time": "18:00–20:30",
        "topic": "סוויש",
        "process": "סוויש ויזואלי",
        "teacher": "תימורה שפירא", "org": "תימורה – לבחור ולהגשים",
        "url": "https://acesse.one/clpoww2",
    },
    {
        "num": 5, "month": "אוקטובר",
        "date": "11.10.26", "day": "ראשון", "time": "18:00–20:30",
        "topic": "מודל התקשורת",
        "process": "מודל התקשורת",
        "teacher": "רויטל חזות", "org": "המרכז להתפתחות אישית ומקצועית NLP",
        "url": "https://acesse.one/67l4axi",
    },
    {
        "num": 6, "month": "נובמבר",
        "date": "1.11.26", "day": "ראשון", "time": "18:00–21:00",
        "topic": "מילטון מודל",
        "process": "DTT בשפת מילטון",
        "teacher": "נרית רבינר", "org": "מרכז MNLP",
        "url": "https://l1nk.dev/6wj31es",
    },
    {
        "num": 7, "month": "דצמבר",
        "date": "17.12.26", "day": "חמישי", "time": "10:00–13:00",
        "topic": "אקולוגיה",
        "process": "מודל הניצחון של דיסני",
        "teacher": "מור-מלכה בנצ'יק", "org": "מכללת שלמים",
        "url": "https://l1nk.dev/dl4xpqv",
    },
    {
        "num": 8, "month": "ינואר",
        "date": "5.1.27", "day": "חמישי", "time": "10:00–12:30",
        "topic": "הנחות יסוד",
        "process": "מעגל הנחות יסוד",
        "teacher": "שרית למפרט שושן", "org": "קיבוץ משמרות / מכללת אורנים",
        "url": "https://l1nk.dev/96j1kz6",
    },
    {
        "num": 9, "month": "פברואר",
        "date": "3.2.27", "day": "רביעי", "time": "10:00–13:00",
        "topic": "רמות לוגיות",
        "process": "רמות לוגיות לשינוי אמונה",
        "teacher": "בוריס מלצר", "org": "מכללה לחיים מוצלחים",
        "url": "https://l1nk.dev/qxdzk0l",
    },
    {
        "num": 10, "month": "מרץ",
        "date": "7.3.27", "day": "ראשון", "time": "18:00–20:30",
        "topic": "אמונות",
        "process": "מוזאון האמונות העתיקות",
        "teacher": "הדס וילף", "org": "בית הספר ל-NLP של הדס וילף",
        "url": "https://l1nk.dev/siwi0ij",
    },
    {
        "num": 11, "month": "אפריל",
        "date": "שבוע ראשון של אפריל", "day": "", "time": "תאריך יעודכן",
        "topic": "Outcome",
        "process": "Outcome",
        "teacher": "עידית ג'וס", "org": "Joss NLP מ א ועד ת",
        "url": None,
    },
    {
        "num": 12, "month": "מאי",
        "date": "18.5.27", "day": "שלישי", "time": "10:00–12:30",
        "topic": "מרכיבי חושים",
        "process": "תרגול עם קלפים",
        "teacher": "אלה גבאי ומירי יפרח", "org": "NLP Creative School",
        "url": "https://l1nk.dev/agwd75s",
    },
    {
        "num": 13, "month": "יוני",
        "date": "7.6", "day": "שני", "time": "10:00–12:30",
        "topic": "עוגנים",
        "process": "מעגל המצויינות",
        "teacher": "עינת זיו", "org": "NLPnow",
        "url": "https://l1nk.dev/avm8vwp",
    },
]


def render_card(lesson):
    parts = [p for p in [lesson["date"], lesson["day"], lesson["time"]] if p]
    date_str = " &nbsp;|&nbsp; ".join(parts)

    if lesson["url"]:
        btn = f'<a href="{lesson["url"]}" target="_blank" class="cal-btn">🗓️ שמור ביומן</a>'
    else:
        btn = '<span class="no-link">⏳ קישור יעודכן בקרוב</span>'

    st.markdown(f"""
    <div class="lesson-card">
        <div class="card-top">
            <span class="lesson-title">שיעור {lesson['num']}</span>
            <span class="lesson-badge">{lesson['month']}</span>
        </div>
        <div class="lesson-date">📅 {date_str}</div>
        <hr class="card-divider">
        <div class="lesson-topic">🎯 {lesson['topic']}</div>
        <div class="lesson-process">🔄 {lesson['process']}</div>
        <div class="lesson-teacher">👩‍🏫 {lesson['teacher']} &nbsp;·&nbsp; {lesson['org']}</div>
        {btn}
    </div>
    """, unsafe_allow_html=True)


st.markdown("""
<div class="page-header">
    <h1>📚 שיעורים פתוחים</h1>
    <p>לוח שנה מלא · 2026–2027</p>
</div>
""", unsafe_allow_html=True)

for lesson in lessons:
    render_card(lesson)
