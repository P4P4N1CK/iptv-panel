from flask import Flask, request, Response, jsonify, redirect
from flask_sslify import SSLify
import json
import uuid
from urllib.parse import urlparse
import re
import ssl
from datetime import datetime, timedelta
import random
import string
import os
import requests
import sys

app = Flask(__name__)
sslify = SSLify(app)

def get_external_ip():
    try:
        response = requests.get("https://ipv4.icanhazip.com")
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Error fetching external IP: {e}")
        sys.exit(1)

def load_config(file_path="data.txt"):
    config = {}

    # Fetch license content from the provided URL
    license_url = "https://raw.githubusercontent.com/syfqsamvpn/iptv/main/panel_access.txt"
    try:
        response = requests.get(license_url)
        license_content = response.text
    except requests.RequestException as e:
        print(f"Error fetching license content: {e}")
        sys.exit(1)

    # Fetch the external IP of the server
    server_ip = get_external_ip()
    if server_ip is None or server_ip not in license_content:
        print("Server IP not authorized. Check your license.")
        sys.exit(1)

    # Load the rest of the configuration from the file
    with open(file_path, "r") as data_file:
        file_content = data_file.read()
        exec(file_content, config)

    return config

config = load_config()

m3u_base = config.get("m3u_base", "")
m3u_host = urlparse(m3u_base).netloc

admin_pass = config.get("admin_pass", "")
redirect_url = config.get("redirect_url", "")
TELEGRAM_BOT_TOKEN = config.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = config.get("TELEGRAM_CHANNEL_ID", "")
USER_IPTV_FILE = config.get("USER_IPTV_FILE", "")
USER_LOG_FILE = config.get("USER_LOG_FILE", "")
RESELLER_FILE = config.get("RESELLER_FILE", "")
SNIFFER_DATA_FILE = config.get("SNIFFER_DATA_FILE", "")
MULTILOGIN_DATA_FILE = config.get("MULTILOGIN_DATA_FILE", "")
SECURE_SHORT_FILE = config.get("SECURE_SHORT_FILE", "")
SECURE_REDIRECT = config.get("SECURE_REDIRECT", "")
OTT_FILE = config.get("OTT_FILE", "")
EXPIRED_FILE = config.get("EXPIRED_FILE", "")
BANNED_FILE = config.get("BANNED_FILE", "")
STORAGE_FILE = config.get("STORAGE_FILE", "")
EXPIRED_DATA = config.get("EXPIRED_DATA", "")
SAFE_LOGIN = config.get("SAFE_LOGIN", "")
CRITICAL_LOGIN = config.get("CRITICAL_LOGIN", "")
DURATION_LOG = config.get("DURATION_LOG", "")
package_info = config.get("package_info", {})
tele_api_url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'


def load_short_links():
    try:
        with open(STORAGE_FILE, "r") as file:
            data = file.read()
            if data:
                return json.loads(data)
            else:
                return {}
    except FileNotFoundError:
        return {}
    
def load_sniff_links():
    try:
        with open(SNIFFER_DATA_FILE, "r") as file:
            data = file.read()
            if data:
                return json.loads(data)
            else:
                return {}
    except FileNotFoundError:
        return {}
    
def load_multi_links():
    try:
        with open(MULTILOGIN_DATA_FILE, "r") as file:
            data = file.read()
            if data:
                return json.loads(data)
            else:
                return {}
    except FileNotFoundError:
        return {}
    
def load_playlist_links():
    try:
        with open(SECURE_SHORT_FILE, "r") as file:
            data = file.read()
            if data:
                return json.loads(data)
            else:
                return {}
    except FileNotFoundError:
        return {}
    
def shorten_with_tny(url):
    tny_api_url = f"http://tny.im/yourls-api.php?action=shorturl&format=simple&url={url}"
    response = requests.get(tny_api_url)

    if response.status_code == 200:
        return response.text.strip()
    else:
        return url

def save_short_links(short_links):
    try:
        with open(STORAGE_FILE, "w") as file:
            if not short_links:
                return {}
            json.dump(short_links, file)
    except FileNotFoundError:
        return {}
    
def save_secure_links(short_links):
    try:
        with open(SECURE_SHORT_FILE, "w") as file:
            if not short_links:
                return {}
            json.dump(short_links, file)
    except FileNotFoundError:
        return {}

