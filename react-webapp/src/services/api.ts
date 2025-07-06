const API_BASE_URL = 'https://wemeetai-apis.vercel.app';

export interface DbUser {
  user_id: number;
  tg_id: number;
  username: string | null;
  display_name: string | null;
  project_name: string | null;
  role: string | null;
  description: string | null;
  profile_image_url: string | null;
  created_at: string;
  updated_at: string;
}

export const getUserByTgId = async (tgId: number): Promise<DbUser | null> => {
  try {
    const response = await fetch(`${API_BASE_URL}/get-user-by-tg-id?tg_id=${tgId}`);
    if (response.status === 404) {
      return null;
    }
    if (!response.ok) {
      throw new Error('Failed to fetch user');
    }
    const data = await response.json();
    return data.user;
  } catch (error) {
    console.error('Error fetching user by tg_id:', error);
    return null;
  }
};

export interface CreateUserPayload {
  tg_id: number;
  username?: string;
  display_name?: string;
  project_name?: string;
  role?: string;
  description?: string;
}

export const createUser = async (payload: CreateUserPayload): Promise<DbUser | null> => {
  try {
    const response = await fetch(`${API_BASE_URL}/create-user`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error('Failed to create user');
    }
    const data = await response.json();
    // Refetch user to get full object
    const newUser = await getUserByTgId(payload.tg_id);
    return newUser;
  } catch (error) {
    console.error('Error creating user:', error);
    return null;
  }
};

export interface UpdateUserPayload {
  display_name?: string;
  project_name?: string;
  role?: string;
  description?: string;
}

export const updateUser = async (userId: number, payload: UpdateUserPayload): Promise<DbUser | null> => {
    try {
      const response = await fetch(`${API_BASE_URL}/update-user/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        throw new Error('Failed to update user');
      }
      // Refetch user to get full object
      const userDetails = await fetch(`${API_BASE_URL}/get-user-details?user_id=${userId}`);
      if (!userDetails.ok) {
          throw new Error('Failed to fetch updated user details');
      }
      const data = await userDetails.json();
      return data.user;
    } catch (error) {
        console.error('Error updating user:', error);
        return null;
    }
};

export const getQrCodeUrl = (tgId: number): string => {
  return `${API_BASE_URL}/api/generate-qr?tg_id=${tgId}`;
};

export interface Connection {
  group_id: number;
  group_link: string;
  event_name: string;
  meeting_location: string;
  meeting_time: string;
  created_at: string;
  updated_at: string;
  other_user_id: number;
  other_user: DbUser;
}

export const getUserConnections = async (userId: number): Promise<Connection[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/get-user-groups?user_id=${userId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch user connections');
    }
    const data = await response.json();
    return data.groups;
  } catch (error) {
    console.error('Error fetching user connections:', error);
    return [];
  }
}; 