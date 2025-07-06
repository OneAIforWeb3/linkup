import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import styled from 'styled-components';

const MainLayout = () => {
  return (
    <Container>
      <Content>
        <Outlet />
      </Content>
      <BottomNav>
        <NavItem to="/qrs">
          <Icon>📱</Icon>
          <span>My QRs</span>
        </NavItem>
        <NavItem to="/connects">
          <Icon>👥</Icon>
          <span>Connects</span>
        </NavItem>
      </BottomNav>
    </Container>
  );
};

export default MainLayout;

const Container = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #121212;
`;

const Content = styled.main`
  flex-grow: 1;
  overflow-y: auto;
`;

const BottomNav = styled.nav`
  display: flex;
  justify-content: space-around;
  background-color: #1c1c1c;
  border-top: 1px solid #333;
  padding: 8px 0;
`;

const NavItem = styled(NavLink)`
  display: flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  color: #888;
  padding: 4px 12px;
  
  &.active {
    color: #DFFF00;
  }
`;

const Icon = styled.span`
  font-size: 24px;
  margin-bottom: 4px;
`; 