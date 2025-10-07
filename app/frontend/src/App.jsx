import React, { useState, useEffect } from 'react';
import {
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
import ModelComparisonPanel from './components/ModelComparisonPanel';
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
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          margin: 0,
          padding: 0,
          width: '100vw',
          overflowX: 'hidden',
        },
        html: {
          margin: 0,
          padding: 0,
          width: '100vw',
          overflowX: 'hidden',
        },
        '#root': {
          margin: 0,
          padding: 0,
          width: '100vw',
          overflowX: 'hidden',
        },
      },
    },
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
  const [showModelComparison, setShowModelComparison] = useState(false);
  const [selectedModel, setSelectedModel] = useState('ensemble'); // Default to ensemble model
  const [availableModels] = useState(['ensemble', 'lstm', 'arima', 'moving_average', 'var', 'gru']);

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
        fetchForecast(selectedInstrument, horizon, selectedModel),
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

  const handleModelChange = async (newModel) => {
    if (!selectedInstrument) {
      setError('Please select an instrument first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Fetch forecast with the new model
      const forecast = await fetchForecast(selectedInstrument, horizon, newModel);
      
      if (forecast.error) {
        throw new Error(forecast.error);
      }

      setForecastData(forecast);
    } catch (err) {
      setError(err.message || 'Failed to generate forecast with selected model');
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
        width: '100vw',
        overflowX: 'hidden', // Prevent horizontal scroll
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
            p: 0, // Remove padding for full width
            minHeight: '100vh',
            width: '100vw', // Full viewport width
            mx: 0, // Remove horizontal margins
          }}>
            {/* Chart Section */}
            <Box sx={{ 
              height: '70vh',
              mb: 2, // Reduce margin
              backgroundColor: '#000000',
              borderRadius: 0, // Remove border radius for full width
              border: '1px solid #333',
              overflow: 'hidden',
              mx: 0, // Remove horizontal margins
            }}>
              <ForecastChart
                historicalData={historicalData}
                forecastData={forecastData}
                symbol={selectedInstrument}
              />
            </Box>

            {/* Control Panel - Below Chart - Full Width */}
            <Grid container spacing={1} sx={{ mx: 0, px: 1 }}>
              {/* Trading Controls - Full Width */}
              <Grid item xs={12}>
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
                    <Grid item xs={12} md={2}>
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

                    <Grid item xs={12} md={2}>
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

                    <Grid item xs={12} md={2}>
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

                    <Grid item xs={12} md={2}>
                      <FormControl fullWidth size="small">
                        <InputLabel>AI Model</InputLabel>
                        <Select
                          value={selectedModel}
                          onChange={(e) => setSelectedModel(e.target.value)}
                          label="AI Model"
                        >
                          {availableModels.map((model) => (
                            <MenuItem key={model} value={model}>
                              {model.replace('_', ' ').toUpperCase()}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>

                    <Grid item xs={12} md={2}>
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

                    <Grid item xs={12} md={2}>
                      <Button
                        variant="outlined"
                        size="large"
                        onClick={() => setShowModelComparison(!showModelComparison)}
                        fullWidth
                        sx={{
                          borderColor: '#ffeb3b',
                          color: '#ffeb3b',
                          fontWeight: 'bold',
                          textTransform: 'uppercase',
                          letterSpacing: 1,
                          '&:hover': {
                            borderColor: '#ffc107',
                            backgroundColor: 'rgba(255, 235, 59, 0.1)'
                          }
                        }}
                      >
                        {showModelComparison ? '📊 HIDE COMPARISON' : '🧠 MODEL COMPARISON'}
                      </Button>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>

              {/* Metrics Panel - Horizontal Layout */}
              <Grid item xs={12}>
                <Grid container spacing={1} sx={{ mx: 0 }}>
                  {/* AI Model Performance */}
                  <Grid item xs={12} md={4}>
                    <Paper sx={{ 
                      p: 2, 
                      height: '100%',
                      background: 'linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(26, 26, 26, 0.9) 100%)',
                      border: '1px solid #2196f3',
                      backdropFilter: 'blur(10px)',
                      borderRadius: 0, // Remove border radius for full width
                      mx: 0, // Remove horizontal margins
                    }}>
                      <Typography variant="h6" gutterBottom sx={{ 
                        display: 'flex', 
                        alignItems: 'center',
                        color: '#2196f3',
                        fontWeight: 'bold',
                        textTransform: 'uppercase',
                        letterSpacing: 1,
                        fontSize: '1rem',
                      }}>
                        🎯 AI MODEL PERFORMANCE
                      </Typography>
                      
                      {forecastData?.metrics ? (
                        <Box>
                          {/* Current Model Display */}
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            <Typography variant="body2" sx={{ minWidth: '50px', fontSize: '0.8rem' }}>
                              Active:
                            </Typography>
                            <Chip 
                              label={forecastData.model_used || selectedModel} 
                              size="small" 
                              color="primary"
                              sx={{ fontSize: '0.7rem' }}
                            />
                          </Box>
                          
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                                RMSE
                              </Typography>
                              <Chip
                                label={forecastData.metrics.rmse ? forecastData.metrics.rmse.toFixed(2) : 'N/A'}
                                size="small"
                                color="success"
                                variant="outlined"
                                sx={{ fontSize: '0.7rem' }}
                              />
                            </Box>
                            
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                                MAE
                              </Typography>
                              <Chip
                                label={forecastData.metrics.mae ? forecastData.metrics.mae.toFixed(2) : 'N/A'}
                                size="small"
                                color="success"
                                variant="outlined"
                                sx={{ fontSize: '0.7rem' }}
                              />
                            </Box>
                            
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                                MAPE
                              </Typography>
                              <Chip
                                label={forecastData.metrics.mape ? `${forecastData.metrics.mape.toFixed(2)}%` : 'N/A'}
                                size="small"
                                color="success"
                                variant="outlined"
                                sx={{ fontSize: '0.7rem' }}
                              />
                            </Box>
                          </Box>
                        </Box>
                      ) : (
                        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
                          No performance metrics available
                        </Typography>
                      )}
                    </Paper>
                  </Grid>

                  {/* Market Sentiment */}
                  <Grid item xs={12} md={4}>
                    <Paper sx={{ 
                      p: 2, 
                      height: '100%',
                      background: 'linear-gradient(135deg, rgba(255, 235, 59, 0.1) 0%, rgba(26, 26, 26, 0.9) 100%)',
                      border: '1px solid #ffeb3b',
                      backdropFilter: 'blur(10px)',
                      borderRadius: 0, // Remove border radius for full width
                      mx: 0, // Remove horizontal margins
                    }}>
                      <Typography variant="h6" gutterBottom sx={{ 
                        display: 'flex', 
                        alignItems: 'center',
                        color: '#ffeb3b',
                        fontWeight: 'bold',
                        textTransform: 'uppercase',
                        letterSpacing: 1,
                        fontSize: '1rem',
                      }}>
                        🧠 MARKET SENTIMENT
                      </Typography>
                      
                      {sentimentData ? (
                        <Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
                              Overall Sentiment
                            </Typography>
                            <Chip
                              label={sentimentData.sentiment || 'Neutral'}
                              color={sentimentData.sentiment === 'positive' ? 'success' : sentimentData.sentiment === 'negative' ? 'error' : 'default'}
                              size="small"
                              sx={{ ml: 1, fontSize: '0.7rem' }}
                            />
                          </Box>
                          
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                              Polarity Score
                            </Typography>
                            <Typography variant="body2" sx={{ fontWeight: 'bold', fontSize: '0.8rem' }}>
                              {sentimentData.polarity ? sentimentData.polarity.toFixed(2) : 'N/A'}
                            </Typography>
                          </Box>
                          
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                              Confidence
                            </Typography>
                            <Typography variant="body2" sx={{ fontWeight: 'bold', fontSize: '0.8rem' }}>
                              {sentimentData.polarity ? 
                                (Math.abs(sentimentData.polarity) > 0.1 ? 'High' : 'Medium') : 
                                'Low'
                              }
                            </Typography>
                          </Box>
                          
                          {sentimentData.title && (
                            <Box sx={{ mt: 1 }}>
                              <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                                Latest News
                              </Typography>
                              <Typography variant="body2" sx={{ 
                                fontSize: '0.7rem',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                              }}>
                                {sentimentData.title}
                              </Typography>
                            </Box>
                          )}
                        </Box>
                      ) : (
                        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
                          No sentiment data available
                        </Typography>
                      )}
                    </Paper>
                  </Grid>

                  {/* Forecast Summary */}
                  <Grid item xs={12} md={4}>
                    <Paper sx={{ 
                      p: 2, 
                      height: '100%',
                      background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(26, 26, 26, 0.9) 100%)',
                      border: '1px solid #4caf50',
                      backdropFilter: 'blur(10px)',
                      borderRadius: 0, // Remove border radius for full width
                      mx: 0, // Remove horizontal margins
                    }}>
                      <Typography variant="h6" gutterBottom sx={{ 
                        display: 'flex', 
                        alignItems: 'center',
                        color: '#4caf50',
                        fontWeight: 'bold',
                        textTransform: 'uppercase',
                        letterSpacing: 1,
                        fontSize: '1rem',
                      }}>
                        📈 FORECAST SUMMARY
                      </Typography>
                      
                      {forecastData?.predictions ? (
                        <Box>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                              Predictions
                            </Typography>
                            <Typography variant="h6" color="primary" sx={{ fontSize: '1rem' }}>
                              {forecastData.predictions.length}
                            </Typography>
                          </Box>
                          
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                              Horizon
                            </Typography>
                            <Typography variant="h6" color="primary" sx={{ fontSize: '1rem' }}>
                              {forecastData.predictions.length}h
                            </Typography>
                          </Box>
                          
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                              Latest Price
                            </Typography>
                            <Typography variant="body2" sx={{ fontWeight: 'bold', fontSize: '0.8rem' }}>
                              ${forecastData.predictions[0]?.value ? forecastData.predictions[0].value.toFixed(2) : 'N/A'}
                            </Typography>
                          </Box>
                          
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                              Final Price
                            </Typography>
                            <Typography variant="body2" sx={{ fontWeight: 'bold', fontSize: '0.8rem' }}>
                              ${forecastData.predictions[forecastData.predictions.length - 1]?.value ? forecastData.predictions[forecastData.predictions.length - 1].value.toFixed(2) : 'N/A'}
                            </Typography>
                          </Box>
                          
                          {forecastData.predictions.length > 1 && (
                            <Box sx={{ mt: 1 }}>
                              <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                                Price Change
                              </Typography>
                              <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                                {(() => {
                                  const startPrice = forecastData.predictions[0]?.value;
                                  const endPrice = forecastData.predictions[forecastData.predictions.length - 1]?.value;
                                  const change = endPrice - startPrice;
                                  const changePercent = startPrice ? (change / startPrice) * 100 : 0;
                                  
                                  return (
                                    <>
                                      <Chip
                                        label={`${change > 0 ? '+' : ''}${change.toFixed(2)}`}
                                        size="small"
                                        color={change > 0 ? 'success' : 'error'}
                                        variant="outlined"
                                        sx={{ fontSize: '0.7rem' }}
                                      />
                                      <Typography variant="caption" sx={{ ml: 1, fontSize: '0.7rem' }}>
                                        ({changePercent.toFixed(2)}%)
                                      </Typography>
                                    </>
                                  );
                                })()}
                              </Box>
                            </Box>
                          )}
                        </Box>
                      ) : (
                        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>
                          No forecast data available
                        </Typography>
                      )}
                    </Paper>
                  </Grid>
                </Grid>
              </Grid>

              {/* Model Comparison Panel - Conditional */}
              {showModelComparison && (
                <Grid item xs={12}>
                  <Paper sx={{
                    p: 3,
                    backgroundColor: 'rgba(26, 26, 26, 0.95)',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid #333',
                  }}>
                    <ModelComparisonPanel
                      symbol={selectedInstrument}
                      onModelSelect={(modelName) => {
                        console.log(`Selected model: ${modelName}`);
                        // You can add logic here to switch to the selected model
                      }}
                    />
                  </Paper>
                </Grid>
              )}
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
                    <FormControl fullWidth size="small">
                      <InputLabel>AI Model</InputLabel>
                      <Select
                        value={selectedModel}
                        onChange={(e) => setSelectedModel(e.target.value)}
                        label="AI Model"
                      >
                        {availableModels.map((model) => (
                          <MenuItem key={model} value={model}>
                            {model.replace('_', ' ').toUpperCase()}
                          </MenuItem>
                        ))}
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
