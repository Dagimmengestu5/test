import os
import re
from functools import wraps
from flask import Flask, send_file, jsonify, request, send_from_directory, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import mimetypes

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app, supports_credentials=True)

# Configuration
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'MekaneHeywetFiles')
VALID_PASSWORDS = [
    "dagi", "Dagi", "mekane heywet", "mekaneheywet",
    "Mekane heywet", "Mekane Heywet", "MEKANE HEYWET",
    "መካነ ሕይወት", "መካነ ህይወት", "መካነሕይወት", "2017"
]
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Supported preview file types
PREVIEW_TYPES = {
    'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'],
    'pdf': ['pdf'],
    'audio': ['mp3', 'wav', 'ogg', 'm4a'],
    'video': ['mp4', 'webm', 'ogg'],
    'text': ['txt', 'csv', 'json', 'xml', 'md']
}

# Initialize mimetypes
mimetypes.add_type('application/pdf', '.pdf')

# Helper functions


def get_safe_path(requested_path):
    requested_path = requested_path.lstrip('/')
    full_path = os.path.join(BASE_DIR, requested_path)
    full_path = os.path.normpath(full_path)

    if not full_path.startswith(os.path.abspath(BASE_DIR)):
        return None
    return full_path


def get_file_type(filename):
    ext = filename.split('.')[-1].lower()
    for file_type, extensions in PREVIEW_TYPES.items():
        if ext in extensions:
            return file_type
    return 'other'


# Authentication decorator
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_token = request.cookies.get('auth_token')
        if auth_token not in VALID_PASSWORDS:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)

    return decorated_function


# Routes
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


# API Routes
@app.route('/api/check-auth')
def check_auth():
    auth_token = request.cookies.get('auth_token')
    if auth_token in VALID_PASSWORDS:
        return jsonify({'authenticated': True})
    return jsonify({'authenticated': False})


@app.route('/api/login', methods=['POST'])
def login():
    password = request.json.get('password')
    if password in VALID_PASSWORDS:
        response = jsonify({'success': True})
        response.set_cookie('auth_token', password, httponly=True, samesite='Lax')
        return response
    return jsonify({'error': 'Invalid password'}), 401


