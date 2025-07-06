import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface TelegramContextType {
  telegramUser: TelegramUser | null;
  tg: any;
  isReady: boolean;
  isDarkMode: boolean;
  shareData: (data: string) => void;
  showAlert: (message: string) => void;
  scanQr: () => Promise<string>;
  backButton: {
    show: () => void;
    hide: () => void;
    onClick: (callback: () => void) => void;
  };
}

interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
}

interface TelegramProviderProps {
  children: ReactNode;
}

const TelegramContext = createContext<TelegramContextType | undefined>(undefined);

export const TelegramProvider: React.FC<TelegramProviderProps> = ({ children }) => {
  const [telegramUser, setTelegramUser] = useState<TelegramUser | null>(null);
  const [tg, setTg] = useState<any>(null);
  const [isReady, setIsReady] = useState(false);
  
  useEffect(() => {
    const tgGlobal = (window as any).Telegram;
    if (tgGlobal?.WebApp) {
      const webApp = tgGlobal.WebApp;
      
      // Initialize Telegram WebApp
      webApp.ready();
      webApp.expand();
      
      // Set main button text color
      webApp.MainButton.setParams({
        text_color: '#FFFFFF',
      });
      
      // Set telegram instance
      setTg(webApp);
      
      // Get user from WebApp
      if (webApp.initDataUnsafe?.user) {
        setTelegramUser(webApp.initDataUnsafe.user);
      } else {
        // Mock user for development
        setTelegramUser({
          id: 123456789,
          first_name: 'Dev',
          last_name: 'User',
          username: 'devuser',
          photo_url: 'https://placehold.co/200'
        });
      }
      
      setIsReady(true);
    } else {
      // For development outside of Telegram
      console.warn('Telegram WebApp is not available. Running in development mode.');
      
      // Mock user for development
      setTelegramUser({
        id: 123456789,
        first_name: 'Dev',
        last_name: 'User',
        username: 'devuser',
        photo_url: 'https://placehold.co/200'
      });
      
      setIsReady(true);
    }
  }, []);
  
  // Share data via Telegram
  const shareData = (data: string) => {
    if (tg) {
      tg.shareMessage(data);
    } else {
      // Fallback for development
      navigator.clipboard.writeText(data);
      showAlert('Copied to clipboard (Telegram sharing not available)');
    }
  };
  
  // Show alert message
  const showAlert = (message: string) => {
    if (tg) {
      tg.showAlert(message);
    } else {
      // Fallback for development
      alert(message);
    }
  };
  
  // Scan QR code
  const scanQr = (): Promise<string> => {
    return new Promise((resolve, reject) => {
      if (tg && tg.showScanQrPopup) {
        tg.showScanQrPopup({
          text: 'Scan a QR code'
        }, (text: string) => {
          if (text) {
            resolve(text);
          } else {
            reject(new Error('QR scan cancelled'));
          }
        });
      } else {
        // Fallback for development
        const mockQrText = prompt('Enter mock QR data for development:');
        if (mockQrText) {
          resolve(mockQrText);
        } else {
          reject(new Error('QR scan cancelled'));
        }
      }
    });
  };
  
  // Back button controls
  const backButton = {
    show: () => {
      if (tg) {
        tg.BackButton.show();
      }
    },
    hide: () => {
      if (tg) {
        tg.BackButton.hide();
      }
    },
    onClick: (callback: () => void) => {
      if (tg) {
        tg.BackButton.onClick(callback);
      }
    }
  };
  
  // Detect if in dark mode
  const isDarkMode = tg ? tg.colorScheme === 'dark' : true; // Default to dark mode in development
  
  const value = {
    telegramUser,
    tg,
    isReady,
    isDarkMode,
    shareData,
    showAlert,
    scanQr,
    backButton
  };

  return (
    <TelegramContext.Provider value={value}>
      {children}
    </TelegramContext.Provider>
  );
};

export const useTelegram = (): TelegramContextType => {
  const context = useContext(TelegramContext);
  
  if (context === undefined) {
    throw new Error('useTelegram must be used within a TelegramProvider');
  }
  
  return context;
};

export default TelegramContext; 