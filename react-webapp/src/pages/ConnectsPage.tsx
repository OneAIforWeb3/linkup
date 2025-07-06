import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useWebApp } from '../context/WebAppContext';
import { getUserConnections, Connection } from '../services/api';

const ConnectsPage = () => {
  const { dbUser } = useWebApp();
  const [connections, setConnections] = useState<Connection[]>([]);

  useEffect(() => {
    if (dbUser) {
      const fetchConnections = async () => {
        const userConnections = await getUserConnections(dbUser.user_id);
        setConnections(userConnections);
      };
      fetchConnections();
    }
  }, [dbUser]);

  return (
    <PageContainer>
      <Header>
        <NavItem className="active">All</NavItem>
        <NavItem>Personal</NavItem>
        <NavItem>Professional</NavItem>
      </Header>
      <ConnectionList>
        {connections.map((conn) => (
          <ConnectionItem key={conn.group_id}>
            <ConnectionInfo>
              <ConnectionName>{dbUser?.display_name} &lt;&gt; {conn.other_user.display_name}</ConnectionName>
              <ConnectionTag color="#8A2BE2">{conn.event_name || 'Personal'}</ConnectionTag>
            </ConnectionInfo>
            <Arrow>&gt;</Arrow>
          </ConnectionItem>
        ))}
      </ConnectionList>
    </PageContainer>
  );
};

export default ConnectsPage;

const PageContainer = styled.div`
  display: flex;
  flex-direction: column;
  padding: 16px;
  background-color: #121212;
  color: white;
  height: 100%;
  box-sizing: border-box;
`;

const Header = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
`;

const NavItem = styled.div`
  padding: 8px 16px;
  border-radius: 20px;
  background-color: #2a2a2a;
  color: #888;
  font-weight: 500;
  
  &.active {
    background-color: #DFFF00;
    color: #121212;
  }
`;

const ConnectionList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const ConnectionItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #1c1c1c;
  padding: 16px;
  border-radius: 12px;
`;

const ConnectionInfo = styled.div``;

const ConnectionName = styled.div`
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
`;

const ConnectionTag = styled.div<{ color: string }>`
  background-color: ${props => props.color};
  color: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  display: inline-block;
`;

const Arrow = styled.div`
  font-size: 20px;
  color: #888;
`; 