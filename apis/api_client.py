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
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 201:
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
        
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        return self._make_request('POST', '/create-user', data=data)
    
    def update_user(self, user_id: int, **kwargs) -> Optional[Dict]:
        """Update user information"""
        # Remove None values
        data = {k: v for k, v in kwargs.items() if v is not None}
        
        if not data:
            return None
            
        return self._make_request('PUT', f'/update-user/{user_id}', data=data)
    
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
        
        return self._make_request('POST', '/create-group', data=data)
    
    def get_group_details(self, group_id: int) -> Optional[Dict]:
        """Get group details with participants"""
        return self._make_request('GET', f'/group-details/{group_id}')
    
    def check_participants(self, group_id: int) -> Optional[Dict]:
        """Get participants for a group"""
        return self._make_request('GET', '/check-participants', params={'group_id': group_id})

    def get_user_groups(self, user_id: int) -> Optional[Dict]:
        """Get all groups for a user (their connections)"""
        return self._make_request('GET', '/get-user-groups', params={'user_id': user_id})

# Global API client instance
api_client = LinkUpAPIClient() 