@app.route('/api/list')
@auth_required
def list_files():
    path = request.args.get('path', '')
    full_path = get_safe_path(path)

    if not full_path:
        return jsonify({'error': 'Invalid path'}), 400

    if not os.path.exists(full_path):
        return jsonify({'error': 'Path not found'}), 404

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
                    'size': os.path.getsize(item_path),
                    'type': get_file_type(item),
                    'path': os.path.join(path, item).replace('\\', '/')
                })

        folders.sort(key=lambda x: x.lower())
        files.sort(key=lambda x: x['name'].lower())

        return jsonify({
            'path': path,
            'folders': folders,
            'files': files
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/view')
@auth_required
def view_file():
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({'error': 'Path parameter is required'}), 400

    full_path = get_safe_path(file_path)
    if not full_path:
        return jsonify({'error': 'Invalid path'}), 400

    if not os.path.exists(full_path):
        return jsonify({'error': 'File not found'}), 404

    if os.path.isdir(full_path):
        return jsonify({'error': 'Cannot view directory'}), 400

    try:
        mime_type, _ = mimetypes.guess_type(full_path)
        if not mime_type:
            mime_type = 'application/octet-stream'

        # Special handling for PDFs in Telegram Web
        user_agent = request.headers.get('User-Agent', '').lower()
        is_telegram = 'telegram' in user_agent

        if full_path.lower().endswith('.pdf'):
            if is_telegram:
                # For Telegram Web, we need to force the PDF to open in the browser
                response = send_file(
                    full_path,
                    mimetype=mime_type,
                    conditional=True
                )
                response.headers['Content-Disposition'] = 'inline; filename="{}"'.format(os.path.basename(full_path))
                response.headers['X-Content-Type-Options'] = 'nosniff'
                return response
            else:
                # For regular browsers
                response = send_file(
                    full_path,
                    mimetype=mime_type,
                    conditional=True
                )
                response.headers['Content-Disposition'] = 'inline'
                return response

        # For other file types that browsers can display directly
        if mime_type.startswith(('image/', 'text/', 'video/', 'audio/')):
            response = send_file(
                full_path,
                mimetype=mime_type,
                conditional=True
            )
            response.headers['Content-Disposition'] = 'inline'
            return response

        # For other file types, force download
        return send_file(
            full_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=os.path.basename(full_path)
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/preview')
@auth_required
def preview_file():
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({'error': 'Path parameter is required'}), 400

    full_path = get_safe_path(file_path)
    if not full_path:
        return jsonify({'error': 'Invalid path'}), 400

    if not os.path.exists(full_path):
        return jsonify({'error': 'File not found'}), 404

    if os.path.isdir(full_path):
        return jsonify({'error': 'Cannot preview directory'}), 400

    file_type = get_file_type(full_path)

    try:
        if file_type == 'other':
            return jsonify({'error': 'Preview not available for this file type'}), 400

        mime_type, _ = mimetypes.guess_type(full_path)
        if not mime_type:
            mime_type = 'application/octet-stream'

        # Special handling for PDF preview in Telegram
        user_agent = request.headers.get('User-Agent', '').lower()
        is_telegram = 'telegram' in user_agent

        if file_type == 'pdf' and is_telegram:
            response = send_file(
                full_path,
                mimetype=mime_type,
                conditional=True
            )
            response.headers['Content-Disposition'] = 'inline; filename="{}"'.format(os.path.basename(full_path))
            return response

        return send_file(full_path, mimetype=mime_type)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stream')
@auth_required
def stream_file():
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({'error': 'Path parameter is required'}), 400

    full_path = get_safe_path(file_path)
    if not full_path:
        return jsonify({'error': 'Invalid path'}), 400

    if not os.path.exists(full_path):
        return jsonify({'error': 'File not found'}), 404

    if os.path.isdir(full_path):
        return jsonify({'error': 'Cannot stream directory'}), 400

    range_header = request.headers.get('Range', None)
    file_size = os.path.getsize(full_path)
    mime_type, _ = mimetypes.guess_type(full_path)

    if not mime_type:
        mime_type = 'application/octet-stream'

    if not range_header:
        response = send_file(
            full_path,
            mimetype=mime_type,
            conditional=True
        )
        response.headers['Accept-Ranges'] = 'bytes'
        return response

    byte1, byte2 = 0, None
    range_ = range_header.split('bytes=')[1].split('-')
    byte1 = int(range_[0])
    if len(range_) == 2:
        byte2 = int(range_[1]) if range_[1] else file_size - 1

    length = byte2 - byte1 + 1 if byte2 else file_size - byte1

    with open(full_path, 'rb') as f:
        f.seek(byte1)
        data = f.read(length)

    response = Response(
        data,
        206,
        mimetype=mime_type,
        direct_passthrough=True
    )

    response.headers.add('Content-Range', f'bytes {byte1}-{byte2 if byte2 else file_size - 1}/{file_size}')
    response.headers.add('Accept-Ranges', 'bytes')
    response.headers.add('Content-Length', str(length))

    return response


@app.route('/api/download')
@auth_required
def download_file():
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({'error': 'Path parameter is required'}), 400

    full_path = get_safe_path(file_path)
    if not full_path:
        return jsonify({'error': 'Invalid path'}), 400

    if not os.path.exists(full_path):
        return jsonify({'error': 'File not found'}), 404

    if os.path.isdir(full_path):
        return jsonify({'error': 'Cannot download directory'}), 400

    try:
        mime_type, _ = mimetypes.guess_type(full_path)
        if not mime_type:
            mime_type = 'application/octet-stream'

        return send_file(
            full_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=os.path.basename(full_path))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    os.makedirs(BASE_DIR, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)