CHECK_USER_EXISTS_QUERY = """
SELECT user_id 
FROM users 
{where_condition}
"""

GET_USERS_DETAILS_QUERY = """
SELECT * 
FROM users 
{where_condition}
"""

INSERT_USER_QUERY = """
INSERT INTO users 
(tg_id, username, display_name, project_name, role, description, profile_image_url)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

UPDATE_USER_QUERY = """
UPDATE users 
SET {set_fields},
updated_at = CURRENT_TIMESTAMP 
WHERE user_id = %s
"""

DELETE_USER_QUERY = """
DELETE FROM users
WHERE user_id = %s
"""

CREATE_GROUP_QUERY = """
INSERT INTO `groups` 
(group_link, event_name, meeting_location, meeting_time)
VALUES (%s, %s, %s, %s)
"""

GET_PARTICIPANT_QUERY = """
SELECT user1_id, user2_id, created_at, updated_at
FROM group_participants 
WHERE group_id = %s
"""

INSERT_GROUP_PARTICIPANTS_QUERY = """
INSERT INTO group_participants (group_id, user1_id, user2_id)
VALUES (%s, %s, %s)
"""

GET_GROUP_DETAILS_QUERY = """
SELECT * 
FROM `groups` 
WHERE group_id = %s
"""

GET_USER_GROUPS_QUERY = """
SELECT g.*, gp.user1_id, gp.user2_id
FROM `groups` g
JOIN group_participants gp ON g.group_id = gp.group_id
WHERE gp.user1_id = %s OR gp.user2_id = %s
"""