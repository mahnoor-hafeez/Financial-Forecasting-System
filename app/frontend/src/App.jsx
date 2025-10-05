import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Chip,
  AppBar,
  Toolbar
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import ForecastChart from './components/ForecastChart';
import MetricsPanel from './components/MetricsPanel';
import Loader from './components/Loader';
import ErrorAlert from './components/ErrorAlert';
import { fetchInstruments, fetchHistoricalData, fetchForecast, fetchSentiment } from './services/api';

const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#000000',
      paper: '#1a1a1a',
    },
    primary: {
      main: '#2196f3', // Blue
    },
    secondary: {
      main: '#ffeb3b', // Yellow
    },
    error: {
      main: '#f44336', // Red
    },
    success: {
      main: '#4caf50', // Green for positive sentiment
    },
    warning: {
      main: '#ff9800', // Orange
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0b0b0',
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#1a1a1a',
          border: '1px solid #333333',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        contained: {
          backgroundColor: '#2196f3',
          '&:hover': {
            backgroundColor: '#1976d2',
          },
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          color: '#ffffff',
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: '#b0b0b0',
        },
      },
    },
  },
});

function App() {
  const [instruments, setInstruments] = useState([]);
  const [selectedInstrument, setSelectedInstrument] = useState('');
  const [horizon, setHorizon] = useState(24);
  const [dataLimit, setDataLimit] = useState(500); // New state for data limit
  const [historicalData, setHistoricalData] = useState([]);
  const [forecastData, setForecastData] = useState(null);
  const [sentimentData, setSentimentData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load instruments on component mount
  useEffect(() => {
    loadInstruments();
  }, []);

  const loadInstruments = async () => {
    try {
      const response = await fetchInstruments();
      if (response.instruments) {
        setInstruments(response.instruments);
        if (response.instruments.length > 0) {
          setSelectedInstrument(response.instruments[0]);
        }
      }
    } catch (err) {
      setError('Failed to load instruments');
    }
  };

  const handleGenerateForecast = async () => {
    if (!selectedInstrument) {
      setError('Please select an instrument');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Fetch all data in parallel
      const [historical, forecast, sentiment] = await Promise.all([
        fetchHistoricalData(selectedInstrument, dataLimit),
        fetchForecast(selectedInstrument, horizon),
        fetchSentiment(selectedInstrument)
      ]);

      if (historical.error) {
        throw new Error(historical.error);
      }
      if (forecast.error) {
        throw new Error(forecast.error);
      }

      setHistoricalData(historical.historical_data || []);
      setForecastData(forecast);
      setSentimentData(sentiment);
    } catch (err) {
      setError(err.message || 'Failed to generate forecast');
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive': return 'success';
      case 'negative': return 'error';
      default: return 'default';
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      
      {/* Professional App Bar */}
      <AppBar position="static" sx={{ backgroundColor: '#1a1a1a', borderBottom: '1px solid #333' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            📈 FINANCIAL AI PRO
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip 
              label="LIVE" 
              color="error" 
              size="small" 
              sx={{ 
                animation: 'pulse 2s infinite',
                '@keyframes pulse': {
                  '0%': { opacity: 1 },
                  '50%': { opacity: 0.5 },
                  '100%': { opacity: 1 },
                },
              }}
            />
            {sentimentData && (
              <Chip
                label={sentimentData.sentiment?.toUpperCase() || 'NEUTRAL'}
                color={getSentimentColor(sentimentData.sentiment)}
                size="small"
                variant="outlined"
              />
            )}
          </Box>
        </Toolbar>
      </AppBar>

      {/* Full Screen Layout */}
      <Box sx={{ 
        minHeight: '100vh', 
        backgroundColor: '#000000',
        p: 0,
        m: 0,
      }}>
        

        {/* Error Alert */}
        {error && (
          <Box sx={{ position: 'fixed', top: 100, right: 20, zIndex: 1001 }}>
            <ErrorAlert message={error} onClose={() => setError(null)} />
          </Box>
        )}

        {/* Loading Overlay */}
        {loading && <Loader />}

        {/* Main Content Container */}
        {!loading && (historicalData.length > 0 || forecastData) && (
          <Box sx={{ 
            mt: 8, // Below AppBar
            p: 2,
            minHeight: '100vh',
          }}>
            {/* Chart Section */}
            <Box sx={{ 
              height: '70vh',
              mb: 3,
              backgroundColor: '#000000',
              borderRadius: 2,
              border: '1px solid #333',
              overflow: 'hidden',
            }}>
              <ForecastChart
                historicalData={historicalData}
                forecastData={forecastData}
                symbol={selectedInstrument}
              />
            </Box>

            {/* Control Panel - Below Chart */}
            <Grid container spacing={3}>
              {/* Left Column - Trading Controls */}
              <Grid item xs={12} md={4}>
                <Paper sx={{
                  p: 3,
                  backgroundColor: 'rgba(26, 26, 26, 0.95)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid #333',
                }}>
                  <Typography variant="h6" sx={{ mb: 2, color: '#2196f3' }}>
                    🎯 TRADING CONTROLS
                  </Typography>
                  
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <FormControl fullWidth size="small">
                        <InputLabel>Instrument</InputLabel>
                        <Select
                          value={selectedInstrument}
                          onChange={(e) => setSelectedInstrument(e.target.value)}
                          label="Instrument"
                        >
                          {instruments.map((instrument) => (
                            <MenuItem key={instrument} value={instrument}>
                              {instrument}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                    
                    <Grid item xs={12}>
                      <FormControl fullWidth size="small">
                        <InputLabel>Horizon</InputLabel>
                        <Select
                          value={horizon}
                          onChange={(e) => setHorizon(e.target.value)}
                          label="Horizon"
                        >
                          <MenuItem value={1}>1 Hour</MenuItem>
                          <MenuItem value={3}>3 Hours</MenuItem>
                          <MenuItem value={24}>24 Hours</MenuItem>
                          <MenuItem value={72}>72 Hours</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid item xs={12}>
                      <FormControl fullWidth size="small">
                        <InputLabel>Data Range</InputLabel>
                        <Select
                          value={dataLimit}
                          onChange={(e) => setDataLimit(e.target.value)}
                          label="Data Range"
                        >
                          <MenuItem value={100}>100 Days</MenuItem>
                          <MenuItem value={250}>250 Days</MenuItem>
                          <MenuItem value={500}>500 Days</MenuItem>
                          <MenuItem value={1000}>1000 Days</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    
                    <Grid item xs={12}>
                      <Button
                        variant="contained"
                        size="large"
                        onClick={handleGenerateForecast}
                        disabled={loading || !selectedInstrument}
                        fullWidth
                        sx={{
                          background: 'linear-gradient(45deg, #2196f3 30%, #21cbf3 90%)',
                          fontWeight: 'bold',
                          textTransform: 'uppercase',
                          letterSpacing: 1,
                        }}
                      >
                        {loading ? '⚡ ANALYZING...' : '🚀 GENERATE FORECAST'}
                      </Button>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>

              {/* Right Column - Metrics */}
              <Grid item xs={12} md={8}>
                <MetricsPanel
                  forecastData={forecastData}
                  sentimentData={sentimentData}
                  symbol={selectedInstrument}
                />
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Welcome Screen with Controls */}
        {!loading && historicalData.length === 0 && !forecastData && (
          <Box sx={{
            mt: 8,
            p: 4,
            minHeight: '100vh',
          }}>
            <Box sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              mb: 4,
            }}>
              <Typography variant="h2" sx={{
                mb: 2,
                background: 'linear-gradient(45deg, #2196f3, #ffeb3b)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontWeight: 'bold',
              }}>
                FINANCIAL AI PRO
              </Typography>
              <Typography variant="h5" sx={{ mb: 4, color: '#b0b0b0' }}>
                Advanced Market Prediction Engine
              </Typography>
            </Box>

            {/* Control Panel for Welcome Screen */}
            <Box sx={{
              display: 'flex',
              justifyContent: 'center',
              mb: 4,
            }}>
              <Paper sx={{
                p: 4,
                backgroundColor: 'rgba(26, 26, 26, 0.95)',
                backdropFilter: 'blur(10px)',
                border: '1px solid #333',
                maxWidth: 500,
                width: '100%',
              }}>
                <Typography variant="h6" sx={{ mb: 3, color: '#2196f3', textAlign: 'center' }}>
                  🎯 TRADING CONTROLS
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Instrument</InputLabel>
                      <Select
                        value={selectedInstrument}
                        onChange={(e) => setSelectedInstrument(e.target.value)}
                        label="Instrument"
                      >
                        {instruments.map((instrument) => (
                          <MenuItem key={instrument} value={instrument}>
                            {instrument}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Horizon</InputLabel>
                      <Select
                        value={horizon}
                        onChange={(e) => setHorizon(e.target.value)}
                        label="Horizon"
                      >
                        <MenuItem value={1}>1 Hour</MenuItem>
                        <MenuItem value={3}>3 Hours</MenuItem>
                        <MenuItem value={24}>24 Hours</MenuItem>
                        <MenuItem value={72}>72 Hours</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Data Range</InputLabel>
                      <Select
                        value={dataLimit}
                        onChange={(e) => setDataLimit(e.target.value)}
                        label="Data Range"
                      >
                        <MenuItem value={100}>100 Days</MenuItem>
                        <MenuItem value={250}>250 Days</MenuItem>
                        <MenuItem value={500}>500 Days</MenuItem>
                        <MenuItem value={1000}>1000 Days</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Button
                      variant="contained"
                      size="large"
                      onClick={handleGenerateForecast}
                      disabled={loading || !selectedInstrument}
                      fullWidth
                      sx={{
                        background: 'linear-gradient(45deg, #2196f3 30%, #21cbf3 90%)',
                        fontWeight: 'bold',
                        textTransform: 'uppercase',
                        letterSpacing: 1,
                      }}
                    >
                      {loading ? '⚡ ANALYZING...' : '🚀 GENERATE FORECAST'}
                    </Button>
                  </Grid>
                </Grid>
              </Paper>
            </Box>

            {/* Welcome Message */}
            <Box sx={{
              display: 'flex',
              justifyContent: 'center',
            }}>
              <Paper sx={{ 
                p: 4, 
                backgroundColor: 'rgba(26, 26, 26, 0.8)',
                border: '1px solid #333',
                maxWidth: 600,
              }}>
                <Typography variant="h6" gutterBottom sx={{ color: '#2196f3' }}>
                  🎯 Ready to Predict the Markets
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Select an instrument from the control panel above and click "Generate Forecast" 
                  to see AI-powered predictions with advanced technical analysis and sentiment intelligence.
                </Typography>
              </Paper>
            </Box>
          </Box>
        )}
      </Box>
    </ThemeProvider>
  );
}

export default App;
