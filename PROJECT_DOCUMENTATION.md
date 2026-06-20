# Project Documentation — שיעור פתוח (Open Lessons)
### Israeli NLP Association

---

## 1. Project Overview

### Purpose
A web application that manages and publishes the annual calendar of open volunteer lessons ("שיעורים פתוחים") organized by the Israeli NLP Association. The system serves as both a public-facing event calendar for members and an internal management tool for coordinators.

### Main Features
- **Public calendar page** — displays upcoming and past lessons with dates, teachers, topics, and calendar links
- **Admin panel** — full lesson management (add, edit, delete, duplicate, reorder)
- **Subscriber management** — visitors can register to receive lesson updates
- **Communication center** — generate WhatsApp messages and email templates for updates
- **Activity log** — full audit trail of every admin action
- **Role-based access** — Admin (full access) and Viewer (read-only) roles
- **Backup system** — automatic backup before every data change, with restore capability
- **Export** — lessons to JSON/CSV, subscribers to CSV

### Target Users
| User | Description |
|---|---|
| General public / NLP members | View lesson calendar, add to calendar, register for updates |
| Admin | Full management of lessons, admins, settings, communication |
| Viewer | Read-only access to admin panel (no write permissions) |

---

## 2. Project Structure

```
פרויקט שיעור פתוח - לשכת ה NLP/
│
├── app.py                    ← Public-facing website (main entry point)
├── utils.py                  ← Shared data layer and business logic
│
├── pages/
│   └── admin.py              ← Admin panel (password-protected)
│
├── lessons_data.json         ← All lesson records (live data)
├── admin_config.json         ← Admin accounts, settings, login config
├── subscribers.json          ← Subscriber list (names, emails, consent)
├── activity_log.json         ← Audit log of all admin actions
│
├── backups/                  ← Auto-generated lesson backups (JSON files)
│   └── lessons_YYYYMMDD_HHMMSS.json
│
├── .streamlit/
│   └── config.toml           ← Streamlit server configuration
│
├── logo_nlp.png              ← Association logo displayed in the public header
│
├── setup_admin.py            ← One-time initialization script (run once at setup)
├── הפעל.bat                  ← Windows launcher script (double-click to start)
│
├── lessons.py                ← Legacy file — original prototype, no longer used
├── generate_cal_links.py     ← Legacy script — one-time calendar link generator
├── process_logo.py           ← Legacy utility — one-time logo processing script
├── process_logo2.py          ← Legacy utility — one-time logo processing script
└── strategic_review.md       ← Internal product/architecture review document
```

### File Details

**`app.py`**
The public Streamlit page. Loads published lessons from `utils.py`, applies lesson-range filters from config, and renders upcoming and past lesson cards with calendar links. When subscriber collection is enabled in settings, also shows a registration form. No authentication required.

**`pages/admin.py`**
The admin panel, accessible at `/admin`. Protected by email + password login with bcrypt verification and brute-force lockout. Contains seven tabs: Dashboard, Lessons, Communication, Admins, Activity Log, Backups & Export, Settings. Enforces role-based access (Admin vs Viewer).

**`utils.py`**
The shared data layer. All file paths are resolved relative to the file itself using `os.path.dirname(os.path.abspath(__file__))`, so the module works correctly from any working directory. Contains all functions for reading/writing lessons, config, subscribers, logs, backups, exports, and message generation.

**`lessons_data.json`**
Array of lesson objects. Each lesson contains: `id` (UUID), `num`, `date_iso`, `day`, `time_start`, `duration_minutes`, `topic`, `subtitle`, `description`, `status`, `visibility`, `teacher`, `org`, `process`, `zoom_link`, `registration_link`, `recording_link`, `files_link`.

**`admin_config.json`**
Contains: admin user array (email, full_name, password_hash bcrypt, role, is_super_admin, created_at, reset_token), login settings (max_attempts, lockout_minutes), app settings (subscription_enabled, display_from_lesson, display_to_lesson).

**`subscribers.json`**
Array of subscriber objects: `id`, `lesson_id`, `lesson_num`, `email`, `first_name`, `last_name`, `subscribed_at`, `active`, `consent`.

**`activity_log.json`**
Array of log entries (newest last, capped at 2,000): `timestamp`, `admin_email`, `admin_name`, `action`, `details`. Displayed in reverse order in the admin panel.

**`backups/`**
Auto-created JSON snapshots of `lessons_data.json`. A new backup is created automatically before every save, restore, or import operation. Filenames follow the pattern `lessons_YYYYMMDD_HHMMSS.json`. The 50 most recent backups are kept; older ones are pruned automatically.

**`.streamlit/config.toml`**
```toml
[browser]
gatherUsageStats = false

[server]
headless = true
```

**`setup_admin.py`**
A one-time initialization script. Creates `admin_config.json` with the first admin account and `lessons_data.json` with the initial lesson schedule. Run only once during initial project setup. Do not re-run on an existing installation — it will overwrite live data.

