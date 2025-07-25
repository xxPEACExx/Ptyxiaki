# # # # title.py
# #
# # def insert_title(did, cursor, db):
# #     if did:
# #         cursor.execute("INSERT IGNORE INTO title (did) VALUES (%s)", (did,))
# #         db.commit()
# #
# # title.py
# def insert_title(did, root, cursor, db):
#     if not did or root is None:
#         return
#
#     invention_titles = root.findall(".//invention-title")
#     title_text = None
#     for title in invention_titles:
#         if title.attrib.get('lang') == 'EN':
#             title_text = ''.join(title.itertext()).strip()
#             break
#
#     if not title_text:
#         return  # Δεν υπάρχει τίτλος στα Αγγλικά
#
#     # Αν θες, εδώ κάνεις lookup για lang_id στον πίνακα state. Εγώ βάζω 1 για EN απλά
#     lang_id = 1
#
#     cursor.execute("""
#         INSERT INTO title (did, title_text, lang)
#         VALUES (%s, %s, %s)
#         ON DUPLICATE KEY UPDATE title_text = VALUES(title_text), lang = VALUES(lang)
#     """, (did, title_text, lang_id))
#     db.commit()
# title.py

def get_lang_id(lang_code, cursor, db):
    cursor.execute("SELECT CID FROM state WHERE country_name = %s", (lang_code,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        # Αν δεν υπάρχει, εισάγεται καινούρια εγγραφή στη state
        cursor.execute("INSERT INTO state (country_name) VALUES (%s)", (lang_code,))
        db.commit()
        return cursor.lastrowid


def insert_title(did, root, cursor, db):
    if not did or root is None:
        return

    invention_titles = root.findall(".//invention-title")
    title_text = None
    lang_code = None

    for title in invention_titles:
        if title.attrib.get('lang') == 'EN':
            title_text = ''.join(title.itertext()).strip()
            lang_code = title.attrib.get('lang')
            break

    if not title_text:
        return  # Δεν υπάρχει τίτλος στα Αγγλικά

    # Υπολογισμός μεγέθους
    size_title_chars = len(title_text)
    size_title_words = len(title_text.split())

    # Αντιστοίχιση γλώσσας με CID στον πίνακα state
    lang_id = get_lang_id(lang_code, cursor, db)

    # Εισαγωγή στον πίνακα title
    cursor.execute("""
        INSERT INTO title (did, title_text, lang, size_title_chars, size_title_words)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            title_text = VALUES(title_text),
            lang = VALUES(lang),
            size_title_chars = VALUES(size_title_chars),
            size_title_words = VALUES(size_title_words)
    """, (did, title_text, lang_id, size_title_chars, size_title_words))

    db.commit()
