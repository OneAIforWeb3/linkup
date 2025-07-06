import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import WebApp from '@twa-dev/sdk';
import { DbUser } from '../services/api';

// Define types for the WebApp user
interface WebAppUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
}

interface WebAppContextType {
  user: WebAppUser | null;
  dbUser: DbUser | null;
  setDbUser: (user: DbUser | null) => void;
  webApp: typeof WebApp;
  isReady: boolean;
  isDarkMode: boolean;
  mainButton: {
    show: (text?: string) => void;
    hide: () => void;
    onClick: (callback: () => void) => void;
    offClick: (callback: () => void) => void;
    showProgress: (leaveActive?: boolean) => void;
    hideProgress: () => void;
  };
  backButton: {
    show: () => void;
    hide: () => void;
    onClick: (callback: () => void) => void;
    offClick: (callback: () => void) => void;
  };
  hapticFeedback: {
    impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void;
    notificationOccurred: (type: 'error' | 'success' | 'warning') => void;
    selectionChanged: () => void;
  };
  showPopup: (params: {
    title?: string;
    message: string;
    buttons?: Array<{
      id: string;
      type?: 'default' | 'ok' | 'close' | 'cancel' | 'destructive';
      text: string;
    }>;
  }) => Promise<string>;
  showAlert: (message: string) => Promise<void>;
  showConfirm: (message: string) => Promise<boolean>;
  scanQR: () => Promise<string>;
  close: () => void;
  expand: () => void;
  ready: () => void;
}

interface WebAppProviderProps {
  children: ReactNode;
}

const WebAppContext = createContext<WebAppContextType | null>(null);

