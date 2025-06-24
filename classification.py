# κανει εισαγωγη το did στον πινακα του classification

def insert_classification(did, cursor, db):
    if did:
        cursor.execute("INSERT IGNORE INTO classification (did) VALUES (%s)", (did,))
        db.commit()