**`הפעל.bat`**
Windows batch file launcher. Double-click to start the application. Uses `%~dp0` to resolve the project directory independently of the current working directory, so it works correctly from OneDrive or any location.

---

## 3. How to Run the Project Locally

### Prerequisites
- Python 3.8 or higher
- `streamlit` and `bcrypt` packages installed

### Install dependencies
```bash
pip install streamlit bcrypt
```

### First-time setup (new installation only)
```bash
cd "<project folder>"
python setup_admin.py
```
This creates `admin_config.json` and `lessons_data.json`.

### Start the application

**Option A — Double-click launcher (Windows)**
Double-click `הפעל.bat` in the project folder.

**Option B — Command line**
```bash
cd "<project folder>"
streamlit run app.py
```

The application opens in the browser at `http://localhost:8501`.
The admin panel is at `http://localhost:8501/admin`.

---

## 4. How to Create a Backup

### Automatic (recommended)
A backup is created automatically before every lesson save, restore, or JSON import. No action required.

### Manual backup via Admin Panel
1. Open the admin panel → **💾 גיבויים וייצוא** tab
2. Select any backup from the list
3. Click **⬇️ הורד גיבוי זה** to download it as a JSON file

### Manual file copy
Copy `lessons_data.json` to a safe location. Optionally also copy `admin_config.json` and `subscribers.json`.

---

## 5. How to Restore a Backup

### Via Admin Panel (recommended)
1. Open **💾 גיבויים וייצוא** tab
2. Select the desired backup from the dropdown list
3. Click **♻️ שחזר גיבוי זה**
4. Confirm — the current lesson data is replaced

### Manual restore
1. Stop the application
2. Replace `lessons_data.json` with the backup file
3. Restart the application

---

## 6. How to Move the Project to Another Computer

1. Copy the entire project folder to the new computer (including all JSON files and the `backups/` folder)
2. Install Python 3.8+ on the new computer
3. Install dependencies: `pip install streamlit bcrypt`
4. Run the application: double-click `הפעל.bat` or run `streamlit run app.py` from the project folder
5. No path changes needed — all paths in the code are relative to the project folder

**Note:** Do not run `setup_admin.py` again. That would overwrite your existing data. Only run it on a completely fresh installation.

---

## 7. How to Deploy in the Future

### Current situation
The application runs locally. It is only accessible while the host computer is on and running the app.

### Option A — Streamlit Community Cloud (free)
Requires migrating data storage from local JSON files to a cloud database (e.g., Supabase free tier), because Streamlit Cloud does not provide persistent file storage. The application code and data layer (utils.py) would need to be adapted.

Steps outline:
1. Create a GitHub repository and push the project files
2. Create a Supabase project and migrate JSON data to PostgreSQL tables
3. Update `utils.py` to read/write from Supabase instead of JSON files
4. Store credentials in Streamlit Cloud Secrets
5. Connect the GitHub repo to Streamlit Community Cloud

### Option B — Railway / Render (minimal code changes)
Platforms that provide a persistent disk. The current JSON-based architecture works as-is.

Steps outline:
1. Push project to GitHub
2. Connect GitHub repo to Railway or Render
3. Set start command: `streamlit run app.py --server.port $PORT --server.headless true`
4. Mount a persistent volume at the project directory

### Option C — VPS (full control)
Deploy on a Linux VPS (e.g., DigitalOcean, AWS Lightsail). Run the app as a systemd service behind an nginx reverse proxy.

---

## 8. External Dependencies and Libraries

| Package | Version constraint | Purpose |
|---|---|---|
| `streamlit` | >= 1.28 | Web framework, UI rendering, session state |
| `bcrypt` | any | Password hashing and verification |

All other imports (`json`, `os`, `uuid`, `csv`, `io`, `re`, `secrets`, `datetime`, `urllib.parse`, `copy`, `sys`, `base64`) are Python standard library — no additional installation required.

### Runtime dependencies (loaded by browser)
| Resource | Source | Purpose |
|---|---|---|
| Heebo font | Google Fonts CDN | Hebrew typography |
| Material Icons / Material Symbols | Google Fonts CDN | Streamlit UI icons |

---

## 9. Future Planned Features

- **Automated email sending** — direct integration with an email provider (Mailgun, SendGrid, or Gmail SMTP) to send updates to subscribers without manual copy-paste
- **Automated lesson reminders** — scheduled emails/messages to subscribers before each lesson
- **Cloud deployment** — make the public page permanently accessible online, independent of any local machine
- **Cloud database migration** — move from JSON flat files to a persistent cloud database to support deployment
- **Publisher role** — a third role with permission to send communication but not edit lesson data
- **Log export** — download the activity log as CSV/JSON for auditing

---

## 10. Known Limitations

