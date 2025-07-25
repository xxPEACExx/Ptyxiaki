# format.py

format_mapping = {'epo': 1, 'original': 2, 'intermediate': 3}

def initialize_format(cursor, db):
    for name, fid in format_mapping.items():
        cursor.execute("SELECT COUNT(*) FROM format WHERE FID = %s", (fid,))
        if cursor.fetchone()[0] == 0:
            print(f"[INFO] Εισαγωγή: ({fid}, '{name}') στον πίνακα format")
            cursor.execute("INSERT INTO format (FID, name) VALUES (%s, %s)", (fid, name))
    db.commit()
