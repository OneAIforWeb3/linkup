import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useWebApp } from '../context/WebAppContext';
import { getQrCodeUrl } from '../services/api';

const MyQRPage = () => {
  const { user, hapticFeedback, showAlert } = useWebApp();
  const [qrCodeUrl, setQrCodeUrl] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      const url = getQrCodeUrl(user.id);
      setQrCodeUrl(url);
    }
  }, [user]);

  const handleShare = () => {
    hapticFeedback.impactOccurred('medium');
    showAlert('Sharing your QR code!');
    // In a real app, you would open a share sheet here
  };
  
  return (
    <PageContainer>
      <Header>
        <NavItem className="active">All</NavItem>
        <NavItem>Personal</NavItem>
        <NavItem>Professional</NavItem>
      </Header>
      <QRImageContainer>
        {qrCodeUrl ? (
          <img src={qrCodeUrl} alt="QR Code" style={{ maxWidth: '90vw', maxHeight: '60vh', display: 'block', margin: '0 auto' }} />
        ) : (
          <div>Loading QR code...</div>
        )}
      </QRImageContainer>
      <ShareSection>
        <ShareTitle>Share via</ShareTitle>
        <ShareButtons>
          <ShareButton className="secondary">Others</ShareButton>
          <ShareButton className="primary" onClick={handleShare}>
            <TelegramIcon viewBox="0 0 24 24" width="24" height="24">
              <path d="M22,3.2l-2.9,13.7c-0.2,0.8-0.7,1-1.3,0.6l-4.3-3.2l-2.1,2c-0.2,0.2-0.4,0.4-0.8,0.4l0.3-4.4L18,6.2 c0.3-0.3-0.1-0.5-0.5-0.2L6.3,12.1l-4.2-1.3c-0.8-0.2-0.8-0.8,0.2-1.2L20.9,2.3C21.6,2,22.2,2.5,22,3.2z" />
            </TelegramIcon>
            <span>Telegram</span>
          </ShareButton>
        </ShareButtons>
      </ShareSection>
    </PageContainer>
  );
};

export default MyQRPage;

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

const QRImageContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  margin-bottom: 32px;
`;

const ShareSection = styled.div``;

const ShareTitle = styled.h2`
  font-size: 16px;
  color: #888;
  text-align: center;
  margin-bottom: 16px;
`;

const ShareButtons = styled.div`
  display: flex;
  justify-content: center;
  gap: 16px;
`;

const ShareButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 14px 24px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;

  &.primary {
    background-color: #DFFF00;
    color: #121212;
    flex-grow: 1;
    max-width: 200px;
  }
  
  &.secondary {
    background-color: #2a2a2a;
    color: white;
  }
  
  span {
    margin-left: 8px;
  }
`;

const TelegramIcon = styled.svg`
  fill: #121212;
`; 