def read_m3u_file(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()
    return file_content

def move_to_expired(username, user_uuid):
    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        users = []

    try:
        with open(EXPIRED_DATA, 'r') as expired_file:
            expireds = json.load(expired_file)
    except json.decoder.JSONDecodeError:
        expireds = []


    for user_info in users:
        if user_info['username'] == username and user_info.get('uuid') == user_uuid:
            expiration_date_str = user_info.get('expiration_date', '')
            if expiration_date_str:
                expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d %H:%M:%S')
                current_date = datetime.now()
                if current_date > expiration_date:
                    expireds.append(user_info)
            continue

    #updated_users = [user for user in users if user not in expireds]

    with open(EXPIRED_DATA, 'w') as expired_file:
        json.dump(expireds, expired_file)

def is_valid_user(username, user_uuid):
    with open(USER_IPTV_FILE, 'r') as user_file:
        users = json.load(user_file)

    for user_info in users:
        if user_info['username'] == username:
            valid_uuid = user_info.get('uuid', '')
            if user_uuid == valid_uuid:
                expiration_date_str = user_info.get('expiration_date', '')
                if expiration_date_str:
                    expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d %H:%M:%S')
                    current_date = datetime.now()
                    if current_date <= expiration_date:
                        return True
                    else:
                        move_to_expired(username, user_uuid)
                        return False
    return False

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def is_username_taken(username):
    try:
        with open(RESELLER_FILE, 'r') as reseller_file:
            resellers = json.load(reseller_file)
            usernames = [reseller['username'] for reseller in resellers]
            return username in usernames
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return False

def register_reseller(username, balance):
    if is_username_taken(username):
        return False
    password = generate_random_password()
    reseller_info = {'username': username, 'password': password, 'balance': balance}
    
    try:
        with open(RESELLER_FILE, 'r') as reseller_file:
            resellers = json.load(reseller_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        resellers = []

    resellers.append(reseller_info)

    with open(RESELLER_FILE, 'w') as reseller_file:
        json.dump(resellers, reseller_file, indent=None)

    return password

def is_valid_reseller(username, password):
    try:
        if not os.path.exists(RESELLER_FILE):
            with open(RESELLER_FILE, 'w') as empty_file:
                json.dump([], empty_file)
        
        with open(RESELLER_FILE, 'r') as reseller_file:
            resellers = json.load(reseller_file)
            
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return False
    
    for reseller_info in resellers:
        if reseller_info['username'] == username and reseller_info['password'] == password:
            return True

    return False

def get_user_info_by_uuid(user_uuid):
    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        users = []

    for user_info in users:
        if user_info.get('uuid') == user_uuid:
            return user_info

    return None

def get_expired_info_by_uuid(user_uuid):
    try:
        with open(EXPIRED_DATA, 'r') as user_file:
            users = json.load(user_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        users = []

    for user_info in users:
        if user_info.get('uuid') == user_uuid:
            return user_info

    return None

def renew_user_expiration(current_date, days):
    current_date = datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
    new_expiration_date = current_date + timedelta(days=days)
    return new_expiration_date.strftime('%Y-%m-%d %H:%M:%S')

def get_reseller_info(username):
    try:
        with open(RESELLER_FILE, 'r') as reseller_file:
            resellers = json.load(reseller_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return None

    for reseller_info in resellers:
        if reseller_info['username'] == username:
            return reseller_info

    return None

def update_user_info(updated_info):
    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        users = []

    for i, user_info in enumerate(users):
        if user_info['username'] == updated_info['username'] and user_info.get('uuid') == updated_info.get('uuid'):
            users[i] = updated_info

    with open(USER_IPTV_FILE, 'w') as user_file:
        json.dump(users, user_file, indent=None)

def update_reseller_info(updated_info):
    try:
        with open(RESELLER_FILE, 'r') as reseller_file:
            resellers = json.load(reseller_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        resellers = []

    for i, reseller_info in enumerate(resellers):
        if reseller_info['username'] == updated_info['username']:
            resellers[i] = updated_info

    with open(RESELLER_FILE, 'w') as reseller_file:
        json.dump(resellers, reseller_file, indent=None)

def log_user_info(user_id, user_uuid, reseller_username=None):
    user_info = {
        'user_id': user_id,
        'user_uuid': user_uuid,
        'ip_address': request.remote_addr,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'reseller_username': reseller_username
    }

    try:
        with open(USER_LOG_FILE, 'r') as log_file:
            user_logs = json.load(log_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        user_logs = []

    user_logs.append(user_info)

    with open(USER_LOG_FILE, 'w') as log_file:
        json.dump(user_logs, log_file, indent=None)

def check_multilogin(user_uuid):
    try:
        with open(USER_LOG_FILE, 'r') as log_file:
            user_logs = json.load(log_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return jsonify({'error': 'Log file not found or empty'}), 200

    user_info_list = []
    unique_user_ids = set()
    reseller_usernames = set()

    for user_info in user_logs:
        if user_info['user_uuid'] == user_uuid:
            user_id = user_info['user_id']
            reseller_username = user_info.get('reseller_username', 'N/A')
            reseller_usernames.add(reseller_username)
            unique_user_ids.add(user_id)
            user_info_list.append({
                'user_id': user_id,
                'ip_address': user_info['ip_address'],
                'timestamp': user_info['timestamp'],
                'reseller_username': reseller_username
            })

    if not user_info_list:
        return jsonify({'message': 'No log entries found for the specified user_uuid'}), 200
    else:
        if len(unique_user_ids) <= SAFE_LOGIN:
            return jsonify({
                'user_info_list': user_info_list,
                'message': 'Safe'
            }), 200
        elif len(unique_user_ids) >= CRITICAL_LOGIN:
            return jsonify({
                'user_info_list': user_info_list,
                'message': 'Critical'
            }), 200
        else:
            return jsonify({
                'user_info_list': user_info_list,
                'message': 'Unsafe'
            }), 200
        
def check_all_multilogin():
    try:
        with open(USER_LOG_FILE, 'r') as log_file:
            user_logs = json.load(log_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return jsonify({'error': 'Log file not found or empty'}), 404

    uuid_states = {}

    for user_info in user_logs:
        user_uuid = user_info['user_uuid']
        user_id = user_info['user_id']
        unique_user_ids = uuid_states.get(user_uuid, set())
        unique_user_ids.add(user_id)
        uuid_states[user_uuid] = unique_user_ids

    critical_uuids = {uuid: len(user_ids) for uuid, user_ids in uuid_states.items() if len(user_ids) >= 3}

    return jsonify({'critical_uuids': critical_uuids, 'message': 'UUIDs with critical state'})

def delete_old_logs():
    try:
        with open(USER_LOG_FILE, 'r') as log_file:
            user_logs = json.load(log_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return

    current_date = datetime.now()

    user_logs = [log for log in user_logs if current_date - datetime.strptime(log['timestamp'], '%Y-%m-%d %H:%M:%S') <= timedelta(days=DURATION_LOG)]

    with open(USER_LOG_FILE, 'w') as log_file:
        json.dump(user_logs, log_file, indent=None)

def delete_short_link(username, user_uuid, storage_file_path):
    try:
        with open(storage_file_path, 'r') as STORAGE_FILE:
            short_links = json.load(STORAGE_FILE)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return

    short_links_copy = short_links.copy()

    for short_id, long_url in short_links_copy.items():
        if f"iptv?id={username}&uuid={user_uuid}" in long_url:
            del short_links[short_id]

    with open(storage_file_path, 'w') as STORAGE_FILE:
        json.dump(short_links, STORAGE_FILE)

def remove_entries_from_user_log(user_uuid):
    try:
        with open(USER_LOG_FILE, 'r') as log_file:
            user_logs = json.load(log_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return

    updated_logs = [log for log in user_logs if log['user_uuid'] != user_uuid]

    with open(USER_LOG_FILE, 'w') as log_file:
        json.dump(updated_logs, log_file, indent=None)

def remove_entries_from_expired_data(user_uuid):
    try:
        with open(EXPIRED_DATA, 'r') as log_file:
            user_logs = json.load(log_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return

    updated_logs = [log for log in user_logs if log['uuid'] != user_uuid]

    with open(EXPIRED_DATA, 'w') as log_file:
        json.dump(updated_logs, log_file, indent=None)

def delete_multi_from_file(username, user_uuid, ip_address):
    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return

    deleted_user = None
    updated_users = []

    for user in users:
        if user['username'] == username and user.get('uuid') == user_uuid:
            deleted_user = user
        else:
            updated_users.append(user)

    with open(USER_IPTV_FILE, 'w') as user_file:
        json.dump(updated_users, user_file, indent=None)

    if deleted_user:
        try:
            with open(MULTILOGIN_DATA_FILE, 'r') as multilogin_file:
                multilogin_data = json.load(multilogin_file)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            multilogin_data = []

        deleted_user['ip_address'] = ip_address
        multilogin_data.append(deleted_user)

        with open(MULTILOGIN_DATA_FILE, 'w') as multilogin_file:
            json.dump(multilogin_data, multilogin_file, indent=None)

        delete_short_link(username, user_uuid, STORAGE_FILE)
        remove_entries_from_user_log(user_uuid)
        message_text = f"User {username} has been banned\nReason : Multilogin\nIP: {ip_address}"
        params = {'chat_id': TELEGRAM_CHANNEL_ID, 'text': message_text}
        response = requests.post(tele_api_url, params=params)

def delete_sniffer_from_file(username, user_uuid, ip_address):
    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return

    deleted_user = None
    updated_users = []

    for user in users:
        if user['username'] == username and user.get('uuid') == user_uuid:
            deleted_user = user
        else:
            updated_users.append(user)

    with open(USER_IPTV_FILE, 'w') as user_file:
        json.dump(updated_users, user_file, indent=None)

    if deleted_user:
        try:
            with open(SNIFFER_DATA_FILE, 'r') as sniffer_file:
                sniffer_data = json.load(sniffer_file)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            sniffer_data = []

        deleted_user['ip_address'] = ip_address
        sniffer_data.append(deleted_user)

        with open(SNIFFER_DATA_FILE, 'w') as sniffer_file:
            json.dump(sniffer_data, sniffer_file, indent=None)

        delete_short_link(username, user_uuid, STORAGE_FILE)

        # Remove corresponding entries from USER_LOG_FILE
        remove_entries_from_user_log(user_uuid)
        message_text = f"User {username} has been banned\nReason : Sniffing\nIP: {ip_address}"
        params = {'chat_id': TELEGRAM_CHANNEL_ID, 'text': message_text}
        response = requests.post(tele_api_url, params=params)

def delete_user_from_file(username, user_uuid):
    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return

    updated_users = []
    user_deleted = False

    for user in users:
        if user['username'] == username and user.get('uuid') == user_uuid:
            user_deleted = True
            continue
        updated_users.append(user)

    if user_deleted:
        with open(USER_IPTV_FILE, 'w') as user_file:
            json.dump(updated_users, user_file, indent=None)

        delete_short_link(username, user_uuid, STORAGE_FILE)
        remove_entries_from_user_log(user_uuid)

        return True
    else:
        return False

@app.route('/api/get_user_data', methods=['GET'])
def get_user_data():
    user_uuid = request.args.get('user_uuid')
    password_input = request.args.get('password_input')

    if not user_uuid or not password_input:
        return jsonify({'error': 'Missing user_uuid or password_input parameter'}), 400

    if password_input != admin_pass:
        return jsonify({'error': 'wrong password'}), 400

    user_data = get_user_info_by_uuid(user_uuid)
    if not user_data:
        return jsonify({'error': 'User not found'}), 404

    if not user_data:
        try:
            with open(SNIFFER_DATA_FILE, 'r') as sniffer_file:
                sniffer_data = json.load(sniffer_file)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            sniffer_data = []

        for sniffer_user in sniffer_data:
            if sniffer_user.get('uuid') == user_uuid:
                return jsonify({'message': 'Banned ID', 'reason': 'sniffing'}), 403

    if user_data:
        return jsonify(user_data)
    else:
        return jsonify({'error': 'User with the specified UUID not found'}), 404

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()

    if 'url' not in data:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    long_url = data['url']
    short_id = str(uuid.uuid4())[:8]
    short_links = load_short_links()
    short_url = f"{m3u_base}/{short_id}"
    short_links[short_id] = long_url
    save_short_links(short_links)
    tny_url = shorten_with_tny(short_url)

    return jsonify({"short_url": tny_url}), 201

@app.route('/secure', methods=['POST'])
def secure_shorten_url():
    data = request.get_json()

    if 'url' not in data or 'short_id' not in data:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    long_url = data['url']
    short_id = data['short_id']
    short_links = load_playlist_links()
    if short_id in str(short_links):
        return jsonify({"error": f"Short ID '{short_id}' already exist"}), 404
    short_url = f"{m3u_base}/{short_id}"
    short_links[short_id] = long_url
    save_secure_links(short_links)

    return jsonify({"short_url": short_url}), 201

@app.route('/secure_edit', methods=['POST'])
def edit_url():
    data = request.get_json()

    if 'url' not in data or 'short_id' not in data:
        return jsonify({"error": "Missing 'url' or 'short_id' parameter"}), 400

    new_url = data['url']
    short_id = data['short_id']
    short_links = load_playlist_links()

    if short_id not in short_links:
        return jsonify({"error": f"Short ID '{short_id}' not found"}), 404

    short_links[short_id] = new_url
    save_secure_links(short_links)

    return jsonify({"message": f"URL for short ID '{short_id}' successfully updated"}), 200

@app.route('/<short_id>', methods=['GET'])
def redirect_to_long_url(short_id):
    headers = request.headers
    connection = request.headers.get('Connection', '')
    host = request.headers.get('Host', '')
    #request_details = {
    #    'Method': request.method,
    #    'Path': request.path,
    #    'Headers': dict(request.headers),
    #    'Query Parameters': dict(request.args),
    #    'Form Data': dict(request.form),
    #    'Cookies': dict(request.cookies),
    #    'Remote Address': request.remote_addr,
    #    'User Agent': request.user_agent.string,
    #    'Scheme': request.scheme
    #}
    #print(request_details)
    play_list = load_playlist_links()
    short_links = load_short_links()
    sniff_links = load_sniff_links()
    multi_links = load_multi_links()
    if short_id in str(play_list):
        if "Accept" in headers and connection == "Keep-Alive" and host == m3u_host:
            return Response("Sniff apa tu abe", status=403)
        elif connection == "Keep-Alive" and host == m3u_host:
            long_url = play_list[short_id]
            return redirect(long_url, code=302)
        else:
            return redirect(SECURE_REDIRECT, code=302)
    elif short_id in str(sniff_links):
        file_content = read_m3u_file(BANNED_FILE)
        return Response(file_content, content_type='text/plain;charset=utf-8')
    elif short_id in str(multi_links):
        file_content = read_m3u_file(BANNED_FILE)
        return Response(file_content, content_type='text/plain;charset=utf-8')
    elif short_id in str(short_links):
        long_url = short_links[short_id]
        return redirect(long_url, code=302)
    else:
        file_content = read_m3u_file(EXPIRED_FILE)
        return Response(file_content, content_type='text/plain;charset=utf-8')

@app.route('/api/register_reseller', methods=['POST'])
def add_reseller():
    data = request.json
    if 'username' not in data or 'balance' not in data or data['password'] != admin_pass:
        return jsonify({'error': 'Got missing or false data'}), 400
    username = data['username']
    balance = data['balance']
    
    password = register_reseller(username, balance)
    if password:
        return jsonify({'username': username, 'password': password, 'message': 'Reseller registered successfully'})
    else:
        return jsonify({'error': 'Username already exist'}), 400

@app.route('/api/delete_reseller', methods=['POST'])  
def delete_reseller():
    data = request.json

    required_fields = ['username', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Required data is missing'}), 400

    admin_password = data['password']
    if admin_password != admin_pass:
        return jsonify({'error': 'Invalid admin password'}), 401

    username = data['username']

    try:
        with open(RESELLER_FILE, 'r') as reseller_file:
            resellers = json.load(reseller_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        resellers = []

    updated_resellers = [reseller for reseller in resellers if reseller['username'] != username]

    if len(updated_resellers) == len(resellers):
        return jsonify({'error': f'Reseller {username} not found'}), 404

    with open(RESELLER_FILE, 'w') as reseller_file:
        json.dump(updated_resellers, reseller_file, indent=None)

    return jsonify({'message': f'Reseller {username} deleted successfully'})

@app.route('/api/add_user', methods=['POST'])
def add_user():
    data = request.json

    required_fields = ['username', 'reseller_username', 'reseller_password', 'package']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Required data is missing'}), 400

    reseller_username = data['reseller_username']
    reseller_password = data['reseller_password']

    if not is_valid_reseller(reseller_username, reseller_password):
        return jsonify({'error': 'Invalid reseller credentials'}), 401

    username = data['username']
    package = data['package']

    if package not in package_info:
        return jsonify({'error': 'Invalid package'}), 400

    total_cost = package_info[package]['price']
    days_valid = package_info[package]['days']

    reseller_info = get_reseller_info(reseller_username)
    if not reseller_info or reseller_info['balance'] < total_cost:
        return jsonify({'error': 'Insufficient balance'}), 400

    reseller_info['balance'] -= total_cost
    balance = reseller_info['balance']

    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except json.decoder.JSONDecodeError:
        users = []

    if username in [user_info['username'] for user_info in users]:
        return jsonify({'error': 'User already exists'}), 400

    user_uuid = str(uuid.uuid4())
    expiration_date = (datetime.now() + timedelta(days=days_valid)).strftime('%Y-%m-%d %H:%M:%S')
    m3u_link = f"{m3u_base}/iptv?id={username}&uuid={user_uuid}"
    short_id = str(uuid.uuid4())[:8]
    short_links = load_short_links()
    short_url = f"{m3u_base}/{short_id}"
    short_links[short_id] = m3u_link
    user_info = {'username': username, 'expiration_date': expiration_date, 'uuid': user_uuid, 'reseller_username': reseller_username, 'link': short_url}
    users.append(user_info)

    with open(USER_IPTV_FILE, 'w') as user_file:
        json.dump(users, user_file)

    save_short_links(short_links)
    tny_url = shorten_with_tny(short_url)
    update_reseller_info(reseller_info)

    return jsonify({'username': username, 'expiration_date': expiration_date, 'uuid': user_uuid, 'reseller_username': reseller_username, 'link': tny_url, 'balance': balance, 'message': 'User added successfully'})

@app.route('/api/add_user_custom', methods=['POST'])
def add_user_custom():
    data = request.json

    required_fields = ['username', 'reseller_username', 'reseller_password', 'admin_password', 'days']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Required data is missing'}), 400

    reseller_username = data['reseller_username']
    reseller_password = data['reseller_password']

    admin_password = data['admin_password']
    if admin_password != admin_pass:
        return jsonify({'error': 'Invalid admin password'}), 401

    if not is_valid_reseller(reseller_username, reseller_password):
        return jsonify({'error': 'Invalid reseller credentials'}), 401

    username = data['username']
    days_valid = data['days']
    total_cost = 0

    reseller_info = get_reseller_info(reseller_username)
    if not reseller_info or reseller_info['balance'] < total_cost:
        return jsonify({'error': 'Insufficient balance'}), 400

    reseller_info['balance'] -= total_cost
    balance = reseller_info['balance']

    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except json.decoder.JSONDecodeError:
        users = []

    if username in [user_info['username'] for user_info in users]:
        return jsonify({'error': 'User already exists'}), 400

    user_uuid = str(uuid.uuid4())
    expiration_date = (datetime.now() + timedelta(days=days_valid)).strftime('%Y-%m-%d %H:%M:%S')
    m3u_link = f"{m3u_base}/iptv?id={username}&uuid={user_uuid}"
    short_id = str(uuid.uuid4())[:8]
    short_links = load_short_links()
    short_url = f"{m3u_base}/{short_id}"
    short_links[short_id] = m3u_link
    user_info = {'username': username, 'expiration_date': expiration_date, 'uuid': user_uuid, 'reseller_username': reseller_username, 'link': short_url}
    users.append(user_info)

    with open(USER_IPTV_FILE, 'w') as user_file:
        json.dump(users, user_file)

    save_short_links(short_links)
    tny_url = shorten_with_tny(short_url)
    update_reseller_info(reseller_info)

    return jsonify({'username': username, 'expiration_date': expiration_date, 'uuid': user_uuid, 'reseller_username': reseller_username, 'link': tny_url, 'balance': balance, 'message': 'User added successfully'})

@app.route('/api/add_reseller_balance', methods=['POST'])
def add_reseller_balance():
    data = request.json

    required_fields = ['username', 'amount', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Required data is missing'}), 400

    admin_password = data['password']
    if admin_password != admin_pass:
        return jsonify({'error': 'Invalid admin password'}), 401

    reseller_username = data['username']
    amount = data['amount']

    reseller_info = get_reseller_info(reseller_username)
    if not reseller_info:
        return jsonify({'error': 'Reseller not found'}), 404

    reseller_info['balance'] += amount
    update_reseller_info(reseller_info)

    return jsonify({'username': reseller_username, 'new_balance': reseller_info['balance'], 'message': 'Reseller balance added successfully'})

@app.route('/api/renew_user', methods=['POST'])
def renew_user():
    data = request.json

    required_fields = ['uuid','package', 'reseller_username', 'reseller_password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Required data is missing'}), 400

    reseller_username = data['reseller_username']
    reseller_password = data['reseller_password']
    user_uuid = data['uuid']
    package = data['package']
    days = package_info[package]['days']

    if not is_valid_reseller(reseller_username, reseller_password):
        return jsonify({'error': 'Invalid reseller credentials'}), 401

    user_info = get_user_info_by_uuid(user_uuid)
    if not user_info:
        user_info = get_expired_info_by_uuid(user_uuid)
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        expiration_date = renew_user_expiration(current_date, days)
        if not user_info:
            return jsonify({'error': 'User not found'}), 404
        else:
            remove_entries_from_expired_data(user_uuid)
    else:
        expiration_date = renew_user_expiration(user_info['expiration_date'], days)
    if package not in package_info:
        return jsonify({'error': 'Invalid package'}), 400

    total_cost = package_info[package]['price']

    reseller_info = get_reseller_info(reseller_username)
    if not reseller_info:
        return jsonify({'error': 'Reseller not found'}), 404

    if reseller_info['balance'] < total_cost:
        return jsonify({'error': 'Insufficient balance'}), 400

    reseller_info['balance'] -= total_cost
    update_reseller_info(reseller_info)

    user_info['expiration_date'] = expiration_date

    update_user_info(user_info)

    return jsonify({
        'username': user_info['username'],
        'uuid': user_uuid,
        'new_expiration_date': expiration_date,
        'reseller_username': reseller_username,
        'new_reseller_balance': reseller_info['balance'],
        'message': 'User expiration date renewed successfully'
    })


@app.route('/iptv')
def iptv():
    headers = request.headers
    user = request.args.get('id')
    user_uuid = request.args.get('uuid')
    user_agent = request.headers.get('User-Agent', '')
    connection = request.headers.get('Connection', '')
    accept_encoding = request.headers.get('Accept-Encoding', '')
    host = request.headers.get('Host', '')
    pattern = r'\(.*?en;\s*([^)]+)\)$'
    match = re.search(pattern, user_agent)
    if not match:
        pattern = r'\(.*?ms;\s*([^)]+)\)$'
        match = re.search(pattern, user_agent)

    if match:
        user_id = match.group(1).strip()
        if user_id:
            if "Accept" in headers and user_agent.startswith("OTT Navigator") and connection == "Keep-Alive" and accept_encoding == "gzip" and host == m3u_host:
                delete_sniffer_from_file(user, user_uuid, request.remote_addr)
                return Response("Sniff apa tu abe", status=403)
            elif not is_valid_user(user, user_uuid):
                delete_user_from_file(user, user_uuid)
                file_content = read_m3u_file(EXPIRED_FILE)
                return Response(file_content, content_type='text/plain;charset=utf-8')
            elif user_agent.startswith("OTT Navigator") and connection == "Keep-Alive" and accept_encoding == "gzip" and host == m3u_host:
                multilogin_result = check_multilogin(user_uuid)
                response_object = multilogin_result[0]
                json_data = json.loads(response_object.get_data(as_text=True))
                log_user = json.dumps(json_data, indent=2)
                if "Critical" in str(log_user):
                    delete_multi_from_file(user, user_uuid, request.remote_addr)
                    file_exp = read_m3u_file(EXPIRED_FILE)
                    return Response(file_exp, content_type='text/plain;charset=utf-8')
                file_content = read_m3u_file(OTT_FILE)

                try:
                    with open(USER_IPTV_FILE, 'r') as user_file:
                        users = json.load(user_file)
                except (json.decoder.JSONDecodeError, FileNotFoundError):
                    users = []
                reseller_username = None

                for user_info in users:
                    if user_info.get('uuid') == user_uuid:
                        reseller_username = user_info.get('reseller_username', 'N/A')
                        break
                log_user_info(user_id, user_uuid, reseller_username)
                return Response(file_content, content_type='text/plain;charset=utf-8')
            else:
                return redirect(redirect_url, code=302)
        else:
            return Response("Hantuuuuuu", status=403)
    else:
        return redirect(redirect_url, code=302)
    
@app.route('/api/delete_user', methods=['POST'])
def delete_user():
    data = request.json

    required_fields = ['username', 'uuid', 'admin_password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Required data is missing'}), 400

    admin_password = data['admin_password']
    if admin_password != admin_pass:
        return jsonify({'error': 'Invalid admin password'}), 401

    username = data['username']
    user_uuid = data['uuid']

    user_deleted = delete_user_from_file(username, user_uuid)

    if user_deleted:
        return jsonify({'message': f'User {username} with UUID {user_uuid} deleted successfully'})
    else:
        return jsonify({'error': f'User {username} with UUID {user_uuid} not found or mismatch'})

@app.route('/api/get_users_by_reseller', methods=['GET'])
def get_users_by_reseller():
    reseller_username = request.args.get('reseller_username')
    password_input = request.args.get('password_input')

    if not reseller_username or not password_input:
        return jsonify({'error': 'Missing reseller_username or password_input parameter'}), 400

    if password_input != admin_pass:
        return jsonify({'error': 'Invalid admin password'}), 401

    try:
        with open(RESELLER_FILE, 'r') as reseller_file:
            resellers = json.load(reseller_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        resellers = []

    reseller_data = next((reseller for reseller in resellers if reseller['username'] == reseller_username), None)

    if not reseller_data:
        return jsonify({'error': f'Reseller {reseller_username} not found'}), 404

    try:
        with open(USER_IPTV_FILE, 'r') as user_file:
            users = json.load(user_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        users = []

    reseller_users = [{'username': user['username'], 'uuid': user.get('uuid')} for user in users if user.get('reseller_username') == reseller_username]

    # Include reseller balance in the response
    response_data = {
        'reseller_username': reseller_username,
        'balance': reseller_data.get('balance', 0),  # assuming 'balance' is the attribute holding the balance
        'users': reseller_users
    }

    return jsonify(response_data)

@app.route('/api/get_all_resellers', methods=['GET'])
def get_all_resellers():
    password_input = request.args.get('password_input')

    if not password_input:
        return jsonify({'error': 'Missing password_input parameter'}), 400

    if password_input != admin_pass:
        return jsonify({'error': 'Invalid admin password'}), 401

    try:
        with open(RESELLER_FILE, 'r') as reseller_file:
            resellers = json.load(reseller_file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        resellers = []

    reseller_data = []
    for reseller in resellers:
        reseller_username = reseller['username']
        reseller_balance = reseller['balance']
        try:
            with open(RESELLER_FILE, 'r') as reseller_file:
                resellers = json.load(reseller_file)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            resellers = []

        reseller_exists = any(reseller['username'] == reseller_username for reseller in resellers)

        if not reseller_exists:
            return jsonify({'error': f'Reseller {reseller_username} not found'}), 404

        try:
            with open(USER_IPTV_FILE, 'r') as user_file:
                users = json.load(user_file)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            users = []

        reseller_users = [{'username': user['username'], 'uuid': user.get('uuid')} for user in users if user.get('reseller_username') == reseller_username]

        reseller_info = {
            'reseller_username': reseller_username,
            'balance': reseller_balance,
            'users': reseller_users
        }
        reseller_data.append(reseller_info)

    return jsonify({'resellers': reseller_data})

@app.route('/api/check_multilogin', methods=['GET'])
def api_check_multilogin():
    user_uuid = request.args.get('user_uuid')
    password_input = request.args.get('password_input')
    delete_old_logs()
    if not user_uuid or not password_input:
        return jsonify({'error': 'Missing user_uuid or password_input parameter'}), 400

    if password_input != admin_pass:
        return jsonify({'error': 'wrong password'}), 400
    
    return check_multilogin(user_uuid)

@app.route('/api/check_all_multilogin', methods=['GET'])
def api_check_all_multilogin():
    password_input = request.args.get('password_input')
    if not password_input:
        return jsonify({'error': 'Missing password_input parameter'}), 400
    if password_input != admin_pass:
        return jsonify({'error': 'wrong password'}), 400
    delete_old_logs()
    return check_all_multilogin()
    
#if __name__ == '__main__':
#    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
#    context.load_cert_chain(f"/etc/letsencrypt/live/{m3u_host}/fullchain.pem",
#                            f"/etc/letsencrypt/live/{m3u_host}/privkey.pem")
#    app.run(host='0.0.0.0', port=443, ssl_context=context, threaded=True)