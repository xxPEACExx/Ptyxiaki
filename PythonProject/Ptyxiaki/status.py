
status_mapping = {
    'corrected': 1,
    'deleted': 2
}

def initialize_status(cursor, db):
    for name, sid in status_mapping.items():
        cursor.execute("SELECT COUNT(*) FROM status WHERE SID = %s", (sid,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO status (SID, name) VALUES (%s, %s)", (sid, name))
    db.commit()
