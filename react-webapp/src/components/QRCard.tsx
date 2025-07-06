import React from 'react';
import styled from 'styled-components';
import theme from '../styles/theme';

interface QRCardProps {
  data: string;
  username?: string;
  color?: 'purple' | 'green' | 'orange' | 'blue';
  label?: string;
  onShare?: () => void;
  qrCodeUrl?: string;
}

const QRCard: React.FC<QRCardProps> = ({
  data,
  username,
  color = 'purple',
  label = 'Personal',
  onShare,
  qrCodeUrl
}) => {
  // Get color values from theme
  const cardColor = theme.colors[color];
  
  return (
    <CardContainer color={cardColor}>
      <QRCodeWrapper>
        {qrCodeUrl ? (
          <img src={qrCodeUrl} alt="QR Code" width="300" height="200" />
        ) : (
          <div>Loading QR code...</div>
        )}
      </QRCodeWrapper>
      
      <CardLabel>{label}</CardLabel>
      
      <NoteArea>
        <NoteText>Add a note</NoteText>
        <EditIcon>✎</EditIcon>
      </NoteArea>
    </CardContainer>
  );
};

const CardContainer = styled.div<{ color: string }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: ${props => props.color};
  border-radius: ${theme.borderRadius.lg};
  padding: ${theme.spacing.lg};
  width: 100%;
  max-width: 280px;
  margin: 0 auto;
  box-shadow: ${theme.shadows.md};
  transition: transform ${theme.transitions.default};
  
  &:active {
    transform: scale(0.98);
  }
`;

const QRCodeWrapper = styled.div`
  background-color: #FFFFFF;
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius.md};
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: ${theme.spacing.lg};
`;

const CardLabel = styled.div`
  background-color: #FFFFFF;
  color: ${props => props.theme.colors.background};
  border-radius: ${theme.borderRadius.full};
  padding: ${theme.spacing.xs} ${theme.spacing.xl};
  font-weight: bold;
  font-size: ${theme.fontSizes.md};
  margin-bottom: ${theme.spacing.md};
`;

const NoteArea = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: ${theme.spacing.xs};
  color: rgba(255, 255, 255, 0.8);
  font-size: ${theme.fontSizes.sm};
`;

const NoteText = styled.span`
  font-weight: 500;
`;

const EditIcon = styled.span`
  font-size: ${theme.fontSizes.sm};
`;

export default QRCard; 