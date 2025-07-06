import os
import requests
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class LinkUpAPIClient:
    """Client for interacting with LinkUp API"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv('LINKUP_API_URL', 'http://localhost:8000')
        self.timeout = 30
        
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Optional[Dict]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        logger.info(f"API Request: {method} {url}")
        if data:
            logger.info(f"Request data: {data}")
        if params:
            logger.info(f"Request params: {params}")
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
            
            logger.info(f"API Response status: {response.status_code}")
            
            if response.status_code == 200:
                logger.info(f"API Response success: {response.text[:200]}...")
                return response.json()
            elif response.status_code == 201:
                logger.info(f"API Response created: {response.text[:200]}...")
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Resource not found: {endpoint}")
                return None
            elif response.status_code == 409:
                logger.warning(f"Conflict: {response.json().get('error', 'Unknown conflict')}")
                return {"error": "already_exists"}
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"API server not available: {e}")
            return None
        except requests.exceptions.Timeout as e:
            logger.error(f"API request timeout: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {e}")
            return None
    
    def create_user(self, tg_id: int, username: str = None, display_name: str = None, 
                   project_name: str = None, role: str = None, description: str = None,
                   profile_image_url: str = None) -> Optional[Dict]:
        """Create a new user"""
        data = {
            'tg_id': tg_id,
            'username': username,
            'display_name': display_name,
            'project_name': project_name,
            'role': role,
            'description': description,
            'profile_image_url': profile_image_url
        }
        
        # Keep None values for profile_image_url but remove other None values
        # This allows explicit null values for profile_image_url
        filtered_data = {}
        for k, v in data.items():
            if k == 'profile_image_url' or v is not None:
                filtered_data[k] = v
        
        return self._make_request('POST', '/create-user', data=filtered_data)
    
    def update_user(self, user_id: int, **kwargs) -> Optional[Dict]:
        """Update user information"""
        # Keep None values for profile_image_url but remove other None values
        # This allows explicit null values for profile_image_url
        filtered_data = {}
        for k, v in kwargs.items():
            if k == 'profile_image_url' or v is not None:
                filtered_data[k] = v
        
        if not filtered_data:
            return None
            
        return self._make_request('PUT', f'/update-user/{user_id}', data=filtered_data)
    
    def delete_user(self, user_id: int) -> Optional[Dict]:
        """Delete a user"""
        return self._make_request('DELETE', f'/delete-user/{user_id}')
    
    def get_user_details(self, user_id: int) -> Optional[Dict]:
        """Get user details by user_id"""
        return self._make_request('GET', '/get-user-details', params={'user_id': user_id})
    
    def get_user_by_tg_id(self, tg_id: int) -> Optional[Dict]:
        """Get user details by telegram ID"""
        return self._make_request('GET', '/get-user-by-tg-id', params={'tg_id': tg_id})
    
    def create_group(self, group_link: str, user1_id: int, user2_id: int,
                    event_name: str = None, meeting_location: str = None,
                    meeting_time: str = None) -> Optional[Dict]:
        """Create a new group"""
        data = {
            'group_link': group_link,
            'user1_id': user1_id,
            'user2_id': user2_id,
            'event_name': event_name,
            'meeting_location': meeting_location,
            'meeting_time': meeting_time
        }
        
        logger.info(f"Creating group with link {group_link} between users {user1_id} and {user2_id}")
        response = self._make_request('POST', '/create-group', data=data)
        
        if response and 'group_id' in response:
            logger.info(f"Successfully created group {response['group_id']}")
        else:
            logger.error(f"Failed to create group between users {user1_id} and {user2_id}")
        
        return response
    
    def get_group_details(self, group_id: int) -> Optional[Dict]:
        """Get group details with participants"""
        return self._make_request('GET', f'/group-details/{group_id}')
    
    def check_participants(self, group_id: int) -> Optional[Dict]:
        """Get participants for a group"""
        return self._make_request('GET', '/check-participants', params={'group_id': group_id})

    def get_user_groups(self, user_id: int) -> Optional[Dict]:
        """Get all groups for a user (their connections)"""
        return self._make_request('GET', '/get-user-groups', params={'user_id': user_id})
        
    def update_group(self, group_id: int, group_link: str = None, 
                    event_name: str = None, meeting_location: str = None, 
                    meeting_time: str = None) -> Optional[Dict]:
        """Update group information"""
        data = {
            'group_link': group_link,
            'event_name': event_name,
            'meeting_location': meeting_location,
            'meeting_time': meeting_time
        }
        
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        if not data:
            return None
        
        logger.info(f"Updating group {group_id} with data: {data}")
        response = self._make_request('PUT', f'/update-group/{group_id}', data=data)
        
        if response:
            logger.info(f"Successfully updated group {group_id}")
        else:
            logger.error(f"Failed to update group {group_id}")
            
        return response

    def update_group_safely(self, group_id: int, group_link: str = None, 
                     event_name: str = None, meeting_location: str = None, 
                     meeting_time: str = None) -> Optional[Dict]:
        """Update group information with fallback to delete+recreate if update fails"""
        # First try direct update
        result = self.update_group(
            group_id=group_id, 
            group_link=group_link, 
            event_name=event_name,
            meeting_location=meeting_location,
            meeting_time=meeting_time
        )
        
        # If update succeeds, we're done
        if result:
            return result
        
        # If update fails, we need to get existing group data
        logger.warning(f"Direct update of group {group_id} failed, trying alternative approach")
        group_details = self.get_group_details(group_id)
        
        if not group_details:
            logger.error(f"Could not retrieve details for group {group_id}")
            return None
        
        # Store the important info
        user1_id = group_details.get('user1_id')
        user2_id = group_details.get('user2_id')
        current_event = group_details.get('event_name')
        current_location = group_details.get('meeting_location')
        current_time = group_details.get('meeting_time')
        
        # Delete the old group
        delete_result = self._make_request('DELETE', f'/delete-group/{group_id}')
        if not delete_result:
            logger.error(f"Could not delete group {group_id}")
            return None
            
        # Create a new group with updated values
        create_data = {
            'group_link': group_link,
            'user1_id': user1_id,
            'user2_id': user2_id,
            'event_name': event_name or current_event,
            'meeting_location': meeting_location or current_location,
            'meeting_time': meeting_time or current_time
        }
        
        # Remove None values
        create_data = {k: v for k, v in create_data.items() if v is not None}
        
        logger.info(f"Recreating group with data: {create_data}")
        return self._make_request('POST', '/create-group', data=create_data)

# Global API client instance
api_client = LinkUpAPIClient() 