import os
import sys

# Add the project root to the Python path to allow importing modules from there
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from mysql.connector import Error

from apis.constants import CHECK_USER_EXISTS_QUERY, INSERT_USER_QUERY, UPDATE_USER_QUERY, DELETE_USER_QUERY, \
    CREATE_GROUP_QUERY, INSERT_GROUP_PARTICIPANTS_QUERY, GET_GROUP_DETAILS_QUERY, GET_PARTICIPANT_QUERY, \
    GET_USERS_DETAILS_QUERY, GET_USER_GROUPS_QUERY
from apis.qr_utils import generate_qr_code_image, create_card_style_qr

load_dotenv()

app = Flask(__name__)
CORS(app)


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )


@app.route('/create-user', methods=['POST'])
def create_user():
    data = request.json
    required_fields = ['tg_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if tg_id already exists
        where_condition = 'WHERE tg_id = %s'
        query = CHECK_USER_EXISTS_QUERY.format(where_condition=where_condition)
        cursor.execute(query, (data['tg_id'],))
        if cursor.fetchone():
            return jsonify({'error': 'User with this tg_id already exists'}), 409
        cursor.execute(INSERT_USER_QUERY, (
            data['tg_id'],
            data.get('username'),
            data.get('display_name'),
            data.get('project_name'),
            data.get('role'),
            data.get('description'),
            data.get('profile_image_url')
        ))
        conn.commit()
        user_id = cursor.lastrowid
        return jsonify({'message': 'User created', 'user_id': user_id}), 201
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/update-user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if user exists
        where_condition = 'WHERE user_id = %s'
        query = CHECK_USER_EXISTS_QUERY.format(where_condition=where_condition)
        cursor.execute(query, (user_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'User not found'}), 404
        # Build update query
        fields = []
        values = []
        for key in ['username', 'display_name', 'project_name', 'role', 'description', 'profile_image_url']:
            if key in data:
                fields.append(f"{key} = %s")
                values.append(data[key])
        if not fields:
            return jsonify({'error': 'No updatable fields provided'}), 400
        values.append(user_id)
        query = UPDATE_USER_QUERY.format(set_fields=', '.join(fields))
        cursor.execute(query, tuple(values))
        conn.commit()
        return jsonify({'message': 'User updated'}), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/delete-user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if user exists
        where_condition = 'WHERE user_id = %s'
        query = CHECK_USER_EXISTS_QUERY.format(where_condition=where_condition)
        cursor.execute(query, (user_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'User not found'}), 404
        cursor.execute(DELETE_USER_QUERY, (user_id,))
        conn.commit()
        return jsonify({'message': 'User deleted'}), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/get-user-details', methods=['GET'])
def get_user_details():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Missing user_id parameter'}), 400
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = GET_USERS_DETAILS_QUERY.format(where_condition=f'WHERE user_id = {user_id}')
        cursor.execute(query)
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'user': user}), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/get-user-by-tg-id', methods=['GET'])
def get_user_by_tg_id():
    tg_id = request.args.get('tg_id')
    if not tg_id:
        return jsonify({'error': 'Missing tg_id parameter'}), 400
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = GET_USERS_DETAILS_QUERY.format(where_condition=f'WHERE tg_id = {tg_id}')
        cursor.execute(query)
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'user': user}), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/create-group', methods=['POST'])
def create_group():
    data = request.json
    required_fields = ['group_link', 'user1_id', 'user2_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Validate user1_id and user2_id exist
        for uid in [data.get('user1_id'), data.get('user2_id')]:
            where_condition = 'WHERE user_id = %s'
            query = CHECK_USER_EXISTS_QUERY.format(where_condition=where_condition)
            cursor.execute(query, (uid,))
            if not cursor.fetchone():
                return jsonify({'error': f'User with user_id {uid} not found'}), 404
        # Create group
        # print(CREATE_GROUP_QUERY)
        cursor.execute(CREATE_GROUP_QUERY, (
            data.get('group_link'),
            data.get('event_name'),
            data.get('meeting_location'),
            data.get('meeting_time')
        ))
        conn.commit()
        group_id = cursor.lastrowid
        # Insert into group_participants
        cursor.execute(INSERT_GROUP_PARTICIPANTS_QUERY, (group_id, data.get('user1_id'), data.get('user2_id')))
        conn.commit()
        return jsonify({'message': 'Group and participants created', 'group_id': group_id}), 201
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/check-participants', methods=['GET'])
def check_participants():
    group_id = request.args.get('group_id')
    if not group_id:
        return jsonify({'error': 'Missing group_id parameter'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(GET_PARTICIPANT_QUERY, (group_id,))
        participants = cursor.fetchall()
        return jsonify({'participants': participants}), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/group-details/<int:group_id>', methods=['GET'])
def group_details(group_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get group details
        cursor.execute(GET_GROUP_DETAILS_QUERY, (group_id,))
        group = cursor.fetchone()
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        # Get participants
        cursor.execute(GET_PARTICIPANT_QUERY, (group_id,))
        participants_rows = cursor.fetchall()
        participant_ids = set()
        for row in participants_rows:
            if row['user1_id']:
                participant_ids.add(row['user1_id'])
            if row['user2_id']:
                participant_ids.add(row['user2_id'])
        participants = []
        if participant_ids:
            format_strings = ','.join(['%s'] * len(participant_ids))
            query = GET_USERS_DETAILS_QUERY.format(where_condition=f'WHERE user_id IN ({format_strings})')
            cursor.execute(query, tuple(participant_ids))
            participants = cursor.fetchall()
        return jsonify({'group': group, 'participants': participants}), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/get-user-groups', methods=['GET'])
def get_user_groups():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Missing user_id parameter'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(GET_USER_GROUPS_QUERY, (user_id, user_id))
        groups = cursor.fetchall()
        
        # Process groups to include connection information
        processed_groups = []
        for group in groups:
            # Determine the other user in the connection
            other_user_id = group['user2_id'] if group['user1_id'] == int(user_id) else group['user1_id']
            
            # Get other user details
            other_user_query = GET_USERS_DETAILS_QUERY.format(where_condition=f'WHERE user_id = {other_user_id}')
            cursor.execute(other_user_query)
            other_user = cursor.fetchone()
            
            processed_group = {
                'group_id': group['group_id'],
                'group_link': group['group_link'],
                'event_name': group['event_name'],
                'meeting_location': group['meeting_location'],
                'meeting_time': group['meeting_time'],
                'created_at': group['created_at'],
                'updated_at': group['updated_at'],
                'other_user_id': other_user_id,
                'other_user': other_user
            }
            processed_groups.append(processed_group)
        
        return jsonify({'groups': processed_groups}), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# Webapp serving routes
@app.route('/webapp/')
@app.route('/webapp')
def serve_webapp():
    """Serve the main webapp index.html"""
    try:
        webapp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'react-webapp', 'build')
        return send_from_directory(webapp_dir, 'index.html')
    except Exception as e:
        return jsonify({'error': f'Webapp not found: {str(e)}'}), 404

@app.route('/webapp/<path:filename>')
def serve_webapp_assets(filename):
    """Serve webapp static assets (CSS, JS, images)"""
    try:
        webapp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'react-webapp', 'build')
        return send_from_directory(webapp_dir, filename)
    except Exception as e:
        return jsonify({'error': f'Asset not found: {str(e)}'}), 404

# API endpoints for the webapp
@app.route('/api/generate-qr', methods=['GET'])
def generate_qr_api():
    """Generate card-style QR code for webapp"""
    import io
    tg_id = request.args.get('tg_id')
    if not tg_id:
        return jsonify({'error': 'Missing tg_id parameter'}), 400
    try:
        # Look up user in DB
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT username, display_name FROM users WHERE tg_id = %s", (tg_id,))
        user = cursor.fetchone()
        if user:
            username = user['username'] or user['display_name'] or f'user_{tg_id}'
        else:
            username = f'user_{tg_id}'
        if cursor: cursor.close()
        if conn: conn.close()
        # Generate card-style QR
        qr_img = create_card_style_qr(f"user_{tg_id}", username)
        if qr_img is not None:
            width, height = qr_img.size
            crop_margin = int(width * 0.12)
            left = crop_margin
            right = width - crop_margin
            qr_img = qr_img.crop((left, 0, right, height))
        if qr_img is None:
            # fallback to basic QR
            from apis.qr_utils import generate_qr_code_image
            qr_img = generate_qr_code_image(tg_id)
        img_buffer = io.BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        return send_file(img_buffer, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': f'Failed to generate QR: {str(e)}'}), 500

@app.route('/api/user-connections', methods=['GET'])
def get_user_connections_api():
    """Get user connections for webapp"""
    tg_id = request.args.get('tg_id')
    if not tg_id:
        return jsonify({'error': 'Missing tg_id parameter'}), 400
    
    # For now, return empty connections - this would need to be implemented
    # based on your connection tracking system
    return jsonify([])

@app.route('/api/update-profile', methods=['PUT'])
def update_profile_api():
    """Update user profile for webapp"""
    data = request.json
    tg_id = data.get('tg_id')
    
    if not tg_id:
        return jsonify({'error': 'Missing tg_id parameter'}), 400
    
    # Update user profile in database
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Find user by tg_id
        cursor.execute("SELECT user_id FROM users WHERE tg_id = %s", (tg_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_id = user[0]
        
        # Build update query
        fields = []
        values = []
        for key in ['display_name', 'role', 'project_name', 'description']:
            if key in data:
                fields.append(f"{key} = %s")
                values.append(data[key])
        
        if not fields:
            return jsonify({'error': 'No updatable fields provided'}), 400
        
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(fields)} WHERE user_id = %s"
        cursor.execute(query, tuple(values))
        conn.commit()
        
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
