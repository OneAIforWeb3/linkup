import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useWebApp } from '../context/WebAppContext';
import { getUserConnections, Connection } from '../services/api';

const getInitials = (name?: string | null) => {
  if (!name) return '';
  const parts = name.split(' ');
  if (parts.length === 1) return parts[0][0];
  return parts[0][0] + parts[1][0];
};

const openGroupLink = (url: string) => {
  // Prefer Telegram WebApp openLink if available
  if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.openLink) {
    window.Telegram.WebApp.openLink(url);
  } else {
    window.open(url, '_blank');
  }
};

const truncate = (str: string, n: number) => (str && str.length > n ? str.slice(0, n) + '…' : str);

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

  // Metrics calculation
  const now = Date.now();
  const getCountSince = (msAgo: number) =>
    connections.filter(conn => conn.created_at && (now - new Date(conn.created_at).getTime() < msAgo)).length;
  const contacts1hr = getCountSince(60 * 60 * 1000);
  const contacts4hr = getCountSince(4 * 60 * 60 * 1000);
  const contacts1d = getCountSince(24 * 60 * 60 * 1000);
  const contactsOverall = connections.length;
  // Dummy pending followups (always less than overall)
  const pendingFollowups = Math.max(0, contactsOverall - Math.floor(Math.random() * (contactsOverall + 1)));

  return (
    <PageContainer>
      <MetricsBar>
        <MetricsRow>
          <MetricCard>
            <MetricValue>{contacts1hr}</MetricValue>
            <MetricLabel>Last 1 hr</MetricLabel>
          </MetricCard>
          <MetricCard>
            <MetricValue>{contacts4hr}</MetricValue>
            <MetricLabel>Last 4 hr</MetricLabel>
          </MetricCard>
          <MetricCard>
            <MetricValue>{contacts1d}</MetricValue>
            <MetricLabel>Last 1 day</MetricLabel>
          </MetricCard>
          <MetricCard>
            <MetricValue>{contactsOverall}</MetricValue>
            <MetricLabel>Overall</MetricLabel>
          </MetricCard>
        </MetricsRow>
        <PendingCard>
          <PendingValue>{pendingFollowups}</PendingValue>
          <PendingLabel>Pending Followups</PendingLabel>
        </PendingCard>
      </MetricsBar>
      <Header>
        <NavItem className="active">My Connections</NavItem>
        {/* <NavItem>Personal</NavItem>
        <NavItem>Professional</NavItem> */}
      </Header>
      <ConnectionList>
        {connections.map((conn) => {
          const user = conn.other_user;
          const avatar = user.profile_image_url ? (
            <AvatarImg src={user.profile_image_url} alt={user.display_name || user.username || ''} />
          ) : (
            <AvatarFallback>{getInitials(user.display_name || user.username)}</AvatarFallback>
          );
          const displayName = truncate(user.display_name || user.username || '', 12);
          return (
            <ConnectionItem key={conn.group_id}>
              <AvatarSection>{avatar}</AvatarSection>
              <ConnectionInfo>
                <ConnectionName title={user.display_name || user.username || ''}>{displayName}</ConnectionName>
                {user.project_name && (
                  <ProjectName title={user.project_name + (user.role && user.role !== 'Not specified' && user.role !== 'LinkUp User' ? ` (${user.role})` : '')}>
                    {truncate(user.project_name || '', 18)}
                    {user.role && user.role !== 'Not specified' && user.role !== 'LinkUp User' && (
                      <span title={user.role || ''}> ({truncate(user.role || '', 18)})</span>
                    )}
                  </ProjectName>
                )}
                {!user.project_name && user.role && user.role !== 'Not specified' && user.role !== 'LinkUp User' && (
                  <ProjectName title={user.role || ''}>{truncate(user.role || '', 18)}</ProjectName>
                )}
                
                
                {/* {user.description && user.description !== 'Not specified' && user.description !== 'LinkUp User' && (
                  <Description>{truncate(user.description || '', 40)}</Description>
                )} */}
                <EventAndDate>
                  {conn.event_name && <ConnectionTag color="#8A2BE2">{conn.event_name}</ConnectionTag>}
                  {conn.created_at && (
                    <MetaText>Connected: {new Date(conn.created_at).toLocaleDateString()}</MetaText>
                  )}
                </EventAndDate>
              </ConnectionInfo>
              <Actions>
                {conn.group_link && (
                  <GroupButton onClick={() => openGroupLink(conn.group_link)}>
                    <span role="img" aria-label="group">👥</span> Group Chat
                  </GroupButton>
                )}
              </Actions>
            </ConnectionItem>
          );
        })}
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
  align-items: flex-start;
  background: rgba(30, 30, 40, 0.45);
  border-radius: 20px;
  padding: 24px 20px;
  gap: 20px;
  border: 1.5px solid rgba(180, 255, 220, 0.18);
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18), 0 0 0 2px rgba(120, 255, 200, 0.08);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  margin-bottom: 18px;
  transition: box-shadow 0.2s, border 0.2s;
  min-height: 120px;
  width: 100%;
  box-sizing: border-box;
  &:hover {
    box-shadow: 0 12px 36px 0 rgba(80, 255, 200, 0.18), 0 0 0 2.5px #a259ff44;
    border: 1.5px solid #a259ff44;
  }
