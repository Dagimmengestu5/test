import os
from flask import Flask, send_file, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configure your base directory here
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'MekaneHeywetFiles')
# BASE_DIR = os.path.join(os.path.expanduser('~'), 'MekaneHeywetFiles')  # Change this to your actual folder path

# Password protection
VALID_PASSWORDS = [
    "dagi", "Dagi", "mekane heywet", "mekaneheywet",
    "Mekane heywet", "Mekane Heywet", "MEKANE HEYWET",
    "መካነ ሕይወት", "መካነ ህይወት", "መካነሕይወት", "2017"
]


@app.route('/')
def index():
    return send_file('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)
@app.route('/api/check-auth')
def check_auth():
    auth_token = request.cookies.get('auth_token')
    if auth_token in VALID_PASSWORDS:
        return jsonify({'authenticated': True})
    return jsonify({'authenticated': False}), 401


@app.route('/api/login', methods=['POST'])
def login():
    password = request.json.get('password')
    if password in VALID_PASSWORDS:
        response = jsonify({'success': True})
        response.set_cookie('auth_token', password)
        return response
    return jsonify({'error': 'Invalid password'}), 401


@app.route('/api/view')
def view_file():
    auth_token = request.cookies.get('auth_token')
    if auth_token not in VALID_PASSWORDS:
        return jsonify({'error': 'Unauthorized'}), 401

    path = request.args.get('path', '')
    full_path = os.path.join(BASE_DIR, path)

    if not os.path.exists(full_path):
        return jsonify({'error': 'File not found'}), 404

    if os.path.isdir(full_path):
        return jsonify({'error': 'Cannot view directory'}), 400

    try:
        # For browsers that can display the file directly
        return send_file(full_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/list')
def list_files():
    auth_token = request.cookies.get('auth_token')
    if auth_token not in VALID_PASSWORDS:
        return jsonify({'error': 'Unauthorized'}), 401

    path = request.args.get('path', '')
    full_path = os.path.join(BASE_DIR, path)

    if not os.path.exists(full_path):
        return jsonify({'error': 'Directory not found'}), 404

    if not os.path.isdir(full_path):
        return jsonify({'error': 'Path is not a directory'}), 400

    try:
        items = os.listdir(full_path)
        folders = []
        files = []

        for item in items:
            item_path = os.path.join(full_path, item)
            if os.path.isdir(item_path):
                folders.append(item)
            else:
                files.append({
                    'name': item,
                    'size': os.path.getsize(item_path)
                })

        # Sort folders and files naturally
        def natural_sort_key(s):
            import re
            return [int(text) if text.isdigit() else text.lower()
                    for text in re.split('([0-9]+)', s)]

        folders.sort(key=natural_sort_key)
        files.sort(key=lambda x: natural_sort_key(x['name']))

        return jsonify({
            'folders': folders,
            'files': files
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download')
def download_file():
    auth_token = request.cookies.get('auth_token')
    if auth_token not in VALID_PASSWORDS:
        return jsonify({'error': 'Unauthorized'}), 401

    path = request.args.get('path', '')
    full_path = os.path.join(BASE_DIR, path)

    if not os.path.exists(full_path):
        return jsonify({'error': 'File not found'}), 404

    if os.path.isdir(full_path):
        return jsonify({'error': 'Cannot download directory'}), 400

    try:
        # Universal solution for all Flask versions
        response = send_file(
            full_path,
            as_attachment=True
        )
        # Manually set the download filename
        response.headers["Content-Disposition"] = f"attachment; filename={os.path.basename(full_path)}"
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_directory_structure():
    # Create the base directory if it doesn't exist
    os.makedirs(BASE_DIR, exist_ok=True)

    # Create subfolders if they don't exist
    main_folders = ["መሰረተ ትምሕርት", "ቤተ ዜማ", "ሥርዓተ ቅዳሴ"]
    weekday_order = [
        "፮.መዝሙረ ዳዊት", "፭.መልክዐ ኢየሰስ", "፬.መልክዐ ማርያም",
        "፫.አንቀፀ ብርሃን", "፪.ውዳሴ ማርያም", "፩.የዘወትር ፀሎት"
    ]

    for folder in main_folders:
        os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

    for day in weekday_order:
        os.makedirs(os.path.join(BASE_DIR, "መሰረተ ትምሕርት", day), exist_ok=True)


if __name__ == '__main__':
    create_directory_structure()
    app.run(host='0.0.0.0', port=5000, debug=True)