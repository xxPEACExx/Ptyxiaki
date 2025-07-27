from flask import Flask, render_template, jsonify, request
import os
import xml.etree.ElementTree as ET
import mysql.connector
import threading
import time
import document
from Ptyxiaki.role import initialize_role
from Ptyxiaki.scheme import initialize_scheme
from Ptyxiaki.kind import initialize_kind
from Ptyxiaki.status import initialize_status

print("Import document from:", document.__file__)

from document import process_document
from claims import insert_claim
from classification import insert_classification
from parties import insert_parties
from title import insert_title
from state import initialize_state
from format import initialize_format
from loadsource import initialize_loadsource




app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="admin",
    database="epdatabase"
)
cursor = db.cursor()

# Καταστάσεις
processing_thread = None
processing_lock = threading.Lock()
running = False
paused = False
stopped = False
progress_percentage = 0


def process_files(files):
    global running, paused, stopped, progress_percentage
    total_files = len(files)
    for idx, file_path in enumerate(files, start=1):
        with processing_lock:
            if stopped:
                print("STOP")
                break
        # Περιμένουμε αν είναι paused
        while True:
            with processing_lock:
                if stopped:
                    print("STOP")
                    return
                if not paused:
                    break
            time.sleep(0.5)

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            did = process_document(file_path, cursor, db)
            insert_claim(did,root, cursor, db)
            insert_classification(did, root, cursor, db)
            insert_parties(did,root, cursor, db)
            insert_title(did, root, cursor, db)
            db.commit()

            progress_percentage = int((idx / total_files) * 100)
            print(f"Πρόοδος: {progress_percentage}%")
        except Exception as e:
            db.rollback()
            print(f"Σφάλμα στο αρχείο {file_path}: {e}")

    with processing_lock:
        running = False
        paused = False
        stopped = False
        progress_percentage = 100
        print("Επεξεργασία ολοκληρώθηκε ή τερματίστηκε.")


def start_processing_thread(files):
    global processing_thread, running, paused, stopped, progress_percentage
    with processing_lock:
        if running:
            return False
        running = True
        paused = False
        stopped = False
        progress_percentage = 0
    processing_thread = threading.Thread(target=process_files, args=(files,))
    processing_thread.start()
    return True


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload_folder', methods=['POST'])
def upload_folder():
    files = request.files.getlist('files')

    if not files:
        return jsonify({'message': 'Δεν επιλέχθηκαν αρχεία.'}), 400

    folder_path = os.path.join('uploaded_files')
    os.makedirs(folder_path, exist_ok=True)

    saved_files = []
    try:
        for file in files:
            file_path = os.path.join(folder_path, file.filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
            saved_files.append(file_path)
    except Exception as e:
        return jsonify({'message': f'Σφάλμα κατά την αποθήκευση: {str(e)}'}), 500

    # Ξεκίνα τη διαδικασία σε thread
    started = start_processing_thread(saved_files)
    if not started:
        return jsonify({'message': 'Η επεξεργασία ήδη τρέχει.'}), 400

    return jsonify({'message': f'Ξεκίνησε η επεξεργασία {len(saved_files)} αρχείων.'})


@app.route('/control', methods=['POST'])
def control():
    global running, paused, stopped
    data = request.json
    action = data.get('action')

    with processing_lock:
        if action == 'pause' and running and not paused:
            paused = True
            return jsonify({'message': 'Η επεξεργασία σταμάτησε προσωρινά.'})
        elif action == 'continue' and running and paused:
            paused = False
            return jsonify({'message': 'Η επεξεργασία συνεχίζεται.'})
        elif action == 'stop' and running:
            stopped = True
            paused = False
            return jsonify({'message': 'Η επεξεργασία τερματίστηκε.'})
        else:
            return jsonify({'message': 'Μη έγκυρη ενέργεια ή η επεξεργασία δεν τρέχει.'}), 400


@app.route('/get_progress', methods=['GET'])
def get_progress():
    global progress_percentage, running, paused
    status = 'running' if running else 'stopped'
    if paused:
        status = 'paused'
    return jsonify({'progress': progress_percentage, 'status': status})
@app.route('/query_documents', methods=['POST'])
def query_documents():
    try:
        data = request.json or {}
        query_type = data.get('queryType', 'all')

        if query_type == 'did_only':
            cursor.execute("SELECT did FROM document")
            rows = cursor.fetchall()
            results = [{"did": row[0]} for row in rows]
        else:
            cursor.execute("SELECT did, ucid, doc_number, date FROM document")
            rows = cursor.fetchall()
            results = []
            for row in rows:
                results.append({
                    "did": row[0],
                    "ucid": row[1],
                    "doc_number": row[2],
                    "date": row[3]
                })

        return jsonify({"results": results})
    except Exception as e:
        print(f"Error in /query_documents: {e}")
        return jsonify({"results": []}), 500


if __name__ == '__main__':
    initialize_state(cursor, db)
    initialize_format(cursor, db)
    initialize_loadsource(cursor, db)
    initialize_kind(cursor, db)
    initialize_scheme(cursor, db)
    initialize_role(cursor, db)
    initialize_status(cursor, db)


    app.run(debug=True)
