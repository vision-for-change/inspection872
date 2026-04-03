# 872 Kiwanis Kanata Squadron — Inspection System

A Flask web application for tracking uniform inspections across all 9 flights.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize the database (first time only)
```bash
python init_db.py
```
This creates `squadron.db` and loads all 200+ cadets automatically.

### 4. Run the app
```bash
python app.py
```

Open your browser to: **http://localhost:5000**

---

## 🔑 Login

Default password: `inspector2024`

---

## 🔒 Changing the Password

1. Open `config.py`
2. Change the `PASSWORD` value:
   ```python
   PASSWORD = 'your-new-password-here'
   ```
3. Restart the app

---

## ➕ Adding Future Cadets

Open `init_db.py` and find the flight you want to add to in `FLIGHTS_CADETS`.

Add a new line in the format `('RANK', 'LastName, FirstInitial')`:
```python
'Arrow': [
    ...existing cadets...
    ('Cdt', 'NewCadet, A'),  # Add here
],
```

Then re-run: `python init_db.py` (note: this resets ALL scores — export CSV first!)

**To add a cadet without resetting the database**, run this in Python:
```python
import sqlite3
conn = sqlite3.connect('squadron.db')
# Find flight ID first:
fid = conn.execute("SELECT id FROM flights WHERE name='Arrow'").fetchone()[0]
# Insert cadet:
conn.execute("INSERT INTO cadets (name, rank, flight_id) VALUES (?,?,?)", ('NewCadet, A', 'Cdt', fid))
conn.commit()
conn.close()
```

---

## 📊 Features

- **Dashboard**: Squadron average, flight cards, Top 5, Most Improved
- **Flight Pages**: Leaderboard, category averages chart, flight ranking
- **Inspection Flow**: Score cadets 1-5 per category, or mark Excused
- **Cadet Profiles**: History graph, radar chart, improvement suggestions
- **Rankings**: Full squadron leaderboard with flight filter
- **Search**: Global cadet search in the top bar
- **Dark Mode**: Toggle in sidebar footer
- **CSV Export**: Download all scores via sidebar button

---

## 📁 Folder Structure

```
squadron/
├── app.py              # Main Flask application
├── init_db.py          # Database initialization & cadet preload
├── config.py           # Password configuration
├── requirements.txt    # Python dependencies
├── squadron.db         # SQLite database (created on first run)
├── templates/
│   ├── base.html       # Sidebar, topbar, search
│   ├── login.html      # Login page
│   ├── dashboard.html  # Main dashboard
│   ├── flight.html     # Flight detail page
│   ├── inspect_select.html  # Choose cadet for inspection
│   ├── inspect_cadet.html   # Scoring form
│   ├── cadet.html      # Cadet profile with charts
│   └── rankings.html   # Full squadron rankings
└── static/
    ├── css/style.css   # All styles (navy/gold theme, dark mode)
    └── js/app.js       # Search, sidebar, dark mode toggle
```

---

## 🏆 Scoring

- Each category scored 1–5 (max 30 points)
- Categories: HEADDRESS, TUNIC, SHIRT, PANTS, BOOTS, ACCESSORIES
- **Excused**: Category not counted toward score
- **Final score** = (total points earned) / (max possible points) × 100%

---

## 🌐 Deploying for Others to Access

To let other inspectors on the same network access the app:
```bash
python app.py --host=0.0.0.0
```
Then share your local IP (e.g., `http://192.168.1.x:5000`).
