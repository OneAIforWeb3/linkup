import React, { useState } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { useWebApp } from '../context/WebAppContext';
import { createUser, updateUser } from '../services/api';

const ProfileSetupPage = () => {
  const navigate = useNavigate();
  const { user: tgUser, dbUser, setDbUser } = useWebApp();
  const [project, setProject] = useState('');
  const [role, setRole] = useState('');
  const [bio, setBio] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleNext = async () => {
    console.log('handleNext called');
    console.log('tgUser:', tgUser);
    console.log('dbUser:', dbUser);
    if (!tgUser || isLoading) return;
    
    setIsLoading(true);
    try {
      const payload = {
        display_name: tgUser.first_name,
        username: tgUser.username,
        project_name: project,
        role,
        description: bio,
      };

      if (dbUser) {
        // User exists, update them
        const updatedUser = await updateUser(dbUser.user_id, payload);
        setDbUser(updatedUser);
      } else {
        // New user, create them
        const newUser = await createUser({ tg_id: tgUser.id, ...payload });
        setDbUser(newUser);
      }
      navigate('/qrs');
    } catch (error) {
      console.error('Failed to save profile:', error);
      // Optionally, show an error message to the user
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container>
      <Header>
        <BackButton onClick={() => navigate(-1)}>&larr;</BackButton>
        <Progress>1/2</Progress>
      </Header>
      <Title>
        <Icon>&#x1F50D;</Icon> Add profile info
      </Title>
      <Form>
        <InputGroup>
          <Label>What's your project called?</Label>
          <Input type="text" placeholder="Type name" value={project} onChange={(e) => setProject(e.target.value)} />
        </InputGroup>
        <InputGroup>
          <Label>What's your role in this project?</Label>
          <Input type="text" placeholder="Type name" value={role} onChange={(e) => setRole(e.target.value)} />
        </InputGroup>
        <InputGroup>
          <Label>Write a bio</Label>
          <Input type="text" placeholder="Type name" value={bio} onChange={(e) => setBio(e.target.value)} />
        </InputGroup>
      </Form>
      <Footer>
        <NextButton onClick={handleNext} disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Next'}
        </NextButton>
      </Footer>
    </Container>
  );
};

export default ProfileSetupPage;

const Container = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 20px;
  box-sizing: border-box;
  background-color: #121212;
  color: white;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const BackButton = styled.button`
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
`;

const Progress = styled.span`
  font-size: 16px;
`;

const Title = styled.h1`
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 32px;
  display: flex;
  align-items: center;
`;

const Icon = styled.span`
  margin-right: 8px;
  font-size: 28px;
`;

const Form = styled.div`
  flex-grow: 1;
`;

const InputGroup = styled.div`
  margin-bottom: 24px;
`;

const Label = styled.label`
  display: block;
  font-size: 16px;
  margin-bottom: 8px;
  color: #aaa;
`;

const Input = styled.input`
  width: 100%;
  background: none;
  border: none;
  border-bottom: 1px solid #444;
  color: white;
  font-size: 18px;
  padding: 8px 0;

  &:focus {
    outline: none;
    border-bottom-color: #DFFF00;
  }
`;

const Footer = styled.div`
  display: flex;
  justify-content: flex-end;
`;

const NextButton = styled.button`
  padding: 14px 40px;
  border: none;
  border-radius: 12px;
  background-color: #DFFF00;
  color: #121212;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  
  &:disabled {
    background-color: #aaa;
    cursor: not-allowed;
  }
`; 