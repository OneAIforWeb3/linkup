import React from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { useWebApp } from '../context/WebAppContext';
import logo from '../assets/images/fulllogo-wemeetAI.png';

const OnboardingPage = () => {
  const navigate = useNavigate();
  const { user } = useWebApp();

  const handleContinue = () => {
    navigate('/profile-setup');
  };

  return (
    <Container>
      <Content>
        <Welcome>Welcome{user ? `, ${user.first_name}` : ''}!</Welcome>
        <Logo src={logo} alt="WeMeet Logo" />
        <Description>The easiest way to connect at events.</Description>
      </Content>
      <Button onClick={handleContinue}>
        Get started
      </Button>
    </Container>
  );
};

const Container = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  min-height: 100vh;
  background: #111;
  padding: 0 16px;
`;

const Content = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 80px;
`;

const Welcome = styled.h2`
  font-size: 24px;
  font-weight: 500;
  margin-bottom: 16px;
`;

const Logo = styled.img`
  width: 180px;
  margin-bottom: 40px;
`;

const Description = styled.div`
  color: #888;
  font-size: 16px;
  margin-bottom: 16px;
`;

const Button = styled.button`
  display: flex;
  justify-content: center;
  width: 100%;
  max-width: 300px;
  padding: 16px;
  border: none;
  border-radius: 12px;
  background-color: #DFFF00;
  color: #121212;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: #c8e600;
  }
`;

export default OnboardingPage; 