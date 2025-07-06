import { createGlobalStyle } from 'styled-components';
import theme from './theme';

const GlobalStyles = createGlobalStyle`
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  html, body {
    font-family: ${theme.fonts.body};
    background-color: ${theme.colors.background};
    color: ${theme.colors.textPrimary};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    overscroll-behavior: none;
    overflow-x: hidden;
    width: 100%;
    height: 100%;
  }

  #root {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  a {
    color: ${theme.colors.accent};
    text-decoration: none;
    transition: opacity ${theme.transitions.fast};
    
    &:hover {
      opacity: 0.8;
    }
  }

  button {
    background: none;
    border: none;
    font-family: ${theme.fonts.body};
    cursor: pointer;
    outline: none;
    transition: opacity ${theme.transitions.fast};
    
    &:disabled {
      cursor: not-allowed;
      opacity: 0.5;
    }
  }

  input, textarea, select {
    font-family: ${theme.fonts.body};
    background: ${theme.colors.surfaceLight};
    border: 1px solid ${theme.colors.surfaceMedium};
    color: ${theme.colors.textPrimary};
    border-radius: ${theme.borderRadius.md};
    padding: ${theme.spacing.md};
    outline: none;
    transition: border-color ${theme.transitions.fast};
    
    &:focus {
      border-color: ${theme.colors.accent};
    }
    
    &::placeholder {
      color: ${theme.colors.textHint};
    }
  }

  /* Hide scrollbar for Chrome, Safari and Opera */
  ::-webkit-scrollbar {
    display: none;
  }

  /* Hide scrollbar for IE, Edge and Firefox */
  html {
    -ms-overflow-style: none;  /* IE and Edge */
    scrollbar-width: none;  /* Firefox */
  }
`;

export default GlobalStyles; 