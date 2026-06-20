# Changelog — שיעור פתוח (Open Lessons)
### Israeli NLP Association

---

## [Current] — June 2026

### Phase 4 — Admin Security & Maintenance
- **Role-based access control** — Added Admin and Viewer roles to the admin user system. Viewers can see all data but cannot add, edit, delete, or restore anything. Two-layer enforcement: buttons hidden in the UI + server-side guard on session state.
- **Role field migration** — Existing admin accounts automatically receive `role: "admin"` on first load via `_migrate_config()`
- **Role visible in sidebar** — Viewer accounts display a "צופה בלבד" badge in the admin sidebar and in the admin list
- **Role selectable in admin form** — Dropdown (מנהל / צופה) when adding or editing admin accounts; role is recorded in the activity log
- **Session state guard** — Even if a viewer's session state contains edit flags (e.g., from a role change mid-session), the lesson form and admin form are blocked and reset automatically
- **PROJECT_DOCUMENTATION.md** — Full project documentation created (this file's companion)
- **CHANGELOG.md** — Milestone history file created

---

## Phase 3 — Public UI Fixes & Settings

### Lesson display range setting
- Added **display_from_lesson** and **display_to_lesson** settings in the admin Settings tab
- Admins can restrict the public page to show only lessons within a specified number range
- Settings stored in `admin_config.json` with automatic migration
- Filter applied before all other public-page filters

### Past lessons section — full rebuild
- Replaced `st.expander()` with a `st.button` + `st.session_state` toggle to eliminate the "keyboard_arrow_down" ligature bug caused by the global Heebo font override breaking Streamlit's internal Material Icons rendering
- Past lesson cards rebuilt with a clean `.lc-past` CSS class instead of scattered inline styles
- Fixed flex-wrap issue that caused lesson title and badges to overlap on narrow screens
- Added guard for empty `process` field (no longer renders empty emoji)
- Toggle button styled as a section header (light purple, rounded border)

### Subscription toggle
- Added **אפשר איסוף פרטים לעדכונים** toggle in admin Settings tab (default: OFF)
- When OFF: public page shows only calendar links, no personal data collected
- When ON: subscription form (name, email, consent) is shown on the public page
- Subscriber code preserved and fully functional — only the display is toggled

---

## Phase 2 — Admin Panel Enhancements

### Advanced search and filtering (admin lessons tab)
- Free-text search across 10 fields: topic, subtitle, teacher, org, school, description, process, date, day, month, status label
- 5 filter dropdowns: year, month, teacher, school, status
- Advanced checkboxes expander: upcoming only, past only, missing description, missing Zoom link
- Clear filters button (active only when a filter is applied)
- Results count display: "נמצאו X שיעורים מתוך Y" when filtered, "סה״כ Y שיעורים" otherwise
- All filter state persisted in `st.session_state` with stable keys

### Settings tab
- Added 7th tab "⚙️ הגדרות" to the admin panel
- Subscription toggle control
- Lesson display range control (added in Phase 3)

### Activity log viewer
- Color-coded action type tags (green = add, blue = edit, red = delete, purple = login)
- Free-text search and action type filter
- Shows 100 most recent filtered entries

---

## Phase 1 — Core System

### Project initialization and setup
- `setup_admin.py` — one-time script to create admin config and initial lesson data
- `utils.py` — shared data layer with all file paths relative to module location
- `app.py` — public-facing Streamlit page with RTL Hebrew layout
- `pages/admin.py` — admin panel with bcrypt authentication

### Public page features
- Lesson cards with topic, teacher, date/time, process, status badges, month badges
- Upcoming lessons sorted chronologically
- Past lessons section (collapsible)
- Calendar links: Google Calendar, Apple Calendar (.ics download), Outlook
- Hover-expand description on upcoming lesson cards
- Search bar (topic, teacher, school, process, description)
- Logo display (embedded as base64)
- RTL layout with Heebo font from Google Fonts
- Footer with admin link

### Admin panel features
- Email + password login with bcrypt
- Brute-force lockout (configurable attempts and lockout duration)
- Password reset via token (displayed on-screen for local use)
- Personal password change
- Dashboard tab: metrics, upcoming lessons, recent activity
- Lessons tab: full CRUD (add, edit, delete, duplicate), lesson form with all fields
- Lesson fields: number, date, day, time, duration, topic, subtitle, description, status, visibility, teacher, org, process, Zoom link, registration link, recording link, files link
- Visibility system: published, draft, hidden
- Status system: planned, open (registration), postponed, cancelled, completed
- Auto-renumber by date
- Duplicate lesson (creates draft copy)
- Communication tab: WhatsApp message generator, email template generator, publishing kit per lesson
- Subscribers panel per lesson with CSV export
- Admins tab: add/edit/delete admins, super-admin flag
- Activity log tab
- Backups & Export tab: auto-backup, restore, JSON export, CSV export, subscriber CSV export, JSON import
- Auto-backup before every save/restore/import

### Subscriber system
- Visitor registration with first name, last name, email, consent checkbox
- Subscribers stored per-lesson in `subscribers.json`
- Email update template generated per lesson
- WhatsApp update template generated per lesson
- "Mark as sent" action logged in activity log
- CSV export per lesson and all-subscribers CSV export

### Path and launcher fixes
- All file paths in `utils.py` use `os.path.dirname(os.path.abspath(__file__))` — no hardcoded paths
- `הפעל.bat` uses `%~dp0` to resolve the project directory independently of the Windows working directory
- Project successfully moved to OneDrive with no path changes required in code

### Project file organization
- Project consolidated from original working directory into dedicated OneDrive folder
- Legacy files retained for reference: `lessons.py`, `generate_cal_links.py`, `process_logo.py`, `process_logo2.py`
- `strategic_review.md` — internal product, architecture, and UX review document

---

## Notes

- All JSON data files (`lessons_data.json`, `admin_config.json`, `subscribers.json`, `activity_log.json`) are excluded from this changelog — they contain live data, not code milestones.
- Backup files in `backups/` are auto-managed by the application.
- The public website URL (`https://shiur-patuach.netlify.app`) is defined in `utils.py` but the site is currently running locally only.
