import os

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from mysql.connector import Error

from constants import CHECK_USER_EXISTS_QUERY, INSERT_USER_QUERY, UPDATE_USER_QUERY, DELETE_USER_QUERY, \
    CREATE_GROUP_QUERY, INSERT_GROUP_PARTICIPANTS_QUERY, GET_GROUP_DETAILS_QUERY, GET_PARTICIPANT_QUERY, \
    GET_USERS_DETAILS_QUERY

load_dotenv()

app = Flask(__name__)


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
        print(CREATE_GROUP_QUERY)
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
