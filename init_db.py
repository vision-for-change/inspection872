import sqlite3
import os

_data_dir = '/data' if os.path.isdir('/data') else '.'
DB_PATH = os.environ.get('DB_PATH', os.path.join(_data_dir, 'squadron.db'))

FLIGHTS_CADETS = {
    'Arrow': [
        ('Cpl', 'Arseneault, E'), ('Cdt', 'Bhatia, K'), ('Cdt', 'Calvert, D'),
        ('Sgt', 'Chauhan, N'), ('Cdt', 'Chin, H'), ('Sgt', 'Eben, R'),
        ('Cdt', 'Falase, V'), ('Cpl', 'Gage, H'), ('LAC', 'Gunny, A'),
        ('Cdt', 'Johnson, J'), ('LAC', 'Kamath, A'), ('Sgt', 'Laughland, C'),
        ('Cdt', 'Liu, S'), ('Cdt', 'Nagaria, S'), ('Cpl', 'Naud, X'),
        ('Cpl', 'Nesbitt, G'), ('Cpl', 'Omariba, H'), ('Cpl', 'Petit-Clerc, T'),
        ('Cdt', 'Rego, A'), ('FCpl', 'Rethish, J'), ('Sgt', 'Rizwan, R'),
        ('Cdt', 'Singer, T'), ('FCpl', 'Tanori, I'), ('Cdt', 'Xie, A'),
    ],
    'Bristol': [
        ('FCpl', 'Anderson, A'), ('LAC', 'Binoy, J'), ('FCpl', 'Brent Lo Giudice, J'),
        ('Cpl', 'Cheung, Y'), ('FCpl', 'Danish, S'), ('Cpl', 'Dazang, J'),
        ('LAC', 'Fetiti, Y'), ('Cdt', 'Gokeda, B'), ('FCpl', 'Hall, S'),
        ('FCpl', 'Hayat, I'), ('Cpl', 'Jani, V'), ('Cdt', 'Khosraw Haneefi, N'),
        ('Cpl', 'Koss, R'), ('Sgt', 'Kozlov, M'), ('Sgt', 'Liu, R'),
        ('Cdt', 'Lunagariya, H'), ('Cpl', 'Mararah, G'), ('Cdt', 'Narayan, V'),
        ('Cpl', 'Nesbitt, T'), ('FCpl', 'Rizwan, Z'), ('LAC', 'Roshan, V'),
        ('Sgt', 'Shah, H'), ('Sgt', 'Shrikanth, S'), ('Cdt', 'Smyth, D'),
        ('Sgt', 'Tala Fokam, O'), ('LAC', 'Tanori, T'), ('Cdt', 'Xie, J'),
        ('Sgt', 'Zheng, C'),
    ],
    'Challenger': [
        ('Cpl', 'Ahmed, R'), ('Cpl', 'Akan, D'), ('FCpl', 'Al-Ghadban, J'),
        ('Sgt', 'Angirus, A'), ('Cpl', 'Deputat, A'), ('FCpl', 'Desormeaux, A'),
        ('LAC', 'Evin Peters, E'), ('LAC', 'Gaikwad, V'), ('Cdt', 'Haq, S'),
        ('Cdt', 'Manhas, O'), ('Sgt', 'Melnyk, K'), ('Cdt', 'Nzinga, S'),
        ('Cpl', 'Polu, S'), ('Sgt', 'Sangueu, K'), ('Cdt', 'Saurel, J'),
        ('Cpl', 'Sharma, S'), ('FCpl', 'Stolyrov, E'), ('Cdt', 'Sun, O'),
        ('Cpl', 'Walry, M'), ('Cpl', 'Xue, C'), ('Sgt', 'Yadav, T'),
        ('Cdt', 'Zaari, M'),
    ],
    'Delta': [
        ('FCpl', 'Aggour, A'), ('Cpl', 'Akan, D'), ('Cpl', 'Butler, Z'),
        ('Cdt', 'Chadha, N'), ('Cpl', 'Daymi, L'), ('Cdt', 'Deepak, P'),
        ('LAC', 'Edoukoi, E'), ('Sgt', 'Gantakolla, P'), ('FCpl', 'Hardy, D'),
        ('Cdt', 'Hassan, Z'), ('Cpl', 'Jacob, J'), ('Sgt', 'Jain, P'),
        ('Cpl', 'Kalyani, A'), ('Cdt', 'Kirkland, C'), ('Cpl', 'Lamb, S'),
        ('FCpl', 'Lu, Lisa'), ('Cpl', 'MacPherson, E'), ('Cpl', 'Massicard, S'),
        ('Cdt', 'Mayaka, M'), ('Sgt', 'Navaladi, D'), ('Cpl', 'Nkoue, O'),
        ('Sgt', 'Pathipan, V'), ('Cdt', 'Sauve, H'), ('Cpl', 'Sauvé Baron, H'),
        ('Cdt', 'Tang, A'), ('Cdt', 'Zaari, C'),
    ],
    'Expeditor': [
        ('Cdt', 'Alam, A'), ('Cpl', 'Anand, A'), ('Cdt', 'Chhajed, L'),
        ('FCpl', 'Davydov, D'), ('Cdt', 'Dennehy, S'), ('Cpl', 'Guduguntla, A'),
        ('Cdt', 'Hayat, J'), ('FCpl', 'Kanwar, V'), ('Cdt', 'Kositsin, H'),
        ('FCpl', 'Li, K'), ('LAC', 'Liu, S'), ('FCpl', 'Mahamoud, L'),
        ('Cdt', 'Melnyk, N'), ('LAC', 'Michalchuk, J'), ('Cpl', 'Nguyen Vince Bao, L'),
        ('Cdt', 'Okoh, J'), ('Cdt', 'Pasha, S'), ('Sgt', 'Rizvi, T'),
        ('FCpl', 'Sangueu, J'), ('Cpl', 'Santa, S'), ('Cdt', 'Serviss, N'),
        ('Sgt', 'Skinner, D'), ('FCpl', 'Spustek, T'), ('Cdt', 'Titus Glover, K'),
        ('Sgt', 'Yeung, G'), ('Cdt', 'Zaid, M'), ('Cpl', 'Zhang'),
    ],
    'Falcon': [
        ('Cdt', 'Al Nounou, O'), ('Cdt', 'Anderson, Q'), ('Cpl', 'Assaf-Pena, J'),
        ('Cpl', 'Cen, D'), ('Cdt', 'Dennis, A'), ('Sgt', 'El-Zallat, H'),
        ('Cpl', 'Falase, D'), ('Cpl', 'Hauser, O'), ('Cdt', 'Haynes, D'),
        ('Cpl', 'Khan, M'), ('Cdt', 'Krishnamurthy, A'), ('Sgt', 'Lee, P'),
        ('Cpl', 'Michalchuk, K'), ('Cdt', 'Mikhelson, A'), ('Cdt', 'Orrell, A'),
        ('FCpl', 'Pandey, N'), ('Cpl', 'Peled, L'), ('Cpl', 'Raza, H'),
        ('Cpl', 'Santhosh Kumar, S'), ('Cdt', 'Sethiya, A'), ('Cpl', 'Smith, O'),
        ('FCpl', 'Stevason, H'), ('Cpl', 'Valluri, A'), ('Sgt', 'Yasari, K'),
        ('Cdt', 'Zheng, E'),
    ],
    'Griffin': [
        ('Cpl', 'Barmat, A'), ('Cdt', 'Berghout, W'), ('FCpl', 'Chandola, K'),
        ('Cdt', 'Chilton Jones, E'), ('Sgt', 'Dazang, A'), ('LAC', 'Duraisamy, V'),
        ('Cpl', 'Falase, R'), ('LAC', 'Hasarambi, S'), ('Cpl', 'Huntington, S'),
        ('Cdt', 'Jafarzade, I'), ('Cdt', 'Kuang, J'), ('Cpl', 'Lee, H'),
        ('Cpl', 'Melo, J'), ('Sgt', 'Moore, A'), ('Cdt', 'Mwenelwata, H'),
        ('Cdt', 'Patel, N'), ('FCpl', 'Rosenlund, S'), ('Sgt', 'Rosenlund, W'),
        ('Sgt', 'Shreves, J'), ('Cdt', 'Simpson, H'), ('Cpl', 'Sultana, A'),
        ('FCpl', 'Wan, U'), ('Cdt', 'Watt, P'), ('FCpl', 'Weatherhead, N'),
        ('Cdt', 'Zheng, L'),
    ],
    'Band': [
        ('Cdt', 'Abdel Ahad, E'), ('Sgt', 'Aitken, Z'), ('Cpl', 'Best, Q'),
        ('FCpl', 'Bustillo, A'), ('Cdt', 'Cai, M'), ('Cdt', 'Chigwamba, R'),
        ('FCpl', 'Clavijo Pacheco, S'), ('FCpl', 'Desai, S'), ('Sgt', 'Dhandapani Anand, A'),
        ('Cpl', 'Doucet, G'), ('Cdt', 'Du, J'), ('Cpl', 'Gembali, E'),
        ('Cpl', 'Ginn, G'), ('Sgt', 'Ginn, J'), ('Sgt', 'Hauterive, M'),
        ('Cpl', 'Hughes, B'), ('Cpl', 'Karkouti, M'), ('FCpl', 'Lan-Yuan, H'),
        ('Cpl', 'Marsh, K'), ('Cdt', "O'Hagan, A"), ('Sgt', 'Okuwoga, J'),
        ('LAC', 'Okuwoga, R'), ('Sgt', 'Olenenko, M'), ('Cpl', 'Ouellet, S'),
        ('Sgt', 'Purohit, M'), ('FCpl', 'Rangakarthikeyan, C'), ('Cpl', 'Regpala, A'),
        ('Sgt', 'Sivakumar, H'), ('Cdt', 'Yapabandara, S'), ('Cdt', 'Tsygankov, A'),
    ],
    'Flag Party': [
        ('Sgt', 'Al-Kayat, D'), ('Sgt', 'Liu, A'), ('Sgt', 'Christianson, M'),
        ('FCpl', 'LeBlanc, S'), ('FCpl', 'Cousineau, M'), ('FCpl', 'Hardy, D'),
    ],
}

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        CREATE TABLE cadets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rank TEXT NOT NULL,
            flight_id INTEGER NOT NULL,
            FOREIGN KEY (flight_id) REFERENCES flights(id)
        );
        CREATE TABLE inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cadet_id INTEGER NOT NULL,
            flight_id INTEGER NOT NULL,
            week_start TEXT NOT NULL,
            date TEXT NOT NULL,
            absent INTEGER NOT NULL DEFAULT 0,
            uniform_type TEXT NOT NULL DEFAULT 'green',
            FOREIGN KEY (cadet_id) REFERENCES cadets(id),
            FOREIGN KEY (flight_id) REFERENCES flights(id)
        );
        CREATE TABLE scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inspection_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            score INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'scored',
            FOREIGN KEY (inspection_id) REFERENCES inspections(id)
        );
        CREATE INDEX idx_insp_cadet_week ON inspections(cadet_id, week_start);
        CREATE INDEX idx_insp_flight_week ON inspections(flight_id, week_start);
    ''')
    for flight_name, cadets in FLIGHTS_CADETS.items():
        c.execute('INSERT INTO flights (name) VALUES (?)', (flight_name,))
        fid = c.lastrowid
        for rank, name in cadets:
            c.execute('INSERT INTO cadets (name, rank, flight_id) VALUES (?,?,?)', (name, rank, fid))
    conn.commit()
    conn.close()
    print(f'DB initialized: {sum(len(v) for v in FLIGHTS_CADETS.values())} cadets, {len(FLIGHTS_CADETS)} flights.')

if __name__ == '__main__':
    init_db()
