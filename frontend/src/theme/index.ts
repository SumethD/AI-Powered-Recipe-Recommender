import { createTheme, responsiveFontSizes } from '@mui/material/styles';
import { grey } from '@mui/material/colors';

// Create a fresh, food-inspired color palette
const palette = {
  sage: {
    light: '#b5c9a1',
    main: '#8BA872', // Sage green - primary color
    dark: '#5e7348',
    contrastText: '#ffffff',
  },
  terracotta: {
    light: '#f0a48a',
    main: '#E07A5F', // Warm terracotta - accent color
    dark: '#c15642',
    contrastText: '#ffffff',
  },
  cream: {
    light: '#fffef8',
    main: '#F8F4E3', // Soft cream - background
    dark: '#eae7d5',
    contrastText: '#2a2a2a',
  },
  olive: {
    light: '#94a187',
    main: '#697A63', // Olive green - secondary color
    dark: '#495545',
    contrastText: '#ffffff',
  },
  neutral: {
    light: '#f4f4f4',
    main: '#EDEDE9', // Soft neutral - background
    dark: '#d6d6d6',
    contrastText: '#3a3a3a',
  },
};

// Create a theme instance
let theme = createTheme({
  palette: {
    primary: {
      main: palette.sage.main,
      light: palette.sage.light,
      dark: palette.sage.dark,
      contrastText: palette.sage.contrastText,
    },
    secondary: {
      main: palette.terracotta.main,
      light: palette.terracotta.light,
      dark: palette.terracotta.dark,
      contrastText: palette.terracotta.contrastText,
    },
    background: {
      default: palette.cream.light,
      paper: '#ffffff',
    },
    text: {
      primary: '#3a3a3a',
      secondary: '#5a5a5a',
    },
    error: {
      main: '#e53935',
    },
    warning: {
      main: '#f5b942',
    },
    info: {
      main: '#81a4cd',
    },
    success: {
      main: '#7cb083',
    },
  },
  typography: {
    fontFamily: [
      'Inter',
      'Poppins',
      'Roboto',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontFamily: 'Poppins, sans-serif',
      fontWeight: 700,
      color: '#3a3a3a',
    },
    h2: {
      fontFamily: 'Poppins, sans-serif',
      fontWeight: 700,
      color: '#3a3a3a',
    },
    h3: {
      fontFamily: 'Poppins, sans-serif',
      fontWeight: 600,
      color: '#3a3a3a',
    },
    h4: {
      fontFamily: 'Poppins, sans-serif',
      fontWeight: 600,
      color: '#3a3a3a',
    },
    h5: {
      fontFamily: 'Poppins, sans-serif',
      fontWeight: 500,
      color: '#3a3a3a',
    },
    h6: {
      fontFamily: 'Poppins, sans-serif',
      fontWeight: 500,
      color: '#3a3a3a',
    },
    subtitle1: {
      fontFamily: 'Inter, sans-serif',
      fontWeight: 500,
    },
    subtitle2: {
      fontFamily: 'Inter, sans-serif',
      fontWeight: 500,
    },
    body1: {
      fontFamily: 'Inter, sans-serif',
    },
    body2: {
      fontFamily: 'Inter, sans-serif',
    },
    button: {
      fontFamily: 'Inter, sans-serif',
      fontWeight: 600,
      textTransform: 'none',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '10px 24px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 8px rgba(0,0,0,0.08)',
          },
        },
        contained: {
          '&:hover': {
            boxShadow: '0 6px 12px rgba(0,0,0,0.12)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 4px 12px rgba(0,0,0,0.04)',
          transition: 'transform 0.3s ease, box-shadow 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 20px rgba(0,0,0,0.08)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
        },
        elevation1: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
        },
        elevation2: {
          boxShadow: '0 4px 12px rgba(0,0,0,0.04)',
        },
        elevation3: {
          boxShadow: '0 6px 16px rgba(0,0,0,0.04)',
        },
        elevation4: {
          boxShadow: '0 8px 24px rgba(0,0,0,0.04)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: palette.sage.light,
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: palette.sage.main,
            },
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 500,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
          borderRadius: 0,
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          fontWeight: 600,
          textTransform: 'none',
        },
      },
    },
  },
});

// Apply responsive font sizes
theme = responsiveFontSizes(theme);

export default theme; 