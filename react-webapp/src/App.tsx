import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from 'styled-components';
import theme from './styles/theme';
import GlobalStyles from './styles/GlobalStyles';
import { WebAppProvider } from './context/WebAppContext';

// Pages
import LoadingPage from './pages/LoadingPage';
import OnboardingPage from './pages/OnboardingPage';
import ProfileSetupPage from './pages/ProfileSetupPage';
import MyQRPage from './pages/MyQRPage';
import ConnectsPage from './pages/ConnectsPage';
import MainLayout from './components/MainLayout';

// Load Telegram Web App script
const loadTelegramScript = () => {
  const script = document.createElement('script');
  script.src = 'https://telegram.org/js/telegram-web-app.js';
  script.async = true;
  document.body.appendChild(script);
  
  return () => {
    document.body.removeChild(script);
  };
};

function App() {
  // Load Telegram script
  React.useEffect(() => {
    return loadTelegramScript();
  }, []);

  return (
    <WebAppProvider>
      <ThemeProvider theme={theme}>
        <GlobalStyles />
        <Router>
          <Routes>
            <Route path="/" element={<LoadingPage />} />
            <Route path="/wemeetai" element={<OnboardingPage />} />
            <Route path="/profile-setup" element={<ProfileSetupPage />} />
            
            <Route element={<MainLayout />}>
              <Route path="/qrs" element={<MyQRPage />} />
              <Route path="/connects" element={<ConnectsPage />} />
            </Route>
            
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </ThemeProvider>
    </WebAppProvider>
  );
}

export default App;
