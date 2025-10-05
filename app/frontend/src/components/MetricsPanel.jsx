import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Grid,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Assessment,
  Psychology,
  Speed,
} from '@mui/icons-material';

const MetricsPanel = ({ forecastData, sentimentData, symbol }) => {
  const getTrendIcon = (value, isNegative = false) => {
    if (value === null || value === undefined) return <Assessment />;
    
    if (isNegative) {
      // For metrics like RMSE, MAE where lower is better
      return value < 1000 ? <TrendingDown color="success" /> : <TrendingUp color="error" />;
    } else {
      // For metrics where higher is better
      return value > 0 ? <TrendingUp color="success" /> : <TrendingDown color="error" />;
    }
  };

  const getTrendColor = (value, isNegative = false) => {
    if (value === null || value === undefined) return 'default';
    
    if (isNegative) {
      return value < 1000 ? 'success' : 'error';
    } else {
      return value > 0 ? 'success' : 'error';
    }
  };

  const formatMetric = (value, isPercentage = false) => {
    if (value === null || value === undefined) return 'N/A';
    
    if (isPercentage) {
      return `${value.toFixed(2)}%`;
    }
    
    if (typeof value === 'number') {
      if (value > 1000) {
        return value.toLocaleString('en-US', { maximumFractionDigits: 0 });
      }
      return value.toFixed(2);
    }
    
    return value.toString();
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return <TrendingUp color="success" />;
      case 'negative':
        return <TrendingDown color="error" />;
      default:
        return <Assessment color="action" />;
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return 'success';
      case 'negative':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      {/* Model Performance Metrics */}
      <Paper sx={{ 
        p: 3, 
        mb: 2,
        background: 'linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(26, 26, 26, 0.9) 100%)',
        border: '1px solid #2196f3',
        backdropFilter: 'blur(10px)',
      }}>
        <Typography variant="h6" gutterBottom sx={{ 
          display: 'flex', 
          alignItems: 'center',
          color: '#2196f3',
          fontWeight: 'bold',
          textTransform: 'uppercase',
          letterSpacing: 1,
        }}>
          <Assessment sx={{ mr: 1 }} />
          🎯 AI MODEL PERFORMANCE
        </Typography>
        
        {forecastData?.metrics ? (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography variant="body2" sx={{ minWidth: '60px' }}>
                  Model:
                </Typography>
                <Chip 
                  label={forecastData.model_used || 'Unknown'} 
                  size="small" 
                  color="primary"
                />
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <List dense>
                <ListItem sx={{ px: 0 }}>
                  <ListItemIcon sx={{ minWidth: '36px' }}>
                    {getTrendIcon(forecastData.metrics.rmse, true)}
                  </ListItemIcon>
                  <ListItemText
                    primary="RMSE"
                    secondary={
                      <Chip
                        label={formatMetric(forecastData.metrics.rmse)}
                        size="small"
                        color={getTrendColor(forecastData.metrics.rmse, true)}
                        variant="outlined"
                      />
                    }
                  />
                </ListItem>
                
                <ListItem sx={{ px: 0 }}>
                  <ListItemIcon sx={{ minWidth: '36px' }}>
                    {getTrendIcon(forecastData.metrics.mae, true)}
                  </ListItemIcon>
                  <ListItemText
                    primary="MAE"
                    secondary={
                      <Chip
                        label={formatMetric(forecastData.metrics.mae)}
                        size="small"
                        color={getTrendColor(forecastData.metrics.mae, true)}
                        variant="outlined"
                      />
                    }
                  />
                </ListItem>
                
                <ListItem sx={{ px: 0 }}>
                  <ListItemIcon sx={{ minWidth: '36px' }}>
                    {getTrendIcon(forecastData.metrics.mape, true)}
                  </ListItemIcon>
                  <ListItemText
                    primary="MAPE"
                    secondary={
                      <Chip
                        label={formatMetric(forecastData.metrics.mape, true)}
                        size="small"
                        color={getTrendColor(forecastData.metrics.mape, true)}
                        variant="outlined"
                      />
                    }
                  />
                </ListItem>
              </List>
            </Grid>
          </Grid>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No performance metrics available
          </Typography>
        )}
      </Paper>

      {/* Sentiment Analysis */}
      <Paper sx={{ 
        p: 3, 
        mb: 2,
        background: 'linear-gradient(135deg, rgba(255, 235, 59, 0.1) 0%, rgba(26, 26, 26, 0.9) 100%)',
        border: '1px solid #ffeb3b',
        backdropFilter: 'blur(10px)',
      }}>
        <Typography variant="h6" gutterBottom sx={{ 
          display: 'flex', 
          alignItems: 'center',
          color: '#ffeb3b',
          fontWeight: 'bold',
          textTransform: 'uppercase',
          letterSpacing: 1,
        }}>
          <Psychology sx={{ mr: 1 }} />
          🧠 MARKET SENTIMENT
        </Typography>
        
        {sentimentData ? (
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <ListItemIcon sx={{ minWidth: '36px' }}>
                {getSentimentIcon(sentimentData.sentiment)}
              </ListItemIcon>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Overall Sentiment
                </Typography>
                <Chip
                  label={sentimentData.sentiment || 'Neutral'}
                  color={getSentimentColor(sentimentData.sentiment)}
                  size="medium"
                />
              </Box>
            </Box>
            
            <Divider sx={{ my: 1 }} />
            
            <Grid container spacing={1}>
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary">
                  Polarity Score
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  {formatMetric(sentimentData.polarity)}
                </Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary">
                  Confidence
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  {sentimentData.polarity ? 
                    (Math.abs(sentimentData.polarity) > 0.1 ? 'High' : 'Medium') : 
                    'Low'
                  }
                </Typography>
              </Grid>
            </Grid>
            
            {sentimentData.title && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Latest News
                </Typography>
                <Typography variant="body2" sx={{ 
                  fontSize: '0.75rem',
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
          <Typography variant="body2" color="text.secondary">
            No sentiment data available
          </Typography>
        )}
      </Paper>

      {/* Forecast Summary */}
      <Paper sx={{ 
        p: 3,
        background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(26, 26, 26, 0.9) 100%)',
        border: '1px solid #4caf50',
        backdropFilter: 'blur(10px)',
      }}>
        <Typography variant="h6" gutterBottom sx={{ 
          display: 'flex', 
          alignItems: 'center',
          color: '#4caf50',
          fontWeight: 'bold',
          textTransform: 'uppercase',
          letterSpacing: 1,
        }}>
          <Speed sx={{ mr: 1 }} />
          📈 FORECAST SUMMARY
        </Typography>
        
        {forecastData?.predictions ? (
          <Box>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary">
                  Predictions
                </Typography>
                <Typography variant="h6" color="primary">
                  {forecastData.predictions.length}
                </Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary">
                  Horizon
                </Typography>
                <Typography variant="h6" color="primary">
                  {forecastData.predictions.length}h
                </Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary">
                  Latest Price
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  ${formatMetric(forecastData.predictions[0]?.value)}
                </Typography>
              </Grid>
              
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary">
                  Final Price
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  ${formatMetric(forecastData.predictions[forecastData.predictions.length - 1]?.value)}
                </Typography>
              </Grid>
            </Grid>
            
            {forecastData.predictions.length > 1 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="text.secondary">
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
                          label={`${change > 0 ? '+' : ''}${formatMetric(change)}`}
                          size="small"
                          color={change > 0 ? 'success' : 'error'}
                          variant="outlined"
                        />
                        <Typography variant="caption" sx={{ ml: 1 }}>
                          ({formatMetric(changePercent, true)})
                        </Typography>
                      </>
                    );
                  })()}
                </Box>
              </Box>
            )}
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No forecast data available
          </Typography>
        )}
      </Paper>
    </Box>
  );
};

export default MetricsPanel;
