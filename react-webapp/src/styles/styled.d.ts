import 'styled-components';

declare module 'styled-components' {
  export interface DefaultTheme {
    colors: {
      background: string;
      surfaceLight: string;
      surfaceMedium: string;
      surfaceDark: string;
      textPrimary: string;
      textSecondary: string;
      textHint: string;
      accent: string;
      
      purple: string;
      green: string;
      orange: string;
      blue: string;
      
      success: string;
      error: string;
      warning: string;
    };
    
    fonts: {
      body: string;
      heading: string;
    };
    
    fontSizes: {
      xs: string;
      sm: string;
      md: string;
      lg: string;
      xl: string;
      '2xl': string;
      '3xl': string;
      '4xl': string;
    };
    
    spacing: {
      xs: string;
      sm: string;
      md: string;
      lg: string;
      xl: string;
      '2xl': string;
    };
    
    borderRadius: {
      sm: string;
      md: string;
      lg: string;
      xl: string;
      full: string;
    };
    
    shadows: {
      sm: string;
      md: string;
      lg: string;
      xl: string;
    };
    
    transitions: {
      default: string;
      fast: string;
      slow: string;
    };
  }
} 