`;

const AvatarSection = styled.div`
  flex-shrink: 0;
`;

const AvatarImg = styled.img`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  background: #333;
`;

const AvatarFallback = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #333;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
`;

const ConnectionInfo = styled.div`
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 100%;
`;

const ConnectionName = styled.div`
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
`;

const ProjectName = styled.div`
  font-size: 15px;
  color: #aaa;
  font-weight: 500;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
`;

const Description = styled.div`
  font-size: 14px;
  color: #ccc;
  margin-bottom: 4px;
  word-break: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const MetaRow = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 2px;
`;

const MetaText = styled.span`
  font-size: 12px;
  color: #aaa;
`;

const EventAndDate = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-bottom: 2px;
`;

const Actions = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
`;

const GroupButton = styled.button`
  background: #8A2BE2;
  color: #fff;
  border: none;
  border-radius: 16px;
  padding: 6px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background 0.2s;
  &:hover {
    background: #a96bff;
  }
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

const MetricsBar = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
`;

const MetricsRow = styled.div`
  display: flex;
  gap: 12px;
  justify-content: space-between;
  flex-wrap: wrap;
`;

const MetricCard = styled.div`
  background: rgba(30, 30, 40, 0.45);
  border-radius: 16px;
  padding: 12px 18px;
  min-width: 90px;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.10), 0 0 0 1.5px rgba(120, 255, 200, 0.10);
  border: 1.5px solid rgba(180, 255, 220, 0.18);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
  transition: box-shadow 0.3s, border 0.3s;

  /* Animated gradient border */
  &::before {
    content: '';
    position: absolute;
    inset: -2px;
    z-index: 0;
    border-radius: 18px;
    background: linear-gradient(120deg, #a259ff 0%, #00ffb4 50%, #a259ff 100%);
    opacity: 0.18;
    filter: blur(6px);
    animation: gradientMove 3s linear infinite;
  }
  /* Overlay for glassy effect */
  &::after {
    content: '';
    position: absolute;
    inset: 0;
    z-index: 1;
    border-radius: 16px;
    background: rgba(30, 30, 40, 0.45);
    pointer-events: none;
  }
  > * {
    position: relative;
    z-index: 2;
  }
  &:hover {
    box-shadow: 0 8px 32px 0 rgba(80, 255, 200, 0.18), 0 0 0 2.5px #a259ff44;
    border: 1.5px solid #a259ff44;
  }

  @keyframes gradientMove {
    0% {
      background-position: 0% 50%;
    }
    100% {
      background-position: 100% 50%;
    }
  }
`;

const MetricValue = styled.div`
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 2px;
`;

const MetricLabel = styled.div`
  font-size: 12px;
  color: #aaa;
`;

const PendingCard = styled.div`
  background: rgba(30, 30, 40, 0.55);
  color: #DFFF00;
  border-radius: 16px;
  padding: 16px 0 10px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.10), 0 0 0 1.5px #a259ff44;
  border: 1.5px solid #a259ff44;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
  transition: box-shadow 0.3s, border 0.3s;
  /* Animated gradient border */
  &::before {
    content: '';
    position: absolute;
    inset: -2px;
    z-index: 0;
    border-radius: 18px;
    background: linear-gradient(120deg, #dfff00 0%, #a259ff 50%, #00ffb4 100%);
    opacity: 0.18;
    filter: blur(8px);
    animation: gradientMove 3s linear infinite;
  }
  &::after {
    content: '';
    position: absolute;
    inset: 0;
    z-index: 1;
    border-radius: 16px;
    background: rgba(30, 30, 40, 0.55);
    pointer-events: none;
  }
`;

const PendingValue = styled.div`
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 2px;
`;

const PendingLabel = styled.div`
  font-size: 14px;
  color: #DFFF00;
  opacity: 0.85;
`; 