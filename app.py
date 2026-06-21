import streamlit as st
import streamlit.components.v1 as components
import os, sys, re
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (load_lessons, google_url, outlook_url, generate_ics,
                   month_from_iso, date_display, time_range, add_subscriber,
                   STATUS_OPTIONS, STATUS_COLORS, PUBLIC_URL, load_config)

st.set_page_config(
    page_title="שיעורים פתוחים – לוח שנה מלא",
    page_icon="📚",
    layout="centered",
)

# Hide admin page from sidebar nav
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0&display=block');
* { font-family: 'Heebo', sans-serif !important; }
/* Restore Material icon font — Heebo !important breaks Streamlit's expander icon text ligatures */
[data-testid="stExpanderToggleIcon"],
.material-icons, .material-symbols-rounded, .material-symbols-outlined,
[class*="material-icon"], [class*="material-symbol"] {
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    display: inline-block;
    overflow: hidden;
    max-width: 2rem;
    vertical-align: middle;
}
html, body, [class*="css"] { direction: rtl; }
[data-testid="stSidebarNavItems"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { display: none !important; }
[data-testid="manage-app-button"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
.stDeployButton { display: none !important; }
footer { display: none !important; }
.block-container { max-width: 740px; padding-top: 1.5rem; }

.page-header {
    background: linear-gradient(145deg,#3d1f7a 0%,#6b42b8 55%,#9b6fd4 100%);
    border-radius: 24px; padding: 2.8rem 2rem 2.6rem;
    text-align: center; color: white; margin-bottom: 1.4rem;
    box-shadow: 0 8px 36px rgba(61,31,122,0.32);
}
.logo-wrap {
    width:80px; height:80px; border-radius:50%;
    background:rgba(255,255,255,0.15); border:2px solid rgba(255,255,255,0.35);
    display:flex; align-items:center; justify-content:center;
    margin:0 auto 1.5rem; overflow:hidden;
}
.logo-wrap img { width:100%; height:100%; object-fit:contain; }
.save-date { font-size:.78rem; font-weight:300; letter-spacing:2.8px;
    text-transform:uppercase; opacity:.7; margin-bottom:.55rem; font-style:italic; }
.h-main { font-size:1.5rem; font-weight:500; opacity:.9; margin-bottom:.25rem; }
.h-sub  { font-size:2.2rem; font-weight:800; }

.intro-box {
    background:#ede7ff; border-radius:20px; padding:2rem 2.2rem 1.8rem;
    margin-bottom:2rem; box-shadow:0 2px 18px rgba(61,31,122,.1);
    text-align:right; direction:rtl;
}
.intro-box p { font-size:.97rem; line-height:1.85; color:#2e1760; margin-bottom:1rem; }
.intro-quote {
    margin-top:1.5rem; padding:1.2rem 1.5rem 1rem;
    background:rgba(255,255,255,.55); border-radius:14px; text-align:center;
}
.intro-quote blockquote { font-size:1.1rem; font-style:italic; color:#3d1f7a;
    font-weight:600; margin-bottom:.5rem; }
.intro-quote .sig { font-size:.78rem; color:#9b6fd4; letter-spacing:.5px; }

.lesson-card {
    background:white; border-radius:18px; padding:1.4rem 1.8rem 1.1rem;
    margin-bottom:.5rem; box-shadow:0 2px 14px rgba(92,61,158,.08);
    border-right:5px solid #7c55c8; direction:rtl;
}
.lc-top { display:flex; justify-content:space-between; align-items:center; margin-bottom:.2rem; }
.lc-title { font-size:1.1rem; font-weight:700; color:#3d1f7a; white-space:nowrap; }
.lc-badges { display:flex; align-items:center; justify-content:flex-end; gap:.3rem; flex-shrink:0; }
.lc-badge { background:#ede7ff; color:#6b42b8; padding:.2rem .9rem;
    border-radius:30px; font-size:.78rem; font-weight:600; white-space:nowrap; }
.lc-datetime { font-size:.85rem; color:#777; margin-bottom:.6rem; text-align:right; }
.lc-no-date { color:#ccc; font-style:italic; font-size:.82rem; }
.lc-divider { border:none; border-top:1px solid #f0eaff; margin:.5rem 0 .7rem; }
.lc-topic    { font-size:1rem; font-weight:600; color:#2e1760; margin-bottom:.05rem; text-align:right; }
.lc-subtitle { font-size:.88rem; color:#5c3d9e; font-style:italic; margin-bottom:.2rem; text-align:right; }
.lc-desc     { font-size:.85rem; color:#555; line-height:1.6; margin-bottom:.35rem; text-align:right; }
.lc-process  { font-size:.88rem; color:#777; margin-bottom:.5rem; text-align:right; }
.lc-teacher  { font-size:.87rem; color:#7c55c8; font-weight:500; margin-bottom:.45rem; text-align:right; }
.lc-done-badge { background:#ede9f8; color:#9b8fc0; padding:.2rem .7rem;
    border-radius:30px; font-size:.75rem; font-weight:500; white-space:nowrap; }
.lc-btn-divider { border:none; border-top:1px solid #f0eaff; margin:.7rem 0 .1rem; }

/* Past lesson card — softer look, flex wrap to prevent title/badge overlap */
.lesson-card.lc-past { opacity:.8; background:#f9f8ff; border-right-color:#c4b8e0; }
.lesson-card.lc-past .lc-top { flex-wrap:wrap; gap:.3rem; }
.lesson-card.lc-past .lc-title { white-space:normal; color:#888; }
.lesson-card.lc-past .lc-topic { color:#666; }
.lesson-card.lc-past .lc-process { color:#999; }
.lesson-card.lc-past .lc-teacher { color:#a090c0; }

/* Past section toggle — styled as a section header, not an action button */
div[data-testid="stButton"] > button {
    background:#f5f3fb !important; color:#3d1f7a !important;
    border:1.5px solid #e0d5f5 !important; border-radius:14px !important;
    font-size:.95rem !important; font-weight:600 !important;
    box-shadow:none !important; padding:.75rem 1.4rem !important;
}
div[data-testid="stButton"] > button:hover {
    background:#ede7ff !important; border-color:#c4b8e0 !important;
}

.stLinkButton a, .stDownloadButton button {
    background:linear-gradient(135deg,#5c3d9e,#9b6fd4) !important;
    color:white !important; border:none !important;
    border-radius:30px !important; font-size:.8rem !important;
    padding:.35rem 1rem !important; font-weight:600 !important;
    box-shadow:0 3px 10px rgba(92,61,158,.3) !important;
    white-space:nowrap !important;
}

/* Inactive lesson cards */
.lesson-card.lc-inactive { opacity:.65; }

/* Action buttons rendered inside the card HTML */
.lc-action-row {
    display:flex; flex-direction:column; align-items:center; gap:9px; padding-top:.5rem;
}
.lc-action-btn {
    display:block; width:75%; text-align:center;
    background:linear-gradient(135deg,#5c3d9e,#9b6fd4);
    color:white !important; border-radius:30px;
    font-size:.82rem; padding:.45rem 1.4rem; font-weight:600;
    box-shadow:0 3px 10px rgba(92,61,158,.25);
    text-decoration:none !important; cursor:pointer;
    transition:opacity .15s;
}
.lc-action-btn:hover { opacity:.88; color:white !important; }
@media (max-width:520px) { .lc-action-btn { width:100%; } }

/* Calendar sub-links (Google / Apple / Outlook) inside the card */
.lc-cal-links { display:flex; justify-content:center; gap:.55rem; flex-wrap:wrap; margin-top:.55rem; }
.lc-cal-link {
    font-size:.78rem; color:#7c55c8 !important; text-decoration:none !important;
    padding:.22rem .8rem; border-radius:20px; border:1px solid #e0d5f5;
    white-space:nowrap; transition:background .15s;
}
.lc-cal-link:hover { background:#f0eaff !important; }

/* Status badge — shown for every lesson */
.lc-status {
    display:inline-block; padding:.15rem .6rem;
    border-radius:12px; font-size:.73rem; font-weight:600; white-space:nowrap;
}

/* Lesson title with inline description expansion */
.lc-title-area { display:block; }
.lc-title-hint { cursor:help; }
.lc-hint-icon {
    display:inline-block; width:15px; height:15px;
    background:#9b6fd4; color:white; border-radius:50%;
    font-size:.62rem; font-weight:700; text-align:center;
    line-height:15px; margin-right:4px; vertical-align:middle;
    user-select:none;
}
.lc-desc-expand {
    display:none;
    background:#3d1f7a; color:white;
    border-radius:10px; padding:.55rem 1rem;
    font-size:.83rem; line-height:1.6;
    text-align:right; margin:.25rem 0 .15rem;
}
.lc-title-area:hover .lc-desc-expand,
.lc-title-area.desc-open .lc-desc-expand { display:block; }

/* Search bar */
.search-wrap { margin-bottom:1.2rem; }
[data-testid="stTextInput"] input[placeholder*="חפש"] {
    border-radius:30px !important; border:1.5px solid #e0d5f5 !important;
    padding:.55rem 1.2rem !important; font-size:.9rem !important;
    direction:rtl !important; text-align:right !important;
}
[data-testid="stTextInput"] input[placeholder*="חפש"]:focus {
    border-color:#7c55c8 !important; box-shadow:0 0 0 3px rgba(124,85,200,.12) !important;
}

/* Footer */
.page-footer {
    text-align:center; direction:rtl;
    margin-top:3rem; padding:1.5rem 1rem;
    border-top:1px solid #ede7ff;
    font-size:.82rem; color:#c0b8d4;
}
.footer-admin-link { color:#c8bde8 !important; text-decoration:none !important; font-size:.78rem; }
.footer-admin-link:hover { color:#7c55c8 !important; }
</style>
""", unsafe_allow_html=True)

LOGO = os.path.join(os.path.dirname(__file__), "logo_nlp.png")
import base64
logo_b64 = ""
if os.path.exists(LOGO):
    with open(LOGO, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()

st.markdown(f"""
<div class="page-header">
  <div class="logo-wrap">
    {'<img src="data:image/png;base64,' + logo_b64 + '">' if logo_b64 else '📖'}
  </div>
  <div class="save-date">Save the Date</div>
  <div class="h-main">לוח שנתי</div>
  <div class="h-sub">״שיעור פתוח״</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="intro-box">
  <p>פרויקט ״השיעורים הפתוחים״ הוא יוזמה התנדבותית של בתי הספר המוכרים על ידי לשכת ה־NLP הישראלית, שנולדה מתוך רצון להעניק ערך מקצועי, להעשיר את הידע ולחזק את קהילת חברי ועמיתי הלשכה.</p>
  <p>אנו מאמינים שלמידה אמיתית אינה מסתיימת בסיום הקורס, אלא ממשיכה דרך מפגש, סקרנות, תרגול ושיתוף בין אנשי מקצוע. כל שיעור הוא הזדמנות לפגוש זווית חדשה, להעמיק את ההבנה ולהרחיב את מפת העולם המקצועית והאישית.</p>
  <p>בכל מפגש תמצאו הסברים, הדגמות חיות ותרגולים מעשיים המבוססים על חומרי הלימוד של קורסי הפרקטישינר בבתי הספר השונים, תוך שמירה על רוח ה־NLP ועל מגוון דרכי ההוראה וההנחיה.</p>
  <p>אתם מוזמנים להצטרף, ללמוד, לתרגל, להרחיב את המפה ולהעשיר את החוויה המקצועית שלכם יחד עם קהילת ה־NLP הישראלית.</p>
  <div class="intro-quote">
    <blockquote>״כל תרגול הוא הזדמנות להרחיב את המפה.״</blockquote>
    <div class="sig">ועדת בתי הספר &nbsp;•&nbsp; פרויקט ״שיעור פתוח״</div>
  </div>
</div>
""", unsafe_allow_html=True)

if "sub_done" not in st.session_state:
    st.session_state.sub_done = {}

_cfg         = load_config()
_sub_enabled = _cfg.get("subscription_enabled", False)
_from_lesson = _cfg.get("display_from_lesson")
_to_lesson   = _cfg.get("display_to_lesson")

_search = st.text_input("חיפוש", placeholder="🔍 חפש לפי נושא, מורה, בית ספר...",
                         key="search_q", label_visibility="collapsed")

def _matches(l, q):
    q = q.strip().lower()
    if not q: return True
    return any(q in (l.get(f) or "").lower()
               for f in ["topic","subtitle","teacher","org","school","process","description"])

def _lesson_ended(l):
    """True when the lesson is completed or its end time is in the past."""
    if l.get("status") == "completed":
        return True
    if l.get("status") in ("cancelled", "postponed"):
        return False
    date_iso = l.get("date_iso")
    if not date_iso:
        return False
    try:
        ts  = l.get("time_start") or "00:00"
        h, m = map(int, ts.split(":"))
        end = datetime.strptime(date_iso, "%Y-%m-%d").replace(hour=h, minute=m) \
              + timedelta(minutes=int(l.get("duration_minutes") or 120))
        return datetime.now() > end
    except Exception:
        return False

def _in_range(l):
    n = l.get("num")
    if n is None: return True
    if _from_lesson is not None and int(n) < _from_lesson: return False
    if _to_lesson   is not None and int(n) > _to_lesson:   return False
    return True

all_lessons = [l for l in load_lessons()
               if l.get("visibility", "published") == "published" and _in_range(l)]
upcoming = sorted(
    [l for l in all_lessons if not _lesson_ended(l)],
    key=lambda l: l.get("date_iso") or "9999-99-99",
)
past = sorted(
    [l for l in all_lessons if _lesson_ended(l)],
    key=lambda l: l.get("date_iso") or "0000-00-00",
    reverse=True,
)

_q_lesson = st.query_params.get("lesson", "")
_q_mode   = st.query_params.get("mode",   "")

_upcoming_shown = [l for l in upcoming if _matches(l, _search)]
_past_shown     = [l for l in past     if _matches(l, _search)]

if _search.strip() and not _upcoming_shown and not _past_shown:
    st.info("לא נמצאו שיעורים התואמים לחיפוש.")

for l in _upcoming_shown:
    lid         = l["id"]
    month       = month_from_iso(l.get("date_iso") or "") or l.get("month", "")
    d_str       = date_display(l.get("date_iso") or "") or ""
    day         = l.get("day", "")
    t_rng       = time_range(l.get("time_start",""), l.get("duration_minutes",120)) if l.get("time_start") else ""
    status_key  = l.get("status", "planned")
    status_lbl  = STATUS_OPTIONS.get(status_key, "")
    status_col  = STATUS_COLORS.get(status_key, "#6b42b8")
    is_inactive = status_key in ("cancelled", "postponed")
    already_sub = lid in st.session_state.sub_done
    panel_open  = (_q_lesson == lid)
    panel_mode  = _q_mode if panel_open else ""

    date_parts   = [p for p in [d_str, day, t_rng] if p]
    full_dt_line = " &nbsp;|&nbsp; ".join(date_parts)
    datetime_row = (
        f'<div class="lc-datetime">{full_dt_line}</div>'
        if full_dt_line else
        '<div class="lc-datetime"><span class="lc-no-date">תאריך יעודכן</span></div>'
    )
    badge_html   = f'<span class="lc-badge">{month}</span>' if month else ''
    status_badge = (
        f'<span class="lc-status" style="background:{status_col}18;color:{status_col}">{status_lbl}</span>'
        if status_key != "planned" else ""
    )
    sub_html     = f'<div class="lc-subtitle">{l["subtitle"]}</div>' if l.get("subtitle","").strip() else ""
    org_part     = f' &nbsp;·&nbsp; {l["org"]}' if l.get("org") else ""
    gurl = google_url(l)
    ourl = outlook_url(l)
    ics  = generate_ics(l)

    # Description — inline expansion on hover (CSS :hover) + tap toggle on mobile
    desc_txt = (l.get("description") or "").strip()
    if desc_txt:
        title_html = (
            f'<span class="lc-title lc-title-hint">'
            f'שיעור {l["num"]}'
            f'<span class="lc-hint-icon">ⓘ</span>'
            f'</span>'
        )
        desc_expand_html = f'<div class="lc-desc-expand">{desc_txt}</div>'
    else:
        title_html = f'<span class="lc-title">שיעור {l["num"]}</span>'
        desc_expand_html = ""

    # Subscribe button (or status message for inactive/no-date)
    if is_inactive:
        action_html = f'<div style="font-size:.82rem;color:#aaa;text-align:center;padding-top:.4rem;">🚫 שיעור זה {status_lbl}</div>'
    elif not gurl:
        action_html = '<div style="font-size:.82rem;color:#bbb;text-align:center;padding-top:.4rem;">⏳ קישור יעודכן בקרוב</div>'
    elif _sub_enabled:
        sub_label = "✅ רשומ/ת לעדכונים" if already_sub else "📅 הוסף ליומן"
        sub_href  = "?" if (panel_open and panel_mode == "subscribe") else f"?lesson={lid}&amp;mode=subscribe"
        action_html = (
            f'<div class="lc-action-row">'
            f'<a href="{sub_href}" class="lc-action-btn">{sub_label}</a>'
            f'</div>'
        )
    else:
        # Subscriptions off — show calendar links directly, no form
        _cal_parts = []
        if gurl:
            _cal_parts.append(f'<a href="{gurl}" target="_blank" class="lc-cal-link">🔵 Google Calendar</a>')
        if ics:
            _ics_bytes = ics if isinstance(ics, bytes) else ics.encode("utf-8")
            _ics_b64   = base64.b64encode(_ics_bytes).decode()
            _cal_parts.append(
                f'<a href="data:text/calendar;base64,{_ics_b64}" '
                f'download="שיעור-{l["num"]}.ics" class="lc-cal-link">🍎 Apple / iCal</a>'
            )
        if ourl:
            _cal_parts.append(f'<a href="{ourl}" target="_blank" class="lc-cal-link">📅 Outlook</a>')
        action_html = (
            f'<div class="lc-action-row">'
            f'<div style="font-size:.83rem;font-weight:600;color:#5c3d9e;text-align:center;padding:.3rem 0">📅 הוסף ליומן</div>'
            f'<div class="lc-cal-links">{"".join(_cal_parts)}</div>'
            f'</div>'
        )

    inactive_cls = " lc-inactive" if is_inactive else ""
    btn_divider  = '<hr class="lc-btn-divider">' if (not is_inactive) else ""

    # ── Complete card as one HTML block ───────────────────────────────────────
    st.markdown(f"""
    <div class="lesson-card{inactive_cls}">
      <div class="lc-title-area"><div class="lc-top">
        {title_html}
        <span class="lc-badges">{status_badge}{badge_html}</span>
      </div>{desc_expand_html}</div>
      {datetime_row}
      <hr class="lc-divider">
      <div class="lc-topic">🎯 {l['topic']}</div>{sub_html}
      <div class="lc-process">🔄 {l.get('process','')}</div>
      <div class="lc-teacher">👩‍🏫 {l['teacher']}{org_part}</div>
      {btn_divider}
      {action_html}
    </div>
    """, unsafe_allow_html=True)

    # ── Subscribe panel (below card, only when open and subscriptions enabled) ──
    if _sub_enabled and panel_open and panel_mode == "subscribe":
        st.markdown(f'<div id="sub-panel-{lid}"></div>', unsafe_allow_html=True)
        components.html(
            f'<script>(function(){{'
            f'var n=0;'
            f'function f(){{'
            f'var e=parent.document.getElementById("sub-panel-{lid}");'
            f'if(e){{e.scrollIntoView({{behavior:"smooth",block:"start"}});}}'
            f'else if(n++<20)setTimeout(f,80);'
            f'}}'
            f'setTimeout(f,80);'
            f'}})();</script>',
            height=0,
        )
        # Calendar links shown after successful registration
        cal_links = []
        if gurl:
            cal_links.append(f'<a href="{gurl}" target="_blank" class="lc-cal-link">🔵 Google Calendar</a>')
        if ics:
            ics_bytes = ics if isinstance(ics, bytes) else ics.encode("utf-8")
            ics_b64   = base64.b64encode(ics_bytes).decode()
            cal_links.append(
                f'<a href="data:text/calendar;base64,{ics_b64}" '
                f'download="שיעור-{l["num"]}.ics" class="lc-cal-link">🍎 Apple / iCal</a>'
            )
        if ourl:
            cal_links.append(f'<a href="{ourl}" target="_blank" class="lc-cal-link">📅 Outlook</a>')
        cal_links_html = f'<div class="lc-cal-links" style="margin-top:.6rem">{"".join(cal_links)}</div>' if cal_links else ''

        if already_sub:
            done = st.session_state.sub_done[lid]
            fname = done.get("first_name", "")
            if done.get("new"):
                st.success(f"✅ {fname + ' — ' if fname else ''}נרשמת לעדכונים בהצלחה!")
            else:
                st.info("ℹ️ כתובת זו כבר רשומה לעדכונים עבור שיעור זה.")
            if cal_links_html:
                st.markdown('<p style="text-align:right;font-weight:600;margin:.4rem 0 .1rem">הוסף את השיעור ליומן שלך:</p>', unsafe_allow_html=True)
                st.markdown(cal_links_html, unsafe_allow_html=True)
        else:
            with st.form(f"sub_form_{lid}"):
                st.markdown("#### 📅 הוסף ליומן וקבל עדכונים")
                col1, col2 = st.columns(2)
                with col1:
                    fname_in = st.text_input("שם פרטי")
                with col2:
                    lname_in = st.text_input("שם משפחה")
                email_in   = st.text_input("כתובת מייל")
                consent_in = st.checkbox("אני מאשר/ת קבלת עדכונים לגבי שיעור זה בלבד")
                submitted  = st.form_submit_button("💾 שמור", type="primary")
            if submitted:
                err = None
                if not fname_in.strip():
                    err = "נא להזין שם פרטי"
                elif not lname_in.strip():
                    err = "נא להזין שם משפחה"
                elif not email_in.strip():
                    err = "נא להזין כתובת מייל"
                elif not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email_in.strip()):
                    err = "כתובת המייל אינה תקינה"
                elif not consent_in:
                    err = "יש לסמן את תיבת האישור"
                if err:
                    st.error(err)
                else:
                    result = add_subscriber(lid, l["num"], email_in.strip(), fname_in.strip(), lname_in.strip())
                    st.session_state.sub_done[lid] = {
                        "email": email_in.strip(), "first_name": fname_in.strip(), "new": result,
                    }
                    st.rerun()

    st.write("")

# ── Past lessons ─────────────────────────────────────────────────────────────
if _past_shown:
    st.markdown("---")
    if "past_expanded" not in st.session_state:
        st.session_state.past_expanded = False

    _arrow = "▲ סגור" if st.session_state.past_expanded else "▼ פתח"
    if st.button(
        f"📚 שיעורים שהתקיימו ({len(_past_shown)})  {_arrow}",
        key="past_toggle",
        use_container_width=True,
    ):
        st.session_state.past_expanded = not st.session_state.past_expanded
        st.rerun()

    if st.session_state.past_expanded:
        for l in _past_shown:
            month_p    = month_from_iso(l.get("date_iso") or "") or ""
            d_str_p    = date_display(l.get("date_iso") or "") or ""
            day_p      = l.get("day", "")
            t_rng_p    = time_range(l.get("time_start", ""), l.get("duration_minutes", 120)) if l.get("time_start") else ""
            dt_parts   = [p for p in [d_str_p, day_p, t_rng_p] if p]
            dt_line    = " &nbsp;|&nbsp; ".join(dt_parts)
            dt_row     = f'<div class="lc-datetime">{dt_line}</div>' if dt_line else ""
            badge_p    = f'<span class="lc-badge" style="background:#f0eeff;color:#b0a0d8">{month_p}</span>' if month_p else ''
            sub_p      = f'<div class="lc-subtitle">{l["subtitle"]}</div>' if l.get("subtitle", "").strip() else ""
            desc_p     = f'<div class="lc-desc">{l["description"]}</div>' if l.get("description", "").strip() else ""
            org_p      = f' &nbsp;·&nbsp; {l["org"]}' if l.get("org") else ""
            process_p  = f'<div class="lc-process">🔄 {l["process"]}</div>' if l.get("process", "").strip() else ""

            st.markdown(f"""
            <div class="lesson-card lc-past">
              <div class="lc-top">
                <span class="lc-title">שיעור {l['num']}</span>
                <span class="lc-badges">
                  <span class="lc-done-badge">✓ התקיים</span>
                  {badge_p}
                </span>
              </div>
              {dt_row}
              <hr class="lc-divider">
              <div class="lc-topic">🎯 {l['topic']}</div>
              {sub_p}
              {desc_p}
              {process_p}
              <div class="lc-teacher">👩‍🏫 {l['teacher']}{org_p}</div>
            </div>
            """, unsafe_allow_html=True)

            rec = l.get("recording_link", "")
            if rec:
                _, cr, _ = st.columns([1, 2, 1])
                with cr:
                    st.link_button("🎬 צפה בהקלטה", rec, key=f"rec_{l['id']}", use_container_width=True)

            st.write("")

st.markdown("""
<div class="page-footer">
  © לשכת ה־NLP הישראלית &nbsp;|&nbsp;
  <a href="/admin" class="footer-admin-link">כניסת מנהלים</a>
</div>
""", unsafe_allow_html=True)
