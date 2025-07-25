
from state import lang_mapping  # Χάρτης χώρας -> ID
from format import format_mapping  # Αν δεν το έχεις, πρόσθεσε το: {'epo': 1, 'original': 2, 'intermediate': 3}
from role import role_mapping  # {'applicant': 1, 'inventor': 2, 'agent': 3}

def insert_parties(did, root, cursor, db):
    if not did or root is None:
        return

    def strip_ns(tag):
        return tag.split('}')[-1] if '}' in tag else tag

    # ➤ Εύρεση του <parties>
    parties_section = None
    for elem in root.iter():
        if strip_ns(elem.tag) == "parties":
            parties_section = elem
            break

    if parties_section is None:
        print("⚠️ Δεν βρέθηκε το στοιχείο <parties> στο XML.")
        return

    count = 0

    for role_tag in ["applicants", "inventors", "agents"]:
        role_section = parties_section.find(role_tag)
        if role_section is not None:
            role_name = role_tag[:-1]  # "applicants" -> "applicant"
            role_id = role_mapping.get(role_name)

            for person in role_section:
                addressbook = person.find("addressbook")
                if addressbook is not None:
                    last_name_elem = addressbook.find("last-name")
                    if last_name_elem is not None and last_name_elem.text:
                        last_name = last_name_elem.text.strip()

                        # 🔢 sequence
                        sequence = person.attrib.get("sequence")
                        try:
                            sequence = int(sequence) if sequence else None
                        except ValueError:
                            sequence = None

                        # 🏙️ city
                        city = None
                        address_elem = addressbook.find("address")
                        if address_elem is not None:
                            city_elem = address_elem.find("city")
                            if city_elem is not None and city_elem.text:
                                city = city_elem.text.strip()

                        # 🗂️ format
                        format_attr = person.attrib.get("format")
                        format_id = format_mapping.get(format_attr) if format_attr else None

                        # 🌍 state (country -> ID)
                        state_id = None
                        if address_elem is not None:
                            country_elem = address_elem.find("country")
                            if country_elem is not None and country_elem.text:
                                country_code = country_elem.text.strip()
                                state_id = lang_mapping.get(country_code)

                        # ✅ Εισαγωγή στην DB
                        cursor.execute("""
                            INSERT INTO parties (did, last_name, sequence, city, format, state, role)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (did, last_name, sequence, city, format_id, state_id, role_id))
                        count += 1

    db.commit()
    print(f"✅ Εισήχθησαν {count} εγγραφές με role & state για DID: {did}")