| Limitation | Impact | Notes |
|---|---|---|
| Local-only deployment | Public users can only access the site while the host computer is running the app | Planned for future cloud deployment |
| No persistent storage on Streamlit Cloud | Data would be lost on every app restart if deployed to Streamlit Cloud | Requires database migration before cloud deployment |
| No concurrent write safety | If two admins save simultaneously, one write may overwrite the other | Acceptable for small teams; would require locking for larger teams |
| Email sending is manual | Admin must copy generated text and send manually | Planned future feature |
| No two-factor authentication | Admin access protected by password only | Mitigated by bcrypt, lockout, and password reset |
| Failed login attempts not persisted | Brute-force counter resets on browser refresh or server restart | Low risk for internal tool |
| Activity log capped at 2,000 entries | Oldest entries are pruned automatically | Acceptable for current scale |
| Log displays only 100 entries | No pagination; older entries not visible unless searched/filtered | Low priority improvement |
| `renumber_lessons` and `update_settings` not in ACTION_LABELS | Appear as raw English keys in the log display | Minor cosmetic issue |
| Backup files accumulate locally | Not automatically synced to cloud | OneDrive sync provides partial mitigation |

---

## 11. Architecture Overview

```
Browser (Public User)
        │
        ▼
   app.py  ──────────────────────────► utils.py
   (Public page)                       │
        │                              ├── load_lessons()
        │                              ├── load_config()
        │                              ├── add_subscriber()
        │                              └── generate_ics() / google_url() / outlook_url()
        │
        │  reads: lessons_data.json
        │  reads: admin_config.json (for settings)
        │  writes: subscribers.json
        │

Browser (Admin)
        │
        ▼
   pages/admin.py  ──────────────────► utils.py
   (Admin panel)                        │
        │                               ├── load_lessons() / save_lessons()
        │                               ├── load_config() / save_config()
        │                               ├── load_subscribers()
        │                               ├── log_action() / load_log()
        │                               ├── auto_backup() / restore_backup()
        │                               ├── export_json() / export_csv()
        │                               └── generate_update_email() / generate_whatsapp_text()
        │
        │  reads/writes: lessons_data.json
        │  reads/writes: admin_config.json
        │  reads/writes: subscribers.json
        │  reads/writes: activity_log.json
        │  writes: backups/lessons_YYYYMMDD_HHMMSS.json
```

### Communication flow
- `app.py` and `pages/admin.py` share no direct connection — they communicate only through the shared data files via `utils.py`
- All file paths in `utils.py` are resolved at module load time using `os.path.dirname(os.path.abspath(__file__))`, making the module location-independent
- Streamlit manages state within a session via `st.session_state`; there is no inter-session shared state beyond the JSON files
- The public page reads config once per page load to apply display range and subscription settings; it does not cache config across reruns

---

## 12. Maintenance Recommendations

- **Add `renumber_lessons` and `update_settings` to `ACTION_LABELS`** in `admin.py` — these action types are logged but not translated to Hebrew in the log viewer
- **Periodically prune backups** — the system keeps 50 backups automatically, but the `backups/` folder should be reviewed periodically if disk space is a concern
- **Export and archive the activity log** — the log is capped at 2,000 entries; export to CSV periodically if long-term audit history is needed
- **Review admin accounts** — remove viewer or admin accounts that are no longer needed
- **Update lesson data proactively** — mark completed lessons as "התקיים" and add recording links promptly after each lesson
- **Do not edit JSON files manually** — always use the admin panel; manual edits can break the JSON structure and crash the app
- **Keep the `setup_admin.py` file** but do not re-run it — it is useful as documentation of the initial data schema
- **Legacy files** (`lessons.py`, `generate_cal_links.py`, `process_logo.py`, `process_logo2.py`) can be safely deleted — they are no longer used by the application

---

## 13. Security Recommendations

- **Change the default admin password immediately** on any new installation — `setup_admin.py` uses a weak default password (`1234`)
- **Do not commit JSON data files to a public GitHub repository** — `lessons_data.json`, `admin_config.json`, and `subscribers.json` contain personal information (emails, names, password hashes)
- **Add a `.gitignore`** before creating a GitHub repository, excluding: `*.json`, `backups/`, `__pycache__/`, `.streamlit/`
- **Keep the `admin_config.json` file private** — it contains bcrypt password hashes and reset tokens
- **The `subscribers.json` file contains personal data** (first name, last name, email, consent) — handle in compliance with applicable privacy regulations (GDPR / Israeli Privacy Protection Law)
- **Use strong passwords** for admin accounts — minimum 12 characters recommended
- **The password reset system is development-only** — reset links are displayed on screen (`http://localhost:8501/admin?reset=...`) rather than sent by email; in production, integrate with an email provider before enabling password reset for cloud deployments

---

## 14. Version Information

| Item | Value |
|---|---|
| Documentation date | June 2026 |
| Python requirement | 3.8+ |
| Primary framework | Streamlit |
| Data storage | JSON flat files |
| Authentication | bcrypt password hashing |
| Deployment status | Local only |
| Admin roles | Admin, Viewer |
| Public URL (planned) | https://shiur-patuach.netlify.app |
