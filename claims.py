# κανει εισαγωγη το did στον πινακα του claim

def insert_claim(did, cursor, db):
    if did:
        cursor.execute("INSERT IGNORE INTO claims (did) VALUES (%s)", (did,))
        db.commit()
