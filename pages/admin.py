"""Admin panel — /admin"""
import streamlit as st
import streamlit.components.v1 as components
import bcrypt, uuid, os, sys, copy
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    load_lessons, save_lessons, validate_lesson, renumber_lessons_by_date,
    list_backups, restore_backup, export_json, export_csv, import_json,
    log_action, load_log,
    load_config, save_config, get_all_admins, get_admin_by_email,
    get_admin_by_id, upsert_admin, delete_admin_by_id,
    set_reset_token, verify_reset_token, clear_reset_token,
    month_from_iso, day_from_iso, date_display, time_range,
    google_url, HEBREW_MONTHS, HEBREW_DAYS, DATA_FILE,
    STATUS_OPTIONS, STATUS_COLORS, VISIBILITY_OPTIONS, VISIBILITY_COLORS,
    add_subscriber, get_subscribers_for_lesson, count_subscribers, total_subscribers,
    export_subscribers_csv_for_lesson, export_all_subscribers_csv,
    load_subscribers, lesson_changed_fields, generate_update_email,
    generate_whatsapp_text, generate_general_email, PUBLIC_URL,
    NOTIFY_FIELD_LABELS,
)

st.set_page_config(page_title="ניהול שיעורים פתוחים", page_icon="🛡️", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700&display=swap');
* { font-family:'Heebo',sans-serif !important; }
html,body,[class*="css"] { direction:rtl; }
[data-testid="stSidebarNavItems"] { display:none !important; }

/* Fix password visibility toggle — RTL direction breaks the eye-icon click in Streamlit */
[data-baseweb="base-input"] { direction:ltr !important; }
[data-baseweb="base-input"] input { direction:rtl !important; text-align:right !important; }

/* ── Admin cards ── */
.admin-badge { background:#3d1f7a; color:white; padding:.15rem .6rem;
  border-radius:12px; font-size:.75rem; margin-right:.4rem; }
.viewer-badge { background:#b08010; color:white; padding:.15rem .6rem;
  border-radius:12px; font-size:.75rem; margin-right:.4rem; }
.lesson-row { background:white; border-radius:12px; padding:.9rem 1.2rem;
  margin-bottom:.6rem; border-right:4px solid #7c55c8;
  box-shadow:0 1px 8px rgba(92,61,158,.08); direction:rtl; }
.lrow-title { font-size:.95rem; font-weight:700; color:#3d1f7a;
  white-space:normal; word-break:break-word; }
.lrow-meta  { font-size:.82rem; color:#666; margin-top:.15rem;
  white-space:normal; word-break:break-word; }
.preview-card { background:white; border-radius:14px; padding:1.2rem 1.4rem;
  border-right:5px solid #7c55c8; box-shadow:0 2px 12px rgba(92,61,158,.1); }

/* ── Buttons: prevent letter-by-letter wrap ── */
[data-testid="stButton"] button, [data-testid="stLinkButton"] a {
  white-space:nowrap !important; min-width:0 !important;
}

/* ── Dashboard: responsive metric cards ── */
.metric-grid {
  display:flex; flex-wrap:wrap; gap:.6rem; margin-bottom:.5rem; direction:rtl;
}
.metric-card {
  flex:1 1 120px; min-width:110px; background:white;
  border-radius:14px; padding:.85rem .8rem; text-align:center;
  box-shadow:0 1px 10px rgba(92,61,158,.08); border-bottom:3px solid #ede7ff;
}
.metric-card .m-val { font-size:1.6rem; font-weight:700; color:#3d1f7a; }
.metric-card .m-lbl { font-size:.75rem; color:#666; margin-top:.15rem; }

/* ── Dashboard: responsive status grid ── */
.status-grid {
  display:flex; flex-wrap:wrap; gap:.5rem; margin:.5rem 0; direction:rtl;
}
.status-card {
  flex:1 1 110px; min-width:100px; text-align:center;
  padding:.75rem .4rem; border-radius:12px; border-top:3px solid;
}
.status-card .s-val { font-size:1.5rem; font-weight:700; }
.status-card .s-lbl { font-size:.75rem; color:#555; }

/* ── Activity log: horizontal scroll ── */
.log-scroll { overflow-x:auto; border:1px solid #ede7ff; border-radius:12px; }
.log-row {
  font-size:.83rem; padding:.38rem .7rem; border-bottom:1px solid #f0eaff;
  white-space:nowrap; direction:rtl;
}
.log-row:nth-child(odd) { background:#faf8ff; }
.tag-add    { color:#1a7f37; font-weight:600; }
.tag-edit   { color:#0550ae; font-weight:600; }
.tag-delete { color:#cf222e; font-weight:600; }
.tag-login  { color:#6b42b8; font-weight:600; }
.tag-other  { color:#555; font-weight:600; }

/* ── Collapse form-split-marker ── */
div[data-testid="stMarkdown"]:has(.form-split-marker) {
  height:0 !important; overflow:hidden !important;
  margin:0 !important; padding:0 !important; line-height:0 !important;
}

/* ── Lesson form: white background bridges the column gap, stack on narrow ── */
div[data-testid="stMarkdown"]:has(.form-split-marker) + div[data-testid="stHorizontalBlock"] {
  background:white; border-radius:12px; padding:.5rem .25rem !important; gap:.75rem !important;
}
@media (max-width:1100px) {
  div[data-testid="stMarkdown"]:has(.form-split-marker) + div[data-testid="stHorizontalBlock"] {
    flex-wrap:wrap !important;
  }
  div[data-testid="stMarkdown"]:has(.form-split-marker) + div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    flex:1 1 100% !important; width:100% !important;
  }
}

/* ══════════════════════════════════════════════════════
   RESPONSIVE — Admin Panel
   ══════════════════════════════════════════════════════ */

/* Main content: always fill available width, never create a ghost center column */
section[data-testid="stMain"] .block-container {
  max-width:100% !important;
  padding-left:1.5rem !important;
  padding-right:1.5rem !important;
  overflow-x:hidden !important;
}

/* Sidebar: 220 px when visible, overflow hidden prevents bleed */
section[data-testid="stSidebar"] {
  min-width:220px !important; max-width:280px !important;
  overflow:hidden !important;
}
section[data-testid="stSidebar"] > div:first-child { min-width:0 !important; overflow:hidden !important; }
/* Sidebar text: wrap at word boundaries, never letter-by-letter */
section[data-testid="stSidebar"] [data-testid="stMarkdown"],
section[data-testid="stSidebar"] code {
  white-space:normal !important; word-break:break-word !important;
  overflow-wrap:anywhere !important; overflow:hidden !important;
}

/* Tab bar: always scrollable, never wrap or break mid-word */
[data-testid="stTabs"] > div:first-child {
  overflow-x:auto !important; flex-wrap:nowrap !important;
  -webkit-overflow-scrolling:touch; scrollbar-width:none;
}
[data-testid="stTabs"] > div:first-child::-webkit-scrollbar { display:none; }
[data-testid="stTabs"] [role="tab"] {
  white-space:nowrap !important; flex-shrink:0 !important;
  min-width:fit-content !important;
  font-size:.77rem !important; padding:.45rem .6rem !important;
}

/* Buttons / links: never split across lines */
[data-testid="stButton"] button, [data-testid="stLinkButton"] a {
  white-space:nowrap !important;
}

/* Content cards: wrap text at word boundaries */
.lesson-row, .lrow-title, .lrow-meta,
.preview-card, .metric-card, .status-card {
  word-break:break-word !important; overflow-wrap:break-word !important;
}

/* All horizontal blocks: wrap when columns don't fit */
div[data-testid="stHorizontalBlock"] {
  flex-wrap:wrap !important;
}
/* Columns: can shrink and grow freely, no hard minimum that forces overflow */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
  min-width:0 !important;
  overflow:visible !important;
  flex-shrink:1 !important;
}

/* ── Breakpoint: 900 px ── */
@media (max-width:900px) {
  /* Tab labels: compact */
  [data-testid="stTabs"] [role="tab"] {
    font-size:.72rem !important; padding:.38rem .45rem !important;
  }
  /* Lesson / admin list rows:
     first column (title/info) → full width
     remaining columns (icon buttons) → auto-width, side-by-side */
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child {
    flex:1 1 100% !important; min-width:0 !important;
  }
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:not(:first-child) {
    flex:0 0 auto !important; min-width:44px !important;
  }
}

/* ── Breakpoint: 650 px — fully stack all columns ── */
@media (max-width:650px) {
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    flex:1 1 100% !important; width:100% !important; min-width:0 !important;
  }
}

/* ── Login page: full-page card layout ── */
div[data-testid="stMarkdown"]:has(.login-marker) { display:none !important; }

.stApp:has(.login-marker) {
  background: linear-gradient(135deg,#f0ebff 0%,#e8e0ff 50%,#ddd5ff 100%) !important;
}
/* Hide sidebar and strip main-area background so the gradient shows */
.stApp:has(.login-marker) [data-testid="stSidebar"],
.stApp:has(.login-marker) section[data-testid="stSidebar"] { display:none !important; }
.stApp:has(.login-marker) section[data-testid="stMain"] { background:transparent !important; }

/* White card — target both Streamlit block-container naming conventions */
.stApp:has(.login-marker) .block-container,
.stApp:has(.login-marker) [data-testid="stMainBlockContainer"] {
  max-width: 420px !important;
  background: white !important;
  border-radius: 24px !important;
  box-shadow: 0 8px 40px rgba(92,61,158,.18) !important;
  padding: 2.5rem 2rem 2rem !important;
  margin: 6vh auto 0 !important;
}
.stApp:has(.login-marker) h2 { color:#3d1f7a !important; text-align:center !important; margin-bottom:1rem !important; }
.stApp:has(.login-marker) [data-testid="stTextInput"] input { font-size:.95rem !important; }
.stApp:has(.login-marker) [data-testid="stButton"] button { width:100% !important; }
</style>""", unsafe_allow_html=True)

# ── Session defaults ──────────────────────────────────────────────────────────
DEFAULTS = {
    "logged_in": False, "admin_email": "", "admin_name": "",
    "login_attempts": 0, "locked_until": None,
    "edit_lesson": None, "adding_lesson": False, "confirm_delete": None,
    "edit_admin": None, "adding_admin": False, "confirm_del_admin": None,
    "show_change_pw": False, "active_tab": 0,
    "notify_lesson":    None,
    "notify_wa_draft":  None,
    "view_subs_lesson": None,
    "show_email_for":   None,
    "lesson_saved":     False,
    "confirm_renumber": False,
    "whatsapp_draft":   None,
    "pubkit_open":      None,
    "comm_lesson_id":   None,
    "comm_channel":     "whatsapp",
    "comm_audience":    "lesson",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

DURATION_OPTIONS = {60:"שעה",90:"שעה וחצי",120:"שעתיים",
                    150:"שעתיים וחצי",180:"שלוש שעות",210:"שלוש וחצי שעות",240:"ארבע שעות"}
DAY_OPTIONS = ["ראשון","שני","שלישי","רביעי","חמישי","שישי","שבת"]

def actor():
    return st.session_state.admin_email, st.session_state.admin_name

def is_viewer():
    cfg = load_config()
    me  = next((a for a in cfg.get("admins", [])
                if a["email"] == st.session_state.admin_email), {})
    return me.get("role", "admin") == "viewer"

def whatsapp_url(text):
    from urllib.parse import quote
    return f"https://wa.me/?text={quote(text)}"

def public_lesson_url(l):
    return f"{PUBLIC_URL}?lesson={l['id']}&mode=subscribe"

# ════════════════════════════════════════════════════════════════════════════
# PUBLISHING KIT panel (per lesson)
# ════════════════════════════════════════════════════════════════════════════
def render_pubkit(l):
    wa_key     = f"pk_wa_{l['id']}"
    subj_key   = f"pk_subj_{l['id']}"
    body_key   = f"pk_body_{l['id']}"

    default_wa   = generate_whatsapp_text(l)
    default_subj, default_body = generate_general_email(l)

    with st.expander(f"📦 ערכת פרסום — שיעור {l['num']}", expanded=True):
        pub_url = public_lesson_url(l)
        st.markdown(
            f'**קישור ציבורי לשיעור:** '
            f'<a href="{pub_url}" target="_blank" style="color:#6b42b8">{pub_url}</a>',
            unsafe_allow_html=True,
        )
        st.markdown("---")

        pk1, pk2 = st.tabs(["💬 וואטסאפ", "📧 מייל"])

        with pk1:
            wa_txt = st.text_area("הודעת וואטסאפ:", value=default_wa, height=260, key=wa_key)
            wc1, wc2 = st.columns(2)
            wc1.link_button("💬 פתח בוואטסאפ", whatsapp_url(wa_txt),
                            use_container_width=True, type="primary")
            wc2.button("📋 העתק טקסט", key=f"pk_wa_copy_{l['id']}",
                       use_container_width=True,
                       help="העתק את הטקסט ללוח")

        with pk2:
            subj = st.text_input("נושא:", value=default_subj, key=subj_key)
            body = st.text_area("גוף המייל:", value=default_body, height=260, key=body_key)
            subs = get_subscribers_for_lesson(l["id"])
            st.caption(f"נרשמים לשיעור זה: {len(subs)}")
            if subs:
                with st.expander("רשימת נמענים"):
                    st.text("\n".join(
                        f"{s.get('first_name','')} {s.get('last_name','')} <{s['email']}>".strip()
                        for s in subs
                    ))
            mc1, mc2 = st.columns(2)
            mc1.code(subj, language=None)
            if mc2.button("📋 העתק גוף מייל", key=f"pk_mail_copy_{l['id']}", use_container_width=True):
                st.toast("הטקסט הועתק!")
            st.code(body, language=None)

        if st.button("❌ סגור ערכת פרסום", key=f"pk_close_{l['id']}"):
            st.session_state.pubkit_open = None
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# COMMUNICATION CENTER tab
# ════════════════════════════════════════════════════════════════════════════
def tab_communication():
    st.markdown("### 📣 מרכז תקשורת")
    lessons = load_lessons()
    all_subs = [s for s in load_subscribers() if s.get("active", True) and s.get("consent", True)]

    # Audience selector
    aud_col, ch_col = st.columns(2)
    audience = aud_col.radio("קהל יעד:", ["כל הנרשמים", "שיעור ספציפי"],
                              horizontal=True, key="comm_aud_radio")
    channel  = ch_col.radio("ערוץ:", ["💬 וואטסאפ", "📧 מייל"],
                             horizontal=True, key="comm_ch_radio")

    selected_lesson = None
    if audience == "שיעור ספציפי":
        lesson_map = {f"שיעור {l['num']} — {l['topic']}": l for l in lessons}
        if not lesson_map:
            st.info("אין שיעורים במערכת."); return
        sel = st.selectbox("בחר שיעור:", list(lesson_map.keys()), key="comm_lesson_sel")
        selected_lesson = lesson_map[sel]
        target_subs = get_subscribers_for_lesson(selected_lesson["id"])
    else:
        target_subs = all_subs

    st.caption(f"נמענים: **{len(target_subs)}**")
    st.markdown("---")

    if "💬" in channel:
        # WhatsApp
        if selected_lesson:
            default_txt = generate_whatsapp_text(selected_lesson)
        else:
            default_txt = (
                "*שיעור פתוח - לשכת ה NLP הישראלית*\n\n"
                "שלום לכולם,\n\n"
                "[כתוב כאן את ההודעה]\n\n"
                f"לוח השיעורים: {PUBLIC_URL}\n\n"
                "מוזמנים להצטרף!"
            )
        wa_msg = st.text_area("הודעת וואטסאפ:", value=default_txt, height=280, key="comm_wa_txt")

        if target_subs:
            phones_note = "וואטסאפ אינו תומך בשליחה המונית ישירות. ניתן לפתוח שיחה עם כל נמען, או לשלוח לקבוצה ידנית."
            st.info(phones_note)

        cc1, cc2 = st.columns(2)
        cc1.link_button("💬 פתח בוואטסאפ", whatsapp_url(wa_msg),
                        use_container_width=True, type="primary")
        with cc2:
            if st.button("📋 העתק הודעה", key="comm_wa_copy", use_container_width=True):
                st.toast("הועתק! הדבק בוואטסאפ.")
        st.code(wa_msg, language=None)

    else:
        # Email
        if selected_lesson:
            default_subj, default_body = generate_general_email(selected_lesson)
        else:
            default_subj = "עדכון מלשכת ה-NLP הישראלית — שיעורים פתוחים"
            default_body = (
                "שלום,\n\n[כתוב כאן את תוכן המייל]\n\n"
                f"לוח השיעורים: {PUBLIC_URL}\n\n"
                "נשמח לראותך,\nועדת בתי הספר – פרויקט ״שיעור פתוח״\n\n---\n"
                "להסרה מרשימת תפוצה זו, השב/י למייל זה עם הנושא: הסרה"
            )

        em_subj = st.text_input("נושא המייל:", value=default_subj, key="comm_email_subj")
        em_body = st.text_area("גוף המייל:", value=default_body, height=300, key="comm_email_body")

        st.markdown("---")
        st.markdown("**תצוגה מקדימה:**")
        st.markdown(
            f'<div style="background:white;border:1px solid #e0d5f5;border-radius:12px;'
            f'padding:1.2rem 1.5rem;direction:rtl;font-size:.9rem;line-height:1.7">'
            f'<b>נושא:</b> {em_subj}<br><hr style="border:none;border-top:1px solid #f0eaff;margin:.5rem 0">'
            f'<pre style="font-family:inherit;white-space:pre-wrap;font-size:.88rem">{em_body}</pre>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        if target_subs:
            with st.expander(f"רשימת נמענים ({len(target_subs)})"):
                st.text("\n".join(
                    f"{s.get('first_name','')} {s.get('last_name','')} <{s['email']}>".strip()
                    for s in target_subs
                ))
        ec1, ec2 = st.columns(2)
        with ec1:
            st.code(em_subj, language=None)
        if ec2.button("📋 העתק גוף מייל", key="comm_copy_body", use_container_width=True):
            st.toast("הועתק!")
        st.code(em_body, language=None)
        st.info(
            "💡 **לשליחה אוטומטית** יש לחבר ספק אימייל (Mailgun, SendGrid, Gmail SMTP). "
            "כרגע ניתן להעתיק ולשלוח ידנית."
        )

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        st.markdown(f"### 🛡️ ניהול")
        _role = next((a.get("role","admin") for a in load_config().get("admins",[])
                      if a["email"]==st.session_state.admin_email), "admin")
        _role_badge = ' <span class="viewer-badge">צופה בלבד</span>' if _role == "viewer" else ""
        st.markdown(f"**{st.session_state.admin_name}**{_role_badge}  \n`{st.session_state.admin_email}`",
                    unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🔑 שנה סיסמה", use_container_width=True):
            st.session_state.show_change_pw = not st.session_state.show_change_pw
            st.rerun()
        st.markdown("---")
        if st.button("🚪 יציאה", use_container_width=True, type="primary"):
            log_action(*actor(), "logout", "יציאה מהמערכת")
            for k in DEFAULTS: st.session_state[k] = DEFAULTS[k]
            st.rerun()
        st.markdown("---")
        st.caption(f"גיבוי אחרון: {_latest_backup_time()}")

def _latest_backup_time():
    bk = list_backups()
    return bk[0]["label"] if bk else "—"

# ════════════════════════════════════════════════════════════════════════════
# CHANGE PASSWORD (inline panel)
# ════════════════════════════════════════════════════════════════════════════
def change_password_panel():
    with st.expander("🔑 שינוי סיסמה", expanded=True):
        c1,c2,c3 = st.columns(3)
        cur  = c1.text_input("סיסמה נוכחית",  type="password", key="cp_cur")
        new1 = c2.text_input("סיסמה חדשה",    type="password", key="cp_new1")
        new2 = c3.text_input("אימות סיסמה חדשה", type="password", key="cp_new2")
        if st.button("עדכן סיסמה", key="cp_submit"):
            admin = get_admin_by_email(st.session_state.admin_email)
            if not bcrypt.checkpw(cur.encode(), admin["password_hash"].encode()):
                st.error("הסיסמה הנוכחית שגויה")
            elif len(new1) < 6:
                st.error("הסיסמה החדשה חייבת להכיל לפחות 6 תווים")
            elif new1 != new2:
                st.error("הסיסמאות אינן תואמות")
            else:
                admin["password_hash"] = bcrypt.hashpw(new1.encode(), bcrypt.gensalt(12)).decode()
                upsert_admin(admin)
                log_action(*actor(), "change_password", "שינוי סיסמה אישית")
                st.success("✅ הסיסמה עודכנה")
                st.session_state.show_change_pw = False
                st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# PREVIEW
# ════════════════════════════════════════════════════════════════════════════
def render_preview(l):
    month      = month_from_iso(l.get("date_iso") or "") or ""
    d_str      = date_display(l.get("date_iso") or "") or "תאריך יעודכן"
    day        = l.get("day", "")
    t_rng      = time_range(l.get("time_start",""), l.get("duration_minutes",120)) if l.get("time_start") else ""
    date_line  = " | ".join(p for p in [d_str, day, t_rng] if p)
    gurl       = google_url(l)
    status_key = l.get("status","planned")
    status_lbl = STATUS_OPTIONS.get(status_key, "מתוכנן")
    status_col = STATUS_COLORS.get(status_key, "#6b42b8")
    sub_html   = (f'<div style="font-size:.84rem;color:#5c3d9e;margin-bottom:.15rem;font-style:italic">'
                  f'{l["subtitle"]}</div>' if l.get("subtitle","").strip() else "")
    desc_html  = (f'<div style="font-size:.81rem;color:#555;margin-bottom:.3rem;line-height:1.55">'
                  f'{l["description"]}</div>' if l.get("description","").strip() else "")
    btn = (f'<a href="{gurl}" target="_blank" style="background:linear-gradient(135deg,#5c3d9e,#9b6fd4);'
           f'color:white;padding:.3rem .9rem;border-radius:20px;font-size:.78rem;text-decoration:none;font-weight:600">'
           f'🗓️ שמור ביומן</a>' if gurl else
           '<span style="color:#bbb;font-size:.8rem;font-style:italic">⏳ קישור יעודכן בקרוב</span>')
    st.markdown(f"""<div class="preview-card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.5rem">
        <b style="color:#3d1f7a">שיעור {l.get('num','')} &mdash; {l.get('topic','')}</b>
        <div>
          <span style="background:{status_col}20;color:{status_col};padding:.12rem .55rem;
            border-radius:10px;font-size:.71rem;font-weight:600;margin-left:.35rem">{status_lbl}</span>
          <span style="background:#ede7ff;color:#6b42b8;padding:.12rem .6rem;border-radius:20px;font-size:.71rem">{month}</span>
        </div>
      </div>
      <div style="font-size:.83rem;color:#666;margin-bottom:.5rem">📅 {date_line}</div>
      <hr style="border:none;border-top:1px solid #f0eaff;margin:.4rem 0 .55rem">
      <div style="font-weight:600;color:#2e1760;margin-bottom:.05rem;font-size:.93rem">🎯 {l.get('topic','')}</div>
      {sub_html}{desc_html}
      <div style="font-size:.82rem;color:#777;margin-bottom:.4rem">🔄 {l.get('process','')}</div>
      <div style="font-size:.82rem;color:#7c55c8;font-weight:500;margin-bottom:.7rem">
        👩‍🏫 {l.get('teacher','')}{(' · '+l['org']) if l.get('org') else ''}</div>
      {btn}
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# LESSON FORM
# ════════════════════════════════════════════════════════════════════════════
def lesson_form(existing=None, is_dup=False):
    is_new = existing is None or is_dup
    title  = ("➕ שיעור חדש" if existing is None
               else ("📋 שכפול שיעור" if is_dup else f"✏️ עריכת שיעור {existing.get('num','')}"))
    st.markdown(f"### {title}")
    st.markdown('<div class="form-split-marker"></div>', unsafe_allow_html=True)
    left, right = st.columns([1.15, 1])

    with left:
        # ── Status + Visibility + Number ─────────────────────────────────
        scol, vcol, ncol = st.columns([2, 2, 1])
        with scol:
            stat_keys = list(STATUS_OPTIONS.keys())
            stat_val  = (existing.get("status","planned") if existing else "planned")
            stat_idx  = stat_keys.index(stat_val) if stat_val in stat_keys else 0
            status_lbl = st.selectbox("סטטוס", list(STATUS_OPTIONS.values()), index=stat_idx)
            status     = stat_keys[list(STATUS_OPTIONS.values()).index(status_lbl)]
        with vcol:
            vis_keys  = list(VISIBILITY_OPTIONS.keys())
            vis_val   = (existing.get("visibility","published") if existing else "published")
            vis_idx   = vis_keys.index(vis_val) if vis_val in vis_keys else 0
            vis_lbl   = st.selectbox("נראות", list(VISIBILITY_OPTIONS.values()), index=vis_idx)
            visibility = vis_keys[list(VISIBILITY_OPTIONS.values()).index(vis_lbl)]
        with ncol:
            all_lessons = load_lessons()
            next_num    = (max((l["num"] for l in all_lessons), default=1) + 1
                           if is_new else int(existing.get("num", 1)))
            num = st.number_input("מספר שיעור", value=next_num, min_value=1, step=1)

        st.divider()

        # ── Content ──────────────────────────────────────────────────────
        st.caption("תוכן השיעור")
        topic    = st.text_input("נושא ראשי / כותרת *",
                                 value=existing.get("topic","") if existing else "")
        subtitle = st.text_input("נושא ספציפי / כותרת משנה",
                                 value=existing.get("subtitle","") if existing else "",
                                 help="יצורף לכותרת האירוע ביומן")
        description = st.text_area("תיאור כללי",
                                   value=existing.get("description","") if existing else "",
                                   height=75, help="תיאור חופשי של תוכן השיעור")
        process  = st.text_input("תהליך / פעילות",
                                 value=existing.get("process","") if existing else "")

        st.divider()

        # ── Teacher ──────────────────────────────────────────────────────
        st.caption("מרצה")
        tcol, ocol = st.columns(2)
        with tcol:
            teacher = st.text_input("שם המרצה *",
                                    value=existing.get("teacher","") if existing else "")
        with ocol:
            org = st.text_input("בית ספר / מוסד",
                                value=existing.get("org","") if existing else "")

        st.divider()

        # ── Schedule ─────────────────────────────────────────────────────
        st.caption("לוח זמנים")
        date_val = None
        if existing and existing.get("date_iso"):
            try: date_val = datetime.strptime(existing["date_iso"], "%Y-%m-%d").date()
            except: pass
        dcol, daycol = st.columns(2)
        with dcol:
            chosen_date = st.date_input("תאריך", value=date_val, format="DD/MM/YYYY")
        date_iso    = chosen_date.strftime("%Y-%m-%d") if chosen_date else None
        auto_day    = day_from_iso(date_iso) if date_iso else ""
        day_display = auto_day or (existing.get("day","") if existing else "")
        day_idx     = DAY_OPTIONS.index(day_display) if day_display in DAY_OPTIONS else 0
        with daycol:
            day = st.selectbox("יום בשבוע", DAY_OPTIONS, index=day_idx)

        t1col, t2col = st.columns(2)
        with t1col:
            time_start = st.text_input("שעת התחלה (HH:MM)",
                                       value=existing.get("time_start","18:00") if existing else "18:00")
        with t2col:
            dur_keys = list(DURATION_OPTIONS.keys())
            dur_val  = int(existing.get("duration_minutes",150)) if existing else 150
            dur_idx  = dur_keys.index(dur_val) if dur_val in dur_keys else 3
            duration = st.selectbox("משך", list(DURATION_OPTIONS.values()), index=dur_idx)
            dur_min  = dur_keys[list(DURATION_OPTIONS.values()).index(duration)]

        st.divider()

        # ── Links ────────────────────────────────────────────────────────
        st.caption("קישורים")
        zoom_link         = st.text_input("קישור Zoom (ביום השיעור)",
                                          value=existing.get("zoom_link","") if existing else "")
        registration_link = st.text_input("קישור הרשמה",
                                          value=existing.get("registration_link","") if existing else "")
        lcol1, lcol2 = st.columns(2)
        with lcol1:
            rec_link   = st.text_input("קישור הקלטה",
                                       value=existing.get("recording_link","") if existing else "")
        with lcol2:
            files_link = st.text_input("קישור חומרים",
                                       value=existing.get("files_link","") if existing else "")

    draft = {
        "id":                (str(uuid.uuid4()) if is_new else existing["id"]),
        "num":               num,
        "status":            status,
        "visibility":        visibility,
        "topic":             topic,
        "subtitle":          subtitle,
        "description":       description,
        "process":           process,
        "teacher":           teacher,
        "org":               org,
        "date_iso":          date_iso,
        "day":               day,
        "time_start":        time_start,
        "duration_minutes":  dur_min,
        "zoom_link":         zoom_link,
        "registration_link": registration_link,
        "recording_link":    rec_link,
        "files_link":        files_link,
        "school":     existing.get("school","")     if existing else "",
        "category":   existing.get("category","")   if existing else "",
        "speaker_photo": existing.get("speaker_photo","") if existing else "",
        "tags":       existing.get("tags",[])       if existing else [],
    }

    with right:
        st.markdown("**תצוגה מקדימה**")
        render_preview(draft)
        errs = validate_lesson(draft)
        if errs:
            for e in errs: st.warning(f"⚠️ {e}")

    st.markdown("---")
    cs, cc, _ = st.columns([1, 1, 5])
    save_btn   = cs.button("💾 שמור", type="primary", use_container_width=True)
    cancel_btn = cc.button("ביטול",                  use_container_width=True)

    if cancel_btn:
        st.session_state.edit_lesson   = None
        st.session_state.adding_lesson = False
        st.rerun()

    if save_btn:
        errs = validate_lesson(draft)
        if errs:
            for e in errs: st.error(f"❌ {e}")
        else:
            lessons = load_lessons()
            action  = "add_lesson" if is_new else "edit_lesson"
            detail  = f"שיעור {num}: {topic}"
            if is_new:
                lessons.append(draft)
            else:
                old_lesson = next((l for l in lessons if l["id"] == draft["id"]), None)
                if old_lesson:
                    changed   = lesson_changed_fields(old_lesson, draft)
                    sub_count = count_subscribers(draft["id"])
                    if changed and sub_count > 0:
                        st.session_state.notify_lesson = {
                            "lesson": draft, "sub_count": sub_count, "changed": changed,
                        }
                lessons = [draft if l["id"] == draft["id"] else l for l in lessons]
            save_lessons(lessons)
            log_action(*actor(), action, detail)
            st.session_state.edit_lesson   = None
            st.session_state.adding_lesson = False
            st.session_state.lesson_saved  = True
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — LESSONS
# ════════════════════════════════════════════════════════════════════════════
def tab_dashboard():
    from datetime import date as _date
    lessons  = load_lessons()
    today    = _date.today().isoformat()
    upcoming = [l for l in lessons
                if l.get("date_iso") and l["date_iso"] >= today
                and l.get("status","planned") not in ("cancelled","completed")]
    done_cnt = sum(1 for l in lessons if l.get("status") == "completed")
    all_subs = total_subscribers()
    admins   = get_all_admins()
    log      = load_log()
    last_ts  = log[0]["timestamp"] if log else "—"

    # ── Metric cards ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="metric-grid">
      <div class="metric-card"><div class="m-val">{len(lessons)}</div><div class="m-lbl">📚 סה״כ שיעורים</div></div>
      <div class="metric-card"><div class="m-val">{len(upcoming)}</div><div class="m-lbl">📅 שיעורים קרובים</div></div>
      <div class="metric-card"><div class="m-val">{done_cnt}</div><div class="m-lbl">✅ הסתיימו</div></div>
      <div class="metric-card"><div class="m-val">{all_subs}</div><div class="m-lbl">👥 נרשמים</div></div>
      <div class="metric-card"><div class="m-val">{len(admins)}</div><div class="m-lbl">🛡️ מנהלים</div></div>
    </div>
    <div style="font-size:.78rem;color:#999;text-align:right;margin-bottom:.25rem">עדכון אחרון: {last_ts}</div>
    """, unsafe_allow_html=True)

    # ── Status breakdown ─────────────────────────────────────────────────
    st.markdown("---")
    status_counts = {k: 0 for k in STATUS_OPTIONS}
    for l in lessons:
        k = l.get("status","planned")
        status_counts[k] = status_counts.get(k, 0) + 1
    status_html = '<div class="status-grid">'
    for k, v in STATUS_OPTIONS.items():
        col = STATUS_COLORS[k]
        cnt = status_counts.get(k, 0)
        status_html += (
            f'<div class="status-card" style="background:{col}18;border-color:{col}">'
            f'<div class="s-val" style="color:{col}">{cnt}</div>'
            f'<div class="s-lbl">{v}</div></div>'
        )
    status_html += '</div>'
    st.markdown(status_html, unsafe_allow_html=True)

    # ── Upcoming lessons ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📅 שיעורים קרובים")
    if upcoming:
        for l in sorted(upcoming, key=lambda x: x.get("date_iso",""))[:5]:
            sc    = count_subscribers(l["id"])
            d     = date_display(l.get("date_iso","")) or "—"
            scol  = STATUS_COLORS.get(l.get("status","planned"), "#6b42b8")
            title = l["topic"] + (f' — {l["subtitle"]}' if l.get("subtitle","").strip() else "")
            st.markdown(
                f'<div style="padding:.55rem 1rem;margin-bottom:.35rem;background:white;'
                f'border-radius:10px;border-right:4px solid {scol};'
                f'box-shadow:0 1px 6px rgba(92,61,158,.07)">'
                f'<b style="color:#3d1f7a">שיעור {l["num"]} — {title}</b>'
                f'<br><span style="font-size:.82rem;color:#666">'
                f'📅 {d} &nbsp;·&nbsp; 👩‍🏫 {l.get("teacher","")} &nbsp;·&nbsp; 👥 {sc} נרשמים</span></div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("אין שיעורים קרובים מתוכננים.")

    # ── Recent activity ──────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📋 פעילות אחרונה")
    if log:
        for e in log[:5]:
            lbl = ACTION_LABELS.get(e.get("action",""), e.get("action",""))
            tag = ACTION_TAGS.get(e.get("action",""), "tag-other")
            st.markdown(
                f'`{e.get("timestamp","")}` &nbsp;'
                f'<span class="{tag}">{lbl}</span> &nbsp;'
                f'{e.get("admin_name","")} &nbsp;'
                f'<span style="color:#888">{e.get("details","")}</span>',
                unsafe_allow_html=True,
            )
    else:
        st.info("אין פעילות רשומה עדיין.")


def _email_panel(lesson):
    """Render the email template panel for a lesson."""
    subs = get_subscribers_for_lesson(lesson["id"])
    subject, body = generate_update_email(lesson)
    with st.expander(f"📧 תבנית מייל עדכון — {len(subs)} נמענים", expanded=True):
        st.markdown(f"**נושא:** `{subject}`")
        st.markdown("**גוף המייל — העתק ושלח ידנית:**")
        st.code(body, language=None)
        if subs:
            st.markdown("**נמענים:**")
            st.text("\n".join(s["email"] for s in subs))
        else:
            st.info("אין נרשמים לשיעור זה עדיין.")
        st.info(
            "💡 **לשליחה אוטומטית** יש לחבר ספק אימייל (Mailgun, SendGrid, Gmail SMTP).\n"
            "כרגע ניתן להעתיק את הטקסט ולשלוח ידנית מכל לקוח מייל."
        )
        ep1, ep2, _ = st.columns([1.2, 1, 5])
        if not is_viewer() and ep1.button("✅ סמן כנשלח", key="mark_sent_ep", type="primary"):
            log_action(*actor(), "send_update",
                       f"שליחת עדכון ל-{len(subs)} נרשמים, שיעור {lesson['num']}")
            st.session_state.show_email_for = None
            st.rerun()
        if ep2.button("❌ סגור", key="close_email_ep"):
            st.session_state.show_email_for = None
            st.rerun()

def tab_lessons():
    # ── Save confirmation ────────────────────────────────────────────────
    if st.session_state.lesson_saved:
        st.success("✅ השיעור נשמר!")
        st.session_state.lesson_saved = False

    # ── Notification banner (after editing with changed fields) ──────────
    if st.session_state.notify_lesson:
        nl      = st.session_state.notify_lesson
        changed = nl.get("changed", [])
        changed_labels = ", ".join(NOTIFY_FIELD_LABELS.get(f, f) for f in changed)
        st.warning(
            f"📬 השיעור עודכן ({changed_labels}). "
            f"לשלוח עדכון ל-**{nl['sub_count']} נרשמים**?"
        )
        nb1, nb2, nb3, _ = st.columns([1.5, 1.5, 1.1, 3])
        if nb1.button("✉️ שלח מייל", type="primary", key="notify_email"):
            st.session_state.show_email_for = nl["lesson"]
            st.session_state.notify_lesson  = None
            st.rerun()
        if nb2.button("💬 הכן וואטסאפ", key="notify_wa"):
            st.session_state.notify_wa_draft = {
                "lesson": nl["lesson"],
                "text":   generate_whatsapp_text(nl["lesson"]),
            }
            st.session_state.notify_lesson = None
            st.rerun()
        if nb3.button("ביטול", key="notify_no"):
            st.session_state.notify_lesson = None
            st.rerun()

    # ── WhatsApp update draft (from notification) ─────────────────────────
    if st.session_state.notify_wa_draft:
        nwd = st.session_state.notify_wa_draft
        with st.expander("💬 הכנת הודעת וואטסאפ לנרשמים", expanded=True):
            wa_txt = st.text_area("ערוך הודעה:", value=nwd["text"], height=250, key="notify_wa_txt")
            nw1, nw2, _ = st.columns([1.5, 1, 4])
            nw1.link_button("💬 פתח בוואטסאפ", whatsapp_url(wa_txt),
                            use_container_width=True, type="primary")
            if nw2.button("❌ סגור", key="notify_wa_close"):
                st.session_state.notify_wa_draft = None
                st.rerun()

    # ── Email template panel ─────────────────────────────────────────────
    if st.session_state.show_email_for:
        _email_panel(st.session_state.show_email_for)

    # ── Lesson form ──────────────────────────────────────────────────────
    if st.session_state.adding_lesson or st.session_state.edit_lesson is not None:
        if is_viewer():
            st.session_state.adding_lesson = False
            st.session_state.edit_lesson   = None
            st.rerun()
        lesson_form(st.session_state.edit_lesson,
                    is_dup=st.session_state.adding_lesson and st.session_state.edit_lesson is not None)
        return

    lessons  = load_lessons()
    _viewer  = is_viewer()

    # ── Filter state initialisation ───────────────────────────────────────
    _FILTER_DEFAULTS = {
        "adv_search": "", "adv_year": "הכל", "adv_month": "הכל",
        "adv_teacher": "הכל", "adv_school": "הכל", "adv_status": "הכל",
        "adv_upcoming": False, "adv_past": False,
        "adv_no_desc": False, "adv_no_zoom": False,
    }
    for _k, _v in _FILTER_DEFAULTS.items():
        if _k not in st.session_state:
            st.session_state[_k] = _v

    # ── Row 1: search + add button ────────────────────────────────────────
    fr1, fr2 = st.columns([3, 1])
    search = fr1.text_input(
        "🔍 חיפוש", key="adv_search",
        placeholder="חפש לפי נושא, מרצה, בית ספר, תאריך, יום, חודש, תיאור, סטטוס...",
    )
    fr2.write("")
    if not _viewer:
        if fr2.button("➕ שיעור חדש", type="primary", use_container_width=True):
            st.session_state.adding_lesson = True; st.session_state.edit_lesson = None; st.rerun()

    # ── Build filter option lists ─────────────────────────────────────────
    _teachers_opts = ["הכל"] + sorted({l.get("teacher","") for l in lessons if l.get("teacher","").strip()})
    _schools_opts  = ["הכל"] + sorted({l.get("org","")     for l in lessons if l.get("org","").strip()})
    _years_opts    = ["הכל"] + sorted(
        {(l.get("date_iso") or "")[:4] for l in lessons if l.get("date_iso")}, reverse=True
    )
    _months_opts   = ["הכל"] + sorted({month_from_iso(l.get("date_iso","")) for l in lessons if l.get("date_iso")})
    _status_opts   = ["הכל"] + list(STATUS_OPTIONS.values())

    # ── Row 2: basic filter dropdowns ─────────────────────────────────────
    ff1, ff2, ff3, ff4, ff5 = st.columns(5)
    flt_year    = ff1.selectbox("שנה",      _years_opts,    key="adv_year",    label_visibility="collapsed")
    flt_month   = ff2.selectbox("חודש",     _months_opts,   key="adv_month",   label_visibility="collapsed")
    flt_teacher = ff3.selectbox("מרצה",     _teachers_opts, key="adv_teacher", label_visibility="collapsed")
    flt_school  = ff4.selectbox("בית ספר",  _schools_opts,  key="adv_school",  label_visibility="collapsed")
    flt_status  = ff5.selectbox("סטטוס",    _status_opts,   key="adv_status",  label_visibility="collapsed")

    # ── Advanced filters expander ─────────────────────────────────────────
    _adv_active = any(
        st.session_state.get(k) for k in ("adv_upcoming", "adv_past", "adv_no_desc", "adv_no_zoom")
    )
    with st.expander(("🔵 " if _adv_active else "") + "סינון מתקדם", expanded=_adv_active):
        ac1, ac2, ac3, ac4 = st.columns(4)
        flt_upcoming = ac1.checkbox("📅 קרובים בלבד",    key="adv_upcoming")
        flt_past     = ac2.checkbox("✅ שהתקיימו בלבד",  key="adv_past")
        flt_no_desc  = ac3.checkbox("⚠️ ללא תיאור",      key="adv_no_desc")
        flt_no_zoom  = ac4.checkbox("⚠️ ללא קישור Zoom", key="adv_no_zoom")

    # ── Clear filters button ──────────────────────────────────────────────
    _any_filter = bool(
        search.strip() or
        flt_year != "הכל" or flt_month != "הכל" or
        flt_teacher != "הכל" or flt_school != "הכל" or flt_status != "הכל" or
        flt_upcoming or flt_past or flt_no_desc or flt_no_zoom
    )
    cl1, _ = st.columns([1, 5])
    if cl1.button("✕ נקה סינון", use_container_width=True, disabled=not _any_filter):
        for _k, _v in _FILTER_DEFAULTS.items():
            st.session_state[_k] = _v
        st.rerun()

    # ── Renumber button + confirmation ────────────────────────────────────
    _, rb = st.columns([5, 2])
    if not _viewer and rb.button("🔢 מספור אוטומטי לפי תאריך", use_container_width=True,
                 help="ממספר מחדש את כל השיעורים לפי סדר כרונולוגי, החל מ-2"):
        st.session_state.confirm_renumber = True; st.rerun()
    if st.session_state.confirm_renumber:
        st.warning("⚠️ פעולה זו תשנה את מספרי כל השיעורים לפי סדר כרונולוגי החל מ-2. להמשיך?")
        rn1, rn2, _ = st.columns([1,1,5])
        if rn1.button("✅ כן, מספר מחדש", type="primary", key="rn_yes"):
            renumber_lessons_by_date(start=2)
            log_action(*actor(), "renumber_lessons", "מספור אוטומטי לפי תאריך")
            st.session_state.confirm_renumber = False
            st.rerun()
        if rn2.button("❌ ביטול", key="rn_no"):
            st.session_state.confirm_renumber = False; st.rerun()

    # ── Apply all filters ─────────────────────────────────────────────────
    from datetime import date as _date
    _today     = _date.today().isoformat()
    rev_status = {v: k for k, v in STATUS_OPTIONS.items()}
    filtered   = lessons

    if search.strip():
        _s = search.strip().lower()
        def _match(l):
            return any(_s in str(v).lower() for v in [
                l.get("topic",""), l.get("subtitle",""), l.get("teacher",""),
                l.get("org",""), l.get("description",""), l.get("process",""),
                l.get("date_iso",""), l.get("day",""),
                month_from_iso(l.get("date_iso","")),
                STATUS_OPTIONS.get(l.get("status","planned"), ""),
            ])
        filtered = [l for l in filtered if _match(l)]

    if flt_year    != "הכל": filtered = [l for l in filtered if (l.get("date_iso") or "").startswith(flt_year)]
    if flt_month   != "הכל": filtered = [l for l in filtered if month_from_iso(l.get("date_iso",""))==flt_month]
    if flt_teacher != "הכל": filtered = [l for l in filtered if l.get("teacher","")==flt_teacher]
    if flt_school  != "הכל": filtered = [l for l in filtered if l.get("org","")==flt_school]
    if flt_status  != "הכל":
        _fk = rev_status.get(flt_status, "")
        filtered = [l for l in filtered if l.get("status","planned")==_fk]

    if flt_upcoming and not flt_past:
        filtered = [l for l in filtered
                    if (l.get("date_iso") or "") >= _today
                    and l.get("status","planned") not in ("cancelled","completed")]
    elif flt_past and not flt_upcoming:
        filtered = [l for l in filtered
                    if (l.get("date_iso") or "") < _today
                    or l.get("status","planned") == "completed"]

    if flt_no_desc: filtered = [l for l in filtered if not l.get("description","").strip()]
    if flt_no_zoom: filtered = [l for l in filtered if not l.get("zoom_link","").strip()]

    # ── Results count ─────────────────────────────────────────────────────
    _total = len(lessons)
    if _any_filter:
        st.markdown(f"נמצאו **{len(filtered)}** שיעורים מתוך {_total}")
    else:
        st.markdown(f"סה״כ **{_total}** שיעורים")
    st.markdown("---")

    for l in filtered:
        d_str     = date_display(l.get("date_iso","")) or "—"
        t_rng     = time_range(l.get("time_start",""), l.get("duration_minutes",120)) if l.get("time_start") else "—"
        month     = month_from_iso(l.get("date_iso","")) or "—"
        sub_count = count_subscribers(l["id"])

        col_info, ce, cd, cdu, cw, cpk, cdel, cg = st.columns([4,.7,.6,.7,.7,.7,.6,.6])
        with col_info:
            sk        = l.get("status","planned")
            scol      = STATUS_COLORS.get(sk,"#6b42b8")
            slbl      = STATUS_OPTIONS.get(sk,"")
            vk        = l.get("visibility","published")
            vcol      = VISIBILITY_COLORS.get(vk,"#1a7f37")
            vlbl      = VISIBILITY_OPTIONS.get(vk,"")
            sub_badge = (
                f' <span style="background:#ede7ff;color:#6b42b8;padding:.1rem .5rem;'
                f'border-radius:12px;font-size:.7rem">👥 {sub_count}</span>'
                if sub_count else ""
            )
            stat_badge = (
                f'<span style="background:{scol}18;color:{scol};padding:.1rem .5rem;'
                f'border-radius:10px;font-size:.7rem;font-weight:600;margin-left:.3rem">{slbl}</span>'
            )
            vis_badge = (
                f'<span style="background:{vcol}18;color:{vcol};padding:.1rem .5rem;'
                f'border-radius:10px;font-size:.7rem;font-weight:600;margin-left:.3rem">{vlbl}</span>'
            )
            st.markdown(f"""<div class="lesson-row">
              <div class="lrow-title">שיעור {l['num']} &mdash; {l['topic']}{sub_badge}{stat_badge}{vis_badge}</div>
              <div class="lrow-meta">📅 {d_str} {l.get('day','')} {t_rng} &nbsp;|&nbsp; 👩‍🏫 {l['teacher']} &nbsp;|&nbsp; {month}</div>
            </div>""", unsafe_allow_html=True)
        with ce:
            st.write("")
            if not _viewer and st.button("✏️", key=f"ed_{l['id']}", help="עריכה", use_container_width=True):
                st.session_state.edit_lesson = l; st.session_state.adding_lesson = False; st.rerun()
        with cd:
            st.write("")
            if not _viewer and st.button("📋", key=f"dp_{l['id']}", help="שכפול", use_container_width=True):
                dup = copy.deepcopy(l)
                dup["id"]           = str(uuid.uuid4())
                dup["num"]          = max((x["num"] for x in lessons), default=0) + 1
                dup["topic"]        = f"[עותק] {dup['topic']}"
                dup["date_iso"]     = None
                dup["day"]          = ""
                dup["time_start"]   = "18:00"
                dup["visibility"]   = "draft"
                st.session_state.edit_lesson   = dup
                st.session_state.adding_lesson = True
                log_action(*actor(), "duplicate_lesson", f"שכפול שיעור {l['num']}: {l['topic']}")
                st.rerun()
        with cdu:
            st.write("")
            gurl = google_url(l)
            if gurl: st.link_button("🗓️", gurl, help="פתח ביומן", use_container_width=True)
        with cw:
            st.write("")
            if st.button("💬", key=f"wa_{l['id']}", help="שתף בוואטסאפ", use_container_width=True):
                current = st.session_state.whatsapp_draft
                if current and current.get("id") == l["id"]:
                    st.session_state.whatsapp_draft = None
                else:
                    st.session_state.whatsapp_draft = {"id": l["id"], "text": generate_whatsapp_text(l)}
                st.rerun()
        with cpk:
            st.write("")
            if st.button("📦", key=f"pk_{l['id']}", help="ערכת פרסום", use_container_width=True):
                st.session_state.pubkit_open = (
                    None if st.session_state.pubkit_open == l["id"] else l["id"]
                )
                st.rerun()
        with cdel:
            st.write("")
            if not _viewer and st.button("🗑️", key=f"dl_{l['id']}", help="מחיקה", use_container_width=True):
                st.session_state.confirm_delete = l["id"]; st.rerun()
        with cg:
            st.write("")
            lbl = f"👥 {sub_count}" if sub_count else "👥"
            if st.button(lbl, key=f"vs_{l['id']}", help="נרשמים לעדכונים", use_container_width=True):
                st.session_state.view_subs_lesson = (
                    None if st.session_state.view_subs_lesson == l["id"] else l["id"]
                )
                st.rerun()

        # ── WhatsApp draft panel ─────────────────────────────────────────
        if st.session_state.whatsapp_draft and st.session_state.whatsapp_draft.get("id") == l["id"]:
            draft = st.session_state.whatsapp_draft
            with st.expander("💬 עריכת הודעת וואטסאפ לפני שליחה", expanded=True):
                txt_col, img_col = st.columns([1.1, 1])
                with txt_col:
                    edited = st.text_area("טקסט ההודעה:", value=draft["text"],
                                          height=260, key=f"wa_edit_{l['id']}",
                                          label_visibility="collapsed")
                with img_col:
                    st.caption("תמונה (אופציונלי) — העתק ללוח ואז הדבק בוואטסאפ")
                    components.html("""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:sans-serif;direction:rtl;background:transparent;padding:2px}
#zone{border:2px dashed #9b6fd4;border-radius:12px;padding:10px;text-align:center;
  color:#777;font-size:12px;background:white;min-height:190px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:7px;
  transition:border-color .2s,background .2s}
#zone.over{border-color:#3d1f7a;background:#f0eaff}
#zone.ok{border-color:#9b6fd4;border-style:solid}
#preview{max-width:100%;max-height:110px;border-radius:8px;display:none;object-fit:contain}
#browse{background:linear-gradient(135deg,#5c3d9e,#9b6fd4);color:white;border:none;
  border-radius:20px;padding:4px 13px;font-size:12px;cursor:pointer}
#fi{display:none}
#copy-btn{background:#1a7f37;color:white;border:none;border-radius:20px;
  padding:4px 13px;font-size:12px;cursor:pointer;display:none}
#status{font-size:11px;color:#555;line-height:1.4;text-align:center}
</style></head><body>
<div id="zone">
  <div id="status">גרור תמונה לכאן<br><b>Ctrl+V</b> להדבקה מהלוח</div>
  <button id="browse" onclick="document.getElementById('fi').click()">בחר מהגלריה</button>
  <input type="file" id="fi" accept="image/*">
  <img id="preview">
  <button id="copy-btn" onclick="doCopy()">העתק תמונה ללוח</button>
</div>
<script>
var _blob=null;
function loadBlob(blob){
  _blob=blob;
  var url=URL.createObjectURL(blob);
  var p=document.getElementById('preview');
  p.onload=function(){
    document.getElementById('zone').classList.add('ok');
    document.getElementById('copy-btn').style.display='inline-block';
    document.getElementById('status').innerHTML='לחץ <b>העתק תמונה ללוח</b><br>ואז הדבק בוואטסאפ (Ctrl+V)';
  };
  p.src=url; p.style.display='block';
}
async function doCopy(){
  if(!_blob)return;
  var btn=document.getElementById('copy-btn'),st=document.getElementById('status');
  try{
    var img=document.getElementById('preview');
    var c=document.createElement('canvas');
    c.width=img.naturalWidth;c.height=img.naturalHeight;
    c.getContext('2d').drawImage(img,0,0);
    var pngBlob=await new Promise(function(res){c.toBlob(res,'image/png');});
    var clip=navigator.clipboard||parent.navigator.clipboard;
    await clip.write([new ClipboardItem({'image/png':pngBlob})]);
    btn.textContent='הועתק!'; btn.style.background='#0550ae';
    st.innerHTML='<b style="color:#1a7f37">התמונה בלוח!</b><br>פתח וואטסאפ ← הדבק (Ctrl+V)';
  }catch(e){
    st.innerHTML='לחץ ימני על התמונה<br>← "העתק תמונה"';
    btn.style.background='#cf222e';
  }
}
document.getElementById('fi').onchange=function(e){
  var f=e.target.files[0];if(f)loadBlob(f);
};
var z=document.getElementById('zone');
z.addEventListener('dragover',function(e){e.preventDefault();z.classList.add('over')});
z.addEventListener('dragleave',function(){z.classList.remove('over')});
z.addEventListener('drop',function(e){
  e.preventDefault();z.classList.remove('over');
  var f=e.dataTransfer.files[0];
  if(f&&f.type.startsWith('image/'))loadBlob(f);
});
document.addEventListener('paste',function(e){
  var items=(e.clipboardData||e.originalEvent.clipboardData).items;
  for(var i=0;i<items.length;i++){
    if(items[i].type.startsWith('image/')){loadBlob(items[i].getAsFile());break;}
  }
});
</script></body></html>""", height=270, scrolling=False)
                wc1, wc2, _ = st.columns([1.8, 1, 4])
                wc1.link_button("💬 פתח בוואטסאפ", whatsapp_url(edited),
                                use_container_width=True, type="primary")
                if wc2.button("❌ סגור", key=f"wa_close_{l['id']}", use_container_width=True):
                    st.session_state.whatsapp_draft = None
                    st.rerun()

        # ── Publishing Kit panel ─────────────────────────────────────────
        if st.session_state.pubkit_open == l["id"]:
            render_pubkit(l)

        # ── Subscriber panel ─────────────────────────────────────────────
        if st.session_state.view_subs_lesson == l["id"]:
            subs = get_subscribers_for_lesson(l["id"])
            with st.expander(f"👥 נרשמים לשיעור {l['num']} — {len(subs)} נרשמים", expanded=True):
                if subs:
                    for s in subs:
                        st.text(f"📧 {s['email']}  ·  {s['subscribed_at'][:10]}")
                else:
                    st.info("אין נרשמים לשיעור זה עדיין.")
                vs1, vs2, vs3 = st.columns(3)
                if not _viewer and vs1.button("📧 שלח עדכון", key=f"send_u_{l['id']}", use_container_width=True):
                    st.session_state.show_email_for   = l
                    st.session_state.view_subs_lesson = None
                    st.rerun()
                if subs:
                    csv_data = export_subscribers_csv_for_lesson(l["id"], l["num"])
                    vs2.download_button(
                        "📊 ייצא CSV", csv_data,
                        file_name=f"נרשמים_שיעור_{l['num']}.csv",
                        mime="text/csv", key=f"exp_subs_{l['id']}",
                        use_container_width=True,
                    )
                if vs3.button("❌ סגור", key=f"closesub_{l['id']}", use_container_width=True):
                    st.session_state.view_subs_lesson = None
                    st.rerun()

        # ── Confirm delete ───────────────────────────────────────────────
        if not _viewer and st.session_state.confirm_delete == l["id"]:
            st.warning(f"⚠️ למחוק את שיעור {l['num']} — **{l['topic']}**?")
            cy, cn, _ = st.columns([1,1,5])
            if cy.button("✅ כן, מחק", key=f"cy_{l['id']}", type="primary"):
                updated = [x for x in lessons if x["id"]!=l["id"]]
                save_lessons(updated)
                log_action(*actor(), "delete_lesson", f"מחיקת שיעור {l['num']}: {l['topic']}")
                st.session_state.confirm_delete = None
                st.success("השיעור נמחק"); st.rerun()
            if cn.button("❌ ביטול", key=f"cn_{l['id']}"):
                st.session_state.confirm_delete = None; st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — ADMINS
# ════════════════════════════════════════════════════════════════════════════
def tab_admins():
    config    = load_config()
    is_super  = next((a.get("is_super_admin") for a in config["admins"]
                      if a["email"]==st.session_state.admin_email), False)
    if not is_super:
        st.info("רק מנהל ראשי יכול לנהל מנהלים."); return

    admins = get_all_admins()
    col_add, _ = st.columns([2,6])
    if col_add.button("➕ הוסף מנהל", type="primary"):
        st.session_state.adding_admin = True; st.session_state.edit_admin = None; st.rerun()

    if st.session_state.adding_admin or st.session_state.edit_admin is not None:
        if is_viewer():
            st.session_state.adding_admin = False
            st.session_state.edit_admin   = None
            st.rerun()
        admin_form(st.session_state.edit_admin); return

    st.markdown("---")
    for a in admins:
        ca, cb, cc, cd = st.columns([3.5,1,1,1])
        with ca:
            badge  = '<span class="admin-badge">סופר מנהל</span>' if a.get("is_super_admin") else ""
            vbadge = '<span class="viewer-badge">צופה בלבד</span>' if a.get("role") == "viewer" else ""
            st.markdown(f"**{a['full_name']}** {badge}{vbadge}  \n`{a['email']}`  \n"
                        f"<span style='font-size:.78rem;color:#888'>נוצר: {a.get('created_at','')[:10]}</span>",
                        unsafe_allow_html=True)
        with cb:
            if st.button("✏️ ערוך", key=f"ea_{a['id']}", use_container_width=True):
                st.session_state.edit_admin = a; st.session_state.adding_admin = False; st.rerun()
        with cc:
            if st.button("🔑 איפוס", key=f"rst_{a['id']}", use_container_width=True):
                token = set_reset_token(a["email"])
                reset_url = f"http://localhost:8501/admin?reset={token}"
                st.info(f"קישור איפוס (בתוקף שעה אחת):  \n`{reset_url}`")
                log_action(*actor(), "reset_password", f"איפוס סיסמה עבור {a['email']}")
        with cd:
            is_me = a["email"] == st.session_state.admin_email
            if not is_me:
                if st.button("🗑️ מחק", key=f"da_{a['id']}", use_container_width=True):
                    st.session_state.confirm_del_admin = a["id"]; st.rerun()
            else:
                st.caption("(אתה)")

        if st.session_state.confirm_del_admin == a["id"]:
            st.warning(f"⚠️ למחוק את המנהל **{a['full_name']}** ({a['email']})?")
            dy, dn, _ = st.columns([1,1,5])
            if dy.button("✅ כן, מחק", key=f"day_{a['id']}", type="primary"):
                delete_admin_by_id(a["id"])
                log_action(*actor(), "delete_admin", f"מחיקת מנהל {a['email']}")
                st.session_state.confirm_del_admin = None; st.rerun()
            if dn.button("❌ ביטול", key=f"dan_{a['id']}"):
                st.session_state.confirm_del_admin = None; st.rerun()
        st.markdown("---")

def admin_form(existing=None):
    is_new = existing is None
    st.markdown(f"### {'➕ מנהל חדש' if is_new else '✏️ עריכת מנהל'}")
    a1, a2 = st.columns(2)
    full_name  = a1.text_input("שם מלא *",   value=existing.get("full_name","") if existing else "")
    email      = a2.text_input("אימייל *",    value=existing.get("email","")     if existing else "",
                                disabled=not is_new)
    is_super   = st.checkbox("מנהל ראשי (יכול לנהל מנהלים אחרים)",
                              value=existing.get("is_super_admin",False) if existing else False)
    role_opts  = ["admin", "viewer"]
    role       = st.selectbox(
        "תפקיד",
        role_opts,
        index=role_opts.index(existing.get("role","admin")) if existing else 0,
        format_func=lambda r: "מנהל — גישה מלאה לכתיבה" if r == "admin" else "צופה — קריאה בלבד",
    )
    if is_new:
        p1, p2 = st.columns(2)
        pw1 = p1.text_input("סיסמה *",         type="password")
        pw2 = p2.text_input("אימות סיסמה *",   type="password")
    else:
        pw1 = pw2 = None

    cs, cc, _ = st.columns([1,1,5])
    if cs.button("💾 שמור", type="primary", use_container_width=True):
        errors = []
        if not full_name.strip(): errors.append("שם מלא הוא שדה חובה")
        if not email.strip():     errors.append("אימייל הוא שדה חובה")
        if is_new:
            if not pw1:            errors.append("סיסמה היא שדה חובה")
            elif len(pw1) < 6:     errors.append("הסיסמה חייבת להכיל לפחות 6 תווים")
            elif pw1 != pw2:       errors.append("הסיסמאות אינן תואמות")
            elif get_admin_by_email(email): errors.append("מנהל עם אימייל זה כבר קיים")
        for e in errors: st.error(f"❌ {e}")
        if not errors:
            if is_new:
                new_admin = {
                    "id": str(uuid.uuid4()), "email": email.strip(),
                    "full_name": full_name.strip(), "is_super_admin": is_super,
                    "role": role,
                    "password_hash": bcrypt.hashpw(pw1.encode(), bcrypt.gensalt(12)).decode(),
                    "created_at": datetime.now().isoformat(),
                    "reset_token": None, "reset_expires": None,
                }
                upsert_admin(new_admin)
                log_action(*actor(), "add_admin", f"הוספת מנהל {email} (תפקיד: {role})")
            else:
                existing["full_name"]      = full_name.strip()
                existing["is_super_admin"] = is_super
                existing["role"]           = role
                upsert_admin(existing)
                log_action(*actor(), "edit_admin", f"עריכת מנהל {existing['email']} (תפקיד: {role})")
            st.session_state.edit_admin = None; st.session_state.adding_admin = False
            st.success("✅ המנהל נשמר"); st.rerun()
    if cc.button("ביטול", use_container_width=True):
        st.session_state.edit_admin = None; st.session_state.adding_admin = False; st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — ACTIVITY LOG
# ════════════════════════════════════════════════════════════════════════════
ACTION_LABELS = {
    "login":"כניסה","logout":"יציאה","add_lesson":"הוספת שיעור","edit_lesson":"עריכת שיעור",
    "delete_lesson":"מחיקת שיעור","duplicate_lesson":"שכפול שיעור",
    "add_admin":"הוספת מנהל","edit_admin":"עריכת מנהל","delete_admin":"מחיקת מנהל",
    "change_password":"שינוי סיסמה","reset_password":"איפוס סיסמה",
    "restore_backup":"שחזור גיבוי","import_lessons":"ייבוא שיעורים",
    "send_update":"שליחת עדכון לנרשמים",
}
ACTION_TAGS = {
    "login":"tag-login","logout":"tag-login",
    "add_lesson":"tag-add","add_admin":"tag-add",
    "edit_lesson":"tag-edit","edit_admin":"tag-edit",
    "duplicate_lesson":"tag-edit","change_password":"tag-edit","reset_password":"tag-edit",
    "delete_lesson":"tag-delete","delete_admin":"tag-delete",
    "send_update":"tag-other",
}

def tab_log():
    log = load_log()
    st.markdown(f"**{len(log)} רשומות** (100 האחרונות מוצגות)")
    ls, la = st.columns([2,2])
    search_log   = ls.text_input("🔍", placeholder="חפש בלוג...", label_visibility="collapsed")
    filter_action = la.selectbox("סוג פעולה", ["הכל"]+list(ACTION_LABELS.values()), label_visibility="collapsed")

    rev_labels = {v:k for k,v in ACTION_LABELS.items()}
    filtered   = log
    if search_log:
        s = search_log.lower()
        filtered = [e for e in filtered if s in e.get("admin_name","").lower() or
                    s in e.get("details","").lower() or s in e.get("action","").lower()]
    if filter_action != "הכל":
        key = rev_labels.get(filter_action, filter_action)
        filtered = [e for e in filtered if e.get("action")==key]

    filtered = filtered[:100]
    rows = "".join(
        '<div class="log-row">'
        f'<b>{e.get("timestamp","")}</b> &nbsp;'
        f'<span class="{ACTION_TAGS.get(e.get("action",""), "tag-other")}">'
        f'{ACTION_LABELS.get(e.get("action",""), e.get("action",""))}</span> &nbsp;'
        f'{e.get("admin_name","")} &nbsp; <span style="color:#888">{e.get("details","")}</span>'
        '</div>'
        for e in filtered
    )
    st.markdown(f'<div class="log-scroll">{rows}</div>', unsafe_allow_html=True)
    if not filtered: st.info("אין רשומות")

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — BACKUP & EXPORT
# ════════════════════════════════════════════════════════════════════════════
def tab_backup():
    _viewer = is_viewer()
    st.markdown("### 💾 גיבויים")
    backups = list_backups()
    if backups:
        b_labels = [f"{b['label']} ({b['count']} שיעורים)" for b in backups]
        sel = st.selectbox("בחר גיבוי", b_labels)
        sel_idx = b_labels.index(sel)
        sel_bk  = backups[sel_idx]
        rc, dc, _ = st.columns([1.2,1.5,5])
        if not _viewer and rc.button("♻️ שחזר גיבוי זה", type="primary"):
            n = restore_backup(sel_bk["filename"])
            log_action(*actor(), "restore_backup", f"שחזור מ-{sel_bk['label']} ({n} שיעורים)")
            st.success(f"✅ שוחזרו {n} שיעורים"); st.rerun()
        with open(sel_bk["path"], "rb") as f:
            dc.download_button("⬇️ הורד גיבוי זה", f.read(),
                               file_name=sel_bk["filename"], mime="application/json")
    else:
        st.info("אין גיבויים עדיין. גיבוי נוצר אוטומטית לפני כל שינוי.")

    st.markdown("---")
    st.markdown("### 📤 ייצוא")
    e1, e2, e3 = st.columns(3)
    e1.download_button("📄 ייצא JSON", data=export_json(), file_name="lessons_export.json", mime="application/json")
    e2.download_button("📊 ייצא CSV",  data=export_csv(),  file_name="lessons_export.csv",  mime="text/csv")
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as raw:
            e3.download_button("📦 הורד קובץ נתונים", raw.read(), file_name="lessons_data.json", mime="application/json")

    st.markdown("---")
    st.markdown("### 👥 נרשמים לעדכונים")
    all_subs = load_subscribers()
    st.markdown(f"סה\"כ **{len(all_subs)}** נרשמים בכל השיעורים.")
    if all_subs:
        st.download_button("📊 ייצא כל הנרשמים (CSV)", export_all_subscribers_csv(),
                           file_name="כל_הנרשמים.csv", mime="text/csv")

    if not _viewer:
        st.markdown("---")
        st.markdown("### 📥 ייבוא")
    if not _viewer and (uploaded := st.file_uploader("העלה קובץ JSON", type=["json"])):
        imp1, imp2 = st.columns([1,1])
        if imp1.button("✅ החלף את כל השיעורים", type="primary"):
            try:
                data = import_json(uploaded.getvalue())
                save_lessons(data)
                log_action(*actor(), "import_lessons", f"ייבוא {len(data)} שיעורים (החלפה)")
                st.success(f"✅ יובאו {len(data)} שיעורים"); st.rerun()
            except Exception as e:
                st.error(f"❌ שגיאת ייבוא: {e}")

# ════════════════════════════════════════════════════════════════════════════
# TAB — SETTINGS
# ════════════════════════════════════════════════════════════════════════════
def tab_settings():
    st.markdown("### ⚙️ הגדרות")
    if is_viewer():
        st.info("👁️ גישת צופה — אין הרשאה לשינוי הגדרות.")
        return
    config = load_config()
    sub_enabled = config.get("subscription_enabled", False)

    st.markdown("#### 📋 איסוף פרטי גולשים")
    new_val = st.toggle("אפשר איסוף פרטים לעדכונים", value=sub_enabled)

    if new_val:
        st.info("**פעיל** — טופס ההרשמה (שם, מייל, הסכמה) מוצג בדף הציבורי. פרטי גולשים נאספים.")
    else:
        st.info("**כבוי** — בדף הציבורי מוצגות רק אפשרויות הוספה ליומן. לא נאספים פרטים אישיים.")

    if new_val != sub_enabled:
        config["subscription_enabled"] = new_val
        save_config(config)
        log_action(*actor(), "update_settings",
                   f"שינוי הגדרת איסוף פרטים: {'פעיל' if new_val else 'כבוי'}")
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🔢 טווח שיעורים להצגה בדף הציבורי")
    st.caption("אפשר לבחור להציג רק שיעורים בטווח מסוים. השאר ריק להצגת כל השיעורים.")

    from_val = config.get("display_from_lesson")
    to_val   = config.get("display_to_lesson")

    col_from, col_to = st.columns(2)
    with col_from:
        new_from_raw = st.number_input(
            "מ שיעור מספר", min_value=1, max_value=999,
            value=int(from_val) if from_val is not None else 1,
            step=1, key="set_from_lesson",
        )
        use_from = st.checkbox("הפעל גבול תחתון", value=from_val is not None, key="chk_from")
    with col_to:
        new_to_raw = st.number_input(
            "עד שיעור מספר", min_value=1, max_value=999,
            value=int(to_val) if to_val is not None else 20,
            step=1, key="set_to_lesson",
        )
        use_to = st.checkbox("הפעל גבול עליון", value=to_val is not None, key="chk_to")

    new_from = int(new_from_raw) if use_from else None
    new_to   = int(new_to_raw)   if use_to   else None

    if new_from is not None and new_to is not None and new_from > new_to:
        st.warning("גבול תחתון גדול מהגבול העליון — בדוק את הערכים.")
    else:
        if new_from != from_val or new_to != to_val:
            config["display_from_lesson"] = new_from
            config["display_to_lesson"]   = new_to
            save_config(config)
            log_action(*actor(), "update_settings",
                       f"שינוי טווח שיעורים: {new_from or 'ללא הגבלה'} – {new_to or 'ללא הגבלה'}")
            st.rerun()

    if new_from is not None or new_to is not None:
        parts = []
        if new_from is not None: parts.append(f"מ שיעור {new_from}")
        if new_to   is not None: parts.append(f"עד שיעור {new_to}")
        st.info(f"**פעיל** — הדף הציבורי מציג שיעורים {' '.join(parts)}.")
    else:
        st.info("**כל השיעורים** — אין סינון לפי מספר שיעור.")

# ════════════════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ════════════════════════════════════════════════════════════════════════════
def login_page():
    # Check for password reset token in URL
    reset_token = st.query_params.get("reset", None)
    if reset_token:
        reset_page(reset_token); return

    st.markdown('<div class="login-marker"></div>', unsafe_allow_html=True)

    now    = datetime.now()
    locked = st.session_state.locked_until and now < st.session_state.locked_until
    if locked:
        mins = int((st.session_state.locked_until - now).total_seconds()/60)+1
        st.error(f"החשבון נעול. נסי שוב בעוד {mins} דקות.")
        return

    st.markdown("## 🔐 כניסת מנהל")
    email    = st.text_input("אימייל")
    password = st.text_input("סיסמה", type="password")

    if st.button("כניסה", type="primary", use_container_width=True):
        _do_login(email, password)

    if st.button("שכחתי סיסמה", use_container_width=True):
        st.session_state["_forgot_mode"] = True; st.rerun()

    if st.session_state.get("_forgot_mode"):
        forgot_password_section()

def _do_login(email, password):
    config = load_config()
    admin  = next((a for a in config["admins"] if a["email"]==email), None)
    if admin and bcrypt.checkpw(password.encode(), admin["password_hash"].encode()):
        st.session_state.logged_in   = True
        st.session_state.admin_email = email
        st.session_state.admin_name  = admin.get("full_name", email)
        st.session_state.login_attempts = 0
        log_action(email, admin.get("full_name",""), "login", "כניסה מוצלחת")
        st.rerun()
    else:
        st.session_state.login_attempts += 1
        left = config.get("max_attempts",5) - st.session_state.login_attempts
        if left <= 0:
            from datetime import timedelta
            st.session_state.locked_until = datetime.now() + timedelta(minutes=config.get("lockout_minutes",15))
            st.error("יותר מדי ניסיונות — החשבון נעול ל-15 דקות.")
        else:
            st.error(f"פרטי כניסה שגויים. נותרו {left} ניסיונות.")

def forgot_password_section():
    st.markdown("---")
    st.markdown("#### 🔑 איפוס סיסמה")
    fe = st.text_input("הזיני את האימייל שלך", key="fp_email")
    if st.button("שלח קישור איפוס", key="fp_btn"):
        admin = get_admin_by_email(fe)
        if admin:
            token     = set_reset_token(fe)
            reset_url = f"http://localhost:8501/admin?reset={token}"
            st.success("קישור האיפוס נוצר:")
            st.code(reset_url)
            st.caption("הקישור בתוקף לשעה אחת. בסביבת ייצור — קישור זה יישלח למייל.")
        else:
            st.info("אם האימייל קיים במערכת, ישלח קישור איפוס.")  # don't reveal existence

def reset_page(token):
    admin = verify_reset_token(token)
    if not admin:
        st.error("קישור האיפוס לא תקין או פג תוקף."); return
    st.markdown(f"## 🔑 איפוס סיסמה — {admin['full_name']}")
    np1 = st.text_input("סיסמה חדשה",    type="password", key="rp1")
    np2 = st.text_input("אימות סיסמה",   type="password", key="rp2")
    if st.button("עדכן סיסמה", type="primary"):
        if len(np1) < 6:   st.error("הסיסמה חייבת להכיל לפחות 6 תווים")
        elif np1 != np2:   st.error("הסיסמאות אינן תואמות")
        else:
            admin["password_hash"] = bcrypt.hashpw(np1.encode(), bcrypt.gensalt(12)).decode()
            clear_reset_token(admin["email"])
            upsert_admin(admin)
            log_action(admin["email"], admin["full_name"], "change_password", "איפוס סיסמה דרך קישור")
            st.success("✅ הסיסמה עודכנה! ניתן להתחבר.")
            st.query_params.clear()
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    login_page()
else:
    render_sidebar()
    if st.session_state.show_change_pw:
        change_password_panel()

    st.markdown("## 🛡️ ממשק ניהול — שיעורים פתוחים")
    t0, t1, t2, t3, t4, t5, t6 = st.tabs([
        "📊 סקירה", "📚 שיעורים", "📣 תקשורת", "👥 מנהלים",
        "📋 יומן פעילות", "💾 גיבויים וייצוא", "⚙️ הגדרות",
    ])
    with t0: tab_dashboard()
    with t1: tab_lessons()
    with t2: tab_communication()
    with t3: tab_admins()
    with t4: tab_log()
    with t5: tab_backup()
    with t6: tab_settings()

st.markdown("""
<div style="text-align:center;direction:rtl;margin-top:3rem;padding:1rem;
  border-top:1px solid #ede7ff;font-size:.8rem;color:#b0a8c8">
  &copy; לשכת ה־NLP הישראלית &nbsp;|&nbsp;
  <a href="/admin" style="color:#9b6fd4;text-decoration:none">כניסת מנהלים</a>
</div>
""", unsafe_allow_html=True)
