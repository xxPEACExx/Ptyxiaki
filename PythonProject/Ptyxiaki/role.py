role_mapping = {
    'applicant': 1,
    'inventor': 2,
    'agent': 3
}

def initialize_role(cursor, db):
    for name, rid in role_mapping.items():
        cursor.execute("SELECT COUNT(*) FROM role WHERE RID = %s", (rid,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO role (RID, name) VALUES (%s, %s)", (rid, name))
    db.commit()
