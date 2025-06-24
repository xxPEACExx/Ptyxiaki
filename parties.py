# το μονο που κανει ειναι να εισαγει μεσα την βαση το did που επιστρεφει το document

def insert_parties(did, cursor, db):
    if did:
        cursor.execute("INSERT IGNORE INTO parties (did) VALUES (%s)", (did,))
        db.commit()
