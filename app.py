from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, Response
import sqlite3
import os
import csv
import io
from datetime import datetime, date, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'squadron872_secret_key_change_me'

_data_dir = '/data' if os.path.isdir('/data') else '.'
DB_PATH = os.environ.get('DB_PATH', os.path.join(_data_dir, 'squadron.db'))

CONFIG_PASSWORD = 'inspector2024'
try:
    import config
    CONFIG_PASSWORD = config.PASSWORD
except:
    pass

UNIFORM_TYPES = {
    'green': {
        'label': 'Green Uniform (FTU)',
        'categories': ['HEADDRESS', 'TUNIC', 'SHIRT', 'PANTS', 'BOOTS', 'ACCESSORIES']
    },
    'blue': {
        'label': 'Blue Uniform (Dress)',
        'categories': ['HEADDRESS', 'TUNIC', 'SHIRT', 'TIE', 'PANTS', 'BOOTS', 'BADGES', 'ACCESSORIES']
    }
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_week_start(d=None):
    if d is None:
        d = date.today()
    monday = d - timedelta(days=d.weekday())
    return monday.isoformat()

def get_session_label(week_start):
    d = date.fromisoformat(week_start)
    wed = d + timedelta(days=2)
    return wed.strftime('Wed %b %d, %Y')

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def calc_score(scores_list):
    total = 0
    max_points = 0
    for score, status in scores_list:
        if status == 'scored':
            total += score
            max_points += 5
    if max_points == 0:
        return None
    return round((total / max_points) * 100, 1)

@app.context_processor
def inject_nav():
    try:
        db = get_db()
        flights = db.execute('SELECT id, name FROM flights ORDER BY name').fetchall()
        db.close()
        return {'nav_flights': [(f['name'], f['id']) for f in flights]}
    except:
        return {'nav_flights': []}

def auto_init_db():
    if not os.path.exists(DB_PATH):
        try:
            import init_db as idb
            idb.init_db()
        except Exception as e:
            print(f'DB init error: {e}')

auto_init_db()

# ── AUTH ────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == CONFIG_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        flash('Incorrect password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── HELPERS ─────────────────────────────────────────────────
def _flight_week_avg(db, flight_id, week_start):
    rows = db.execute('''
        SELECT s.score, s.status FROM scores s
        JOIN inspections i ON s.inspection_id=i.id
        WHERE i.flight_id=? AND i.week_start=?
    ''', (flight_id, week_start)).fetchall()
    if not rows:
        return None
    return calc_score([(r['score'], r['status']) for r in rows])

def _cadet_week_score(db, cadet_id, week_start):
    insp = db.execute('SELECT * FROM inspections WHERE cadet_id=? AND week_start=?', (cadet_id, week_start)).fetchone()
    if not insp or insp['absent']:
        return None
    sc = db.execute('SELECT score, status FROM scores WHERE inspection_id=?', (insp['id'],)).fetchall()
    return calc_score([(r['score'], r['status']) for r in sc])

def _flight_category_avgs(db, flight_id, week_start):
    all_cats = set()
    for u in UNIFORM_TYPES.values():
        all_cats.update(u['categories'])
    cat_totals = {c: [] for c in all_cats}
    rows = db.execute('''
        SELECT s.score, s.status, s.category FROM scores s
        JOIN inspections i ON s.inspection_id=i.id
        WHERE i.flight_id=? AND i.week_start=? AND i.absent=0
    ''', (flight_id, week_start)).fetchall()
    for r in rows:
        if r['status'] == 'scored' and r['category'] in cat_totals:
            cat_totals[r['category']].append(r['score'])
    return {cat: (round(sum(v)/len(v), 2) if v else None) for cat, v in cat_totals.items()}

def _get_recent_weeks(db, n=8):
    rows = db.execute('SELECT DISTINCT week_start FROM inspections ORDER BY week_start DESC LIMIT ?', (n,)).fetchall()
    return [r['week_start'] for r in rows]

# ── DASHBOARD ───────────────────────────────────────────────
@app.route('/')
@login_required
def dashboard():
    db = get_db()
    week = get_week_start()
    last_week = (date.fromisoformat(week) - timedelta(weeks=1)).isoformat()

    flights = db.execute('SELECT * FROM flights ORDER BY name').fetchall()
    flight_data = []
    for f in flights:
        count = db.execute('SELECT COUNT(*) FROM cadets WHERE flight_id=?', (f['id'],)).fetchone()[0]
        this_avg = _flight_week_avg(db, f['id'], week)
        prev_avg = _flight_week_avg(db, f['id'], last_week)
        trend = round(this_avg - prev_avg, 1) if (this_avg and prev_avg) else None
        inspected = db.execute('SELECT COUNT(DISTINCT cadet_id) FROM inspections WHERE flight_id=? AND week_start=?', (f['id'], week)).fetchone()[0]
        absent = db.execute('SELECT COUNT(*) FROM inspections WHERE flight_id=? AND week_start=? AND absent=1', (f['id'], week)).fetchone()[0]
        flight_data.append({'flight': dict(f), 'avg': this_avg, 'prev_avg': prev_avg, 'trend': trend, 'count': count, 'inspected': inspected, 'absent': absent})

    all_scores = [fd['avg'] for fd in flight_data if fd['avg'] is not None]
    squad_avg = round(sum(all_scores)/len(all_scores), 1) if all_scores else None

    # Top 5 this week
    cadets_all = db.execute('SELECT c.id, c.name, c.rank, f.name as flight FROM cadets c JOIN flights f ON c.flight_id=f.id').fetchall()
    top_list = []
    for c in cadets_all:
        score = _cadet_week_score(db, c['id'], week)
        if score is not None:
            top_list.append({'id': c['id'], 'name': c['name'], 'rank': c['rank'], 'flight': c['flight'], 'score': score})
    top_list.sort(key=lambda x: x['score'], reverse=True)
    top5 = top_list[:5]

    # Most improved (this week vs last week)
    improved = []
    for c in cadets_all:
        s1 = _cadet_week_score(db, c['id'], last_week)
        s2 = _cadet_week_score(db, c['id'], week)
        if s1 is not None and s2 is not None:
            improved.append({'id': c['id'], 'name': c['name'], 'rank': c['rank'], 'flight': c['flight'], 'improvement': round(s2-s1,1), 'current': s2})
    improved.sort(key=lambda x: x['improvement'], reverse=True)
    top_improved = improved[:5]

    db.close()
    return render_template('dashboard.html',
        squad_avg=squad_avg, flights=flight_data,
        top5=top5, improved=top_improved,
        week_label=get_session_label(week), current_week=week)

# ── FLIGHT PAGE ─────────────────────────────────────────────
@app.route('/flight/<int:flight_id>')
@login_required
def flight(flight_id):
    db = get_db()
    f = db.execute('SELECT * FROM flights WHERE id=?', (flight_id,)).fetchone()
    week = get_week_start()
    last_week = (date.fromisoformat(week) - timedelta(weeks=1)).isoformat()

    cadets = db.execute('SELECT * FROM cadets WHERE flight_id=? ORDER BY name', (flight_id,)).fetchall()
    leaderboard = []
    for c in cadets:
        insp = db.execute('SELECT * FROM inspections WHERE cadet_id=? AND week_start=?', (c['id'], week)).fetchone()
        score = None
        absent = False
        if insp:
            absent = bool(insp['absent'])
            if not absent:
                sc = db.execute('SELECT score, status FROM scores WHERE inspection_id=?', (insp['id'],)).fetchall()
                score = calc_score([(r['score'], r['status']) for r in sc])
        leaderboard.append({'id': c['id'], 'name': c['name'], 'rank': c['rank'], 'score': score, 'absent': absent, 'inspected': insp is not None})
    leaderboard.sort(key=lambda x: (x['absent'], x['score'] is None, -(x['score'] or 0)))

    cat_avgs = _flight_category_avgs(db, flight_id, week)
    valid_cats = {k: v for k, v in cat_avgs.items() if v is not None}
    strongest = max(valid_cats, key=valid_cats.get) if valid_cats else None
    weakest = min(valid_cats, key=valid_cats.get) if valid_cats else None

    this_avg = _flight_week_avg(db, flight_id, week)
    last_avg = _flight_week_avg(db, flight_id, last_week)
    trend = round(this_avg - last_avg, 1) if (this_avg and last_avg) else None

    # Weekly history for chart
    all_weeks = db.execute('SELECT DISTINCT week_start FROM inspections WHERE flight_id=? ORDER BY week_start', (flight_id,)).fetchall()
    weekly_avgs = []
    for w in all_weeks:
        avg = _flight_week_avg(db, flight_id, w['week_start'])
        weekly_avgs.append({'label': get_session_label(w['week_start']), 'avg': avg})

    all_flights = db.execute('SELECT id FROM flights').fetchall()
    flight_avgs = [(af['id'], _flight_week_avg(db, af['id'], week)) for af in all_flights]
    flight_avgs = [(fid, avg) for fid, avg in flight_avgs if avg is not None]
    flight_avgs.sort(key=lambda x: x[1], reverse=True)
    rank = next((i+1 for i, (fid, _) in enumerate(flight_avgs) if fid == flight_id), None)

    absent_count = db.execute('SELECT COUNT(*) FROM inspections WHERE flight_id=? AND week_start=? AND absent=1', (flight_id, week)).fetchone()[0]

    db.close()
    return render_template('flight.html',
        flight=f, leaderboard=leaderboard,
        cat_avgs=cat_avgs, strongest=strongest, weakest=weakest,
        avg_score=this_avg, last_avg=last_avg, trend=trend,
        weekly_avgs=weekly_avgs,
        rank=rank, total_flights=len(all_flights),
        absent_count=absent_count,
        week_label=get_session_label(week))

# ── INSPECT SELECT ──────────────────────────────────────────
@app.route('/inspect/<int:flight_id>')
@login_required
def inspect_flight(flight_id):
    db = get_db()
    f = db.execute('SELECT * FROM flights WHERE id=?', (flight_id,)).fetchone()
    cadets = db.execute('SELECT * FROM cadets WHERE flight_id=? ORDER BY name', (flight_id,)).fetchall()
    week = get_week_start()
    cadet_status = {}
    for c in cadets:
        insp = db.execute('SELECT absent FROM inspections WHERE cadet_id=? AND week_start=?', (c['id'], week)).fetchone()
        if insp is None:
            cadet_status[c['id']] = 'pending'
        elif insp['absent']:
            cadet_status[c['id']] = 'absent'
        else:
            cadet_status[c['id']] = 'done'
    db.close()
    pending = sum(1 for s in cadet_status.values() if s == 'pending')
    done = sum(1 for s in cadet_status.values() if s == 'done')
    absent = sum(1 for s in cadet_status.values() if s == 'absent')
    return render_template('inspect_select.html',
        flight=f, cadets=cadets, cadet_status=cadet_status,
        week_label=get_session_label(week),
        pending=pending, done=done, absent=absent)

# ── INSPECT CADET ───────────────────────────────────────────
@app.route('/inspect/cadet/<int:cadet_id>', methods=['GET', 'POST'])
@login_required
def inspect_cadet(cadet_id):
    db = get_db()
    cadet = db.execute(
        'SELECT c.*, f.name as flight_name, f.id as fid FROM cadets c JOIN flights f ON c.flight_id=f.id WHERE c.id=?',
        (cadet_id,)
    ).fetchone()
    week = get_week_start()

    if request.method == 'POST':
        data = request.json
        old = db.execute('SELECT id FROM inspections WHERE cadet_id=? AND week_start=?', (cadet_id, week)).fetchone()
        if old:
            db.execute('DELETE FROM scores WHERE inspection_id=?', (old['id'],))
            db.execute('DELETE FROM inspections WHERE id=?', (old['id'],))

        absent = data.get('absent', False)
        uniform_type = data.get('uniform_type', 'green')
        insp_id = db.execute(
            'INSERT INTO inspections (cadet_id, flight_id, week_start, date, absent, uniform_type) VALUES (?,?,?,?,?,?)',
            (cadet_id, cadet['fid'], week, datetime.now().isoformat(), 1 if absent else 0, uniform_type)
        ).lastrowid

        if not absent:
            for cat in UNIFORM_TYPES[uniform_type]['categories']:
                status = data.get(f'{cat}_status', 'scored')
                score = int(data.get(cat, 3)) if status == 'scored' else 0
                db.execute('INSERT INTO scores (inspection_id, category, score, status) VALUES (?,?,?,?)',
                           (insp_id, cat, score, status))

        db.commit()
        db.close()
        return jsonify({'success': True})

    existing = db.execute('SELECT * FROM inspections WHERE cadet_id=? AND week_start=?', (cadet_id, week)).fetchone()
    existing_scores = {}
    existing_uniform = 'green'
    if existing and not existing['absent']:
        existing_uniform = existing['uniform_type'] or 'green'
        rows = db.execute('SELECT * FROM scores WHERE inspection_id=?', (existing['id'],)).fetchall()
        for r in rows:
            existing_scores[r['category']] = {'score': r['score'], 'status': r['status']}

    # Next cadet in same flight
    all_cadets = db.execute('SELECT id FROM cadets WHERE flight_id=? ORDER BY name', (cadet['fid'],)).fetchall()
    ids = [c['id'] for c in all_cadets]
    next_id = None
    if cadet_id in ids:
        idx = ids.index(cadet_id)
        if idx + 1 < len(ids):
            next_id = ids[idx + 1]

    db.close()
    return render_template('inspect_cadet.html',
        cadet=cadet, uniform_types=UNIFORM_TYPES,
        existing=existing, existing_scores=existing_scores,
        existing_uniform=existing_uniform,
        next_cadet_id=next_id,
        week_label=get_session_label(week))

# ── CADET PROFILE ───────────────────────────────────────────
@app.route('/cadet/<int:cadet_id>')
@login_required
def cadet_profile(cadet_id):
    db = get_db()
    cadet = db.execute(
        'SELECT c.*, f.name as flight_name, f.id as fid FROM cadets c JOIN flights f ON c.flight_id=f.id WHERE c.id=?',
        (cadet_id,)
    ).fetchone()

    inspections = db.execute('SELECT * FROM inspections WHERE cadet_id=? ORDER BY week_start', (cadet_id,)).fetchall()
    history = []
    for insp in inspections:
        label = get_session_label(insp['week_start'])
        if insp['absent']:
            history.append({'week': insp['week_start'], 'label': label, 'score': None, 'absent': True, 'uniform_type': None})
        else:
            sc = db.execute('SELECT score, status FROM scores WHERE inspection_id=?', (insp['id'],)).fetchall()
            pct = calc_score([(r['score'], r['status']) for r in sc])
            history.append({'week': insp['week_start'], 'label': label, 'score': pct, 'absent': False, 'uniform_type': insp['uniform_type']})

    cat_scores = {}
    suggestions = []
    latest_uniform = 'green'
    latest_insp = next((h for h in reversed(history) if not h['absent']), None)
    if latest_insp:
        latest_uniform = latest_insp['uniform_type'] or 'green'
        insp_row = db.execute('SELECT id FROM inspections WHERE cadet_id=? AND week_start=?', (cadet_id, latest_insp['week'])).fetchone()
        if insp_row:
            rows = db.execute('SELECT * FROM scores WHERE inspection_id=?', (insp_row['id'],)).fetchall()
            for r in rows:
                cat_scores[r['category']] = {'score': r['score'], 'status': r['status']}
                if r['status'] == 'scored' and r['score'] < 4:
                    suggestions.append({'category': r['category'], 'score': r['score']})

    absence_count = sum(1 for h in history if h['absent'])
    scored_history = [h for h in history if not h['absent'] and h['score'] is not None]
    current_score = scored_history[-1]['score'] if scored_history else None
    overall_improvement = round(scored_history[-1]['score'] - scored_history[0]['score'], 1) if len(scored_history) >= 2 else None

    db.close()
    return render_template('cadet.html',
        cadet=cadet, history=history,
        cat_scores=cat_scores, suggestions=suggestions,
        current_score=current_score,
        absence_count=absence_count,
        overall_improvement=overall_improvement,
        categories=UNIFORM_TYPES[latest_uniform]['categories'],
        latest_uniform=latest_uniform,
        uniform_types=UNIFORM_TYPES)

# ── WEEKLY OVERVIEW ─────────────────────────────────────────
@app.route('/weekly')
@login_required
def weekly_history():
    db = get_db()
    week = get_week_start()
    last_week = (date.fromisoformat(week) - timedelta(weeks=1)).isoformat()

    all_weeks_raw = db.execute('SELECT DISTINCT week_start FROM inspections ORDER BY week_start DESC').fetchall()
    all_weeks = [w['week_start'] for w in all_weeks_raw]

    flights = db.execute('SELECT * FROM flights ORDER BY name').fetchall()

    # Matrix: flight rows x week columns
    matrix = []
    for f in flights:
        row = {'name': f['name'], 'id': f['id'], 'weeks': []}
        prev = None
        for w in reversed(all_weeks):  # chronological
            avg = _flight_week_avg(db, f['id'], w)
            trend = round(avg - prev, 1) if (avg and prev) else None
            row['weeks'].append({'week': w, 'avg': avg, 'trend': trend})
            prev = avg
        row['weeks'].reverse()  # back to newest first
        matrix.append(row)

    # Improvement: this week vs last week per flight
    flight_trends = []
    for f in flights:
        curr = _flight_week_avg(db, f['id'], week)
        prev = _flight_week_avg(db, f['id'], last_week)
        trend = round(curr - prev, 1) if (curr is not None and prev is not None) else None
        flight_trends.append({'id': f['id'], 'name': f['name'], 'current': curr, 'previous': prev, 'trend': trend})
    flight_trends.sort(key=lambda x: (x['current'] is None, -(x['current'] or 0)))

    db.close()
    return render_template('weekly.html',
        all_weeks=all_weeks,
        week_labels={w: get_session_label(w) for w in all_weeks},
        matrix=matrix, flight_trends=flight_trends,
        current_week=week, week_label=get_session_label(week))

# ── RANKINGS ────────────────────────────────────────────────
@app.route('/rankings')
@login_required
def rankings():
    db = get_db()
    week = get_week_start()
    cadets = db.execute('SELECT c.id, c.name, c.rank, f.name as flight, f.id as fid FROM cadets c JOIN flights f ON c.flight_id=f.id').fetchall()
    leaderboard = []
    for c in cadets:
        insp = db.execute('SELECT * FROM inspections WHERE cadet_id=? AND week_start=?', (c['id'], week)).fetchone()
        score = None
        absent = False
        if insp:
            absent = bool(insp['absent'])
            if not absent:
                sc = db.execute('SELECT score, status FROM scores WHERE inspection_id=?', (insp['id'],)).fetchall()
                score = calc_score([(r['score'], r['status']) for r in sc])
        leaderboard.append({'id': c['id'], 'name': c['name'], 'rank': c['rank'], 'flight': c['flight'], 'fid': c['fid'], 'score': score, 'absent': absent})
    leaderboard.sort(key=lambda x: (x['absent'], x['score'] is None, -(x['score'] or 0)))
    for i, e in enumerate(leaderboard):
        e['position'] = i + 1
    flights = db.execute('SELECT * FROM flights ORDER BY name').fetchall()
    db.close()
    return render_template('rankings.html', leaderboard=leaderboard, flights=flights, week_label=get_session_label(week))

# ── SEARCH ──────────────────────────────────────────────────
@app.route('/search')
@login_required
def search():
    q = request.args.get('q', '').strip()
    db = get_db()
    results = []
    if q:
        rows = db.execute("SELECT c.id, c.name, c.rank, f.name as flight FROM cadets c JOIN flights f ON c.flight_id=f.id WHERE c.name LIKE ? OR c.rank LIKE ? ORDER BY c.name LIMIT 20", (f'%{q}%', f'%{q}%')).fetchall()
        results = [dict(r) for r in rows]
    db.close()
    return jsonify(results)

# ── EXPORT ──────────────────────────────────────────────────
@app.route('/export')
@login_required
def export_csv():
    db = get_db()
    week = get_week_start()
    cadets = db.execute('SELECT c.id, c.name, c.rank, f.name as flight FROM cadets c JOIN flights f ON c.flight_id=f.id ORDER BY f.name, c.name').fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Rank', 'Name', 'Flight', f'Score ({get_session_label(week)})', 'Status', 'Total Inspections', 'Absences'])
    for c in cadets:
        insp = db.execute('SELECT * FROM inspections WHERE cadet_id=? AND week_start=?', (c['id'], week)).fetchone()
        total = db.execute('SELECT COUNT(*) FROM inspections WHERE cadet_id=?', (c['id'],)).fetchone()[0]
        absences = db.execute('SELECT COUNT(*) FROM inspections WHERE cadet_id=? AND absent=1', (c['id'],)).fetchone()[0]
        status = 'Not Inspected'
        score_str = ''
        if insp:
            if insp['absent']:
                status = 'Absent'
            else:
                sc = db.execute('SELECT score, status FROM scores WHERE inspection_id=?', (insp['id'],)).fetchall()
                s = calc_score([(r['score'], r['status']) for r in sc])
                status = 'Inspected'
                score_str = f'{s}%' if s else ''
        writer.writerow([c['rank'], c['name'], c['flight'], score_str, status, total, absences])
    db.close()
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': f'attachment; filename=squadron_{datetime.now().strftime("%Y%m%d")}.csv'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