export const WebAppProvider: React.FC<WebAppProviderProps> = ({ children }) => {
  const [user, setUser] = useState<WebAppUser | null>(null);
  const [dbUser, setDbUser] = useState<DbUser | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [initError, setInitError] = useState<string | null>(null);

  useEffect(() => {
    const initWebApp = async () => {
      console.log('WebAppProvider: Initializing WebApp SDK...');
      try {
        await WebApp.ready();
        console.log('WebAppProvider: SDK ready.');
        
        // Use mock user for development in browser
        if (WebApp.initDataUnsafe?.user) {
          console.log('WebAppProvider: Found real user data.', WebApp.initDataUnsafe.user);
          setUser(WebApp.initDataUnsafe.user);
        } else {
          console.warn('WebAppProvider: Telegram WebApp user data not found, using mock user for development.');
          const mockUser = {
            id: 999999,
            first_name: 'Dev',
            last_name: 'User',
            username: 'dev_user',
            language_code: 'en',
            is_premium: true,
          };
          setUser(mockUser);
          console.log('WebAppProvider: Set mock user.', mockUser);
        }
        
        setIsReady(true);
        console.log('WebAppProvider: isReady set to true.');
      } catch (error) {
        console.error('WebAppProvider: Failed to initialize Telegram WebApp SDK', error);
      }
    };
    
    initWebApp();
  }, []);

  // Detect if in dark mode
  const isDarkMode = WebApp.colorScheme === 'dark';

  // Main button controls
  const mainButton = {
    show: (text?: string) => {
      try {
        if (text) {
          WebApp.MainButton.setText(text);
        }
        WebApp.MainButton.show();
      } catch (error) {
        console.error('Error showing main button:', error);
      }
    },
    hide: () => {
      try {
        WebApp.MainButton.hide();
      } catch (error) {
        console.error('Error hiding main button:', error);
      }
    },
    onClick: (callback: () => void) => {
      try {
        WebApp.MainButton.onClick(callback);
      } catch (error) {
        console.error('Error setting onClick for main button:', error);
      }
    },
    offClick: (callback: () => void) => {
      try {
        WebApp.MainButton.offClick(callback);
      } catch (error) {
        console.error('Error setting offClick for main button:', error);
      }
    },
    showProgress: (leaveActive?: boolean) => {
      try {
        WebApp.MainButton.showProgress(leaveActive);
      } catch (error) {
        console.error('Error showing progress on main button:', error);
      }
    },
    hideProgress: () => {
      try {
        WebApp.MainButton.hideProgress();
      } catch (error) {
        console.error('Error hiding progress on main button:', error);
      }
    }
  };

  // Back button controls
  const backButton = {
    show: () => {
      try {
        WebApp.BackButton.show();
      } catch (error) {
        console.error('Error showing back button:', error);
      }
    },
    hide: () => {
      try {
        WebApp.BackButton.hide();
      } catch (error) {
        console.error('Error hiding back button:', error);
      }
    },
    onClick: (callback: () => void) => {
      try {
        WebApp.BackButton.onClick(callback);
      } catch (error) {
        console.error('Error setting onClick for back button:', error);
      }
    },
    offClick: (callback: () => void) => {
      try {
        WebApp.BackButton.offClick(callback);
      } catch (error) {
        console.error('Error setting offClick for back button:', error);
      }
    }
  };

  // Haptic feedback
  const hapticFeedback = {
    impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => {
      try {
        WebApp.HapticFeedback.impactOccurred(style);
      } catch (error) {
        console.error('Error with haptic feedback impactOccurred:', error);
      }
    },
    notificationOccurred: (type: 'error' | 'success' | 'warning') => {
      try {
        WebApp.HapticFeedback.notificationOccurred(type);
      } catch (error) {
        console.error('Error with haptic feedback notificationOccurred:', error);
      }
    },
    selectionChanged: () => {
      try {
        WebApp.HapticFeedback.selectionChanged();
      } catch (error) {
        console.error('Error with haptic feedback selectionChanged:', error);
      }
    }
  };

  // Show popup
  const showPopup = (params: {
    title?: string;
    message: string;
    buttons?: Array<{
      id: string;
      type?: 'default' | 'ok' | 'close' | 'cancel' | 'destructive';
      text: string;
    }>;
  }): Promise<string> => {
    return new Promise((resolve) => {
      try {
        // Convert our button format to WebApp's format
        const buttons = params.buttons?.map(button => ({
          id: button.id,
          type: button.type || 'default',
          text: button.text
        }));

        WebApp.showPopup({
          title: params.title,
          message: params.message,
          buttons
        }, (buttonId) => {
          // Ensure buttonId is never undefined
          resolve(buttonId || '');
        });
      } catch (error) {
        console.error('Error showing popup:', error);
        resolve('error');
      }
    });
  };

  // Show alert
  const showAlert = (message: string): Promise<void> => {
    return new Promise((resolve) => {
      try {
        WebApp.showAlert(message, () => {
          resolve();
        });
      } catch (error) {
        console.error('Error showing alert:', error);
        resolve();
      }
    });
  };

  // Show confirm
  const showConfirm = (message: string): Promise<boolean> => {
    return new Promise((resolve) => {
      try {
        WebApp.showConfirm(message, (confirmed) => {
          resolve(confirmed);
        });
      } catch (error) {
        console.error('Error showing confirm:', error);
        resolve(false);
      }
    });
  };

  // Scan QR code
  const scanQR = (): Promise<string> => {
    return new Promise((resolve, reject) => {
      try {
        if (WebApp.showScanQrPopup) {
          WebApp.showScanQrPopup({ text: 'Scan a QR code' }, (text) => {
            if (text) {
              resolve(text);
            } else {
              reject(new Error('QR scan cancelled'));
            }
            WebApp.closeScanQrPopup();
          });
        } else {
          console.log('QR scanning not available, using mock for development');
          // For development
          const mockQrText = prompt('Enter mock QR data for development:');
          if (mockQrText) {
            resolve(mockQrText);
          } else {
            reject(new Error('QR scan cancelled'));
          }
        }
      } catch (error) {
        console.error('Error scanning QR code:', error);
        reject(error);
      }
    });
  };

  // Close WebApp
  const close = () => {
    try {
      WebApp.close();
    } catch (error) {
      console.error('Error closing WebApp:', error);
    }
  };

  // Expand WebApp
  const expand = () => {
    try {
      WebApp.expand();
    } catch (error) {
      console.error('Error expanding WebApp:', error);
    }
  };

  // Ready WebApp
  const ready = () => {
    try {
      WebApp.ready();
    } catch (error) {
      console.error('Error calling ready on WebApp:', error);
    }
  };

  const value: WebAppContextType = {
    user,
    dbUser,
    setDbUser,
    webApp: WebApp,
    isReady,
    isDarkMode,
    mainButton,
    backButton,
    hapticFeedback,
    showPopup,
    showAlert,
    showConfirm,
    scanQR,
    close,
    expand,
    ready
  };

  // If there's an initialization error in production, show an error message
  if (initError && process.env.NODE_ENV !== 'development') {
    return (
      <div style={{
        padding: '20px',
        textAlign: 'center',
        color: '#ff3b30',
        fontFamily: 'sans-serif'
      }}>
        <h2>Error Initializing Telegram Mini App</h2>
        <p>{initError}</p>
        <p>Please try again or contact support.</p>
      </div>
    );
  }

  return (
    <WebAppContext.Provider value={value}>
      {children}
    </WebAppContext.Provider>
  );
};

export const useWebApp = (): WebAppContextType => {
  const context = useContext(WebAppContext);
  if (!context) {
    throw new Error('useWebApp must be used within a WebAppProvider');
  }
  return context;
};

export default WebAppContext; 