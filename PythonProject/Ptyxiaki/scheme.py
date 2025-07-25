scheme_mapping = {
    'CPC': 1,
    'EC': 2,
    'ICO': 3
}

def initialize_scheme(cursor, db):
    for scheme_name, sid in scheme_mapping.items():
        cursor.execute("SELECT COUNT(*) FROM scheme WHERE SID = %s", (sid,))
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO scheme (SID, name) VALUES (%s, %s)",
                (sid, scheme_name)
            )
    db.commit()
