import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useWebApp } from '../context/WebAppContext';
import { getUserByTgId } from '../services/api';

const LoadingPage = () => {
  const navigate = useNavigate();
  const { user: tgUser, setDbUser, isReady } = useWebApp();

  useEffect(() => {
    if (!isReady || !tgUser) {
      return; // Wait for the WebApp to be ready and tgUser to be available
    }

    const checkUserProfile = async () => {
      try {
        const dbProfile = await getUserByTgId(tgUser.id);
        setDbUser(dbProfile);

        if (dbProfile && dbProfile.project_name) {
          // Profile exists and is complete
          navigate('/qrs');
        } else {
          // No profile or incomplete profile, start onboarding
          navigate('/wemeetai');
        }
      } catch (error) {
        console.error('Failed to check user profile:', error);
        // On error, send to onboarding as a fallback
        navigate('/wemeetai');
      }
    };

    checkUserProfile();
  }, [isReady, tgUser, navigate, setDbUser]);

  return (
    <Container>
      <Spinner />
      <p>Loading...</p>
    </Container>
  );
};

export default LoadingPage;

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: #121212;
  color: white;
`;

const Spinner = styled.div`
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top: 4px solid #DFFF00;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`; 