import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Grid,
  Card,
  CardContent,
  Button,
  Alert,
  CircularProgress,
  Tabs,
  Tab
} from '@mui/material';
import { styled } from '@mui/material/styles';

const StyledTableContainer = styled(TableContainer)(({ theme }) => ({
  backgroundColor: 'rgba(26, 26, 26, 0.95)',
  borderRadius: '8px',
  border: '1px solid #333',
}));

const StyledTableCell = styled(TableCell)(({ theme }) => ({
  color: '#E0E0E0',
  borderBottom: '1px solid #333',
  '&.header': {
    backgroundColor: 'rgba(33, 150, 243, 0.1)',
    fontWeight: 'bold',
    color: '#2196f3',
  },
}));

const PerformanceCard = styled(Card)(({ theme }) => ({
  backgroundColor: 'rgba(26, 26, 26, 0.95)',
  border: '1px solid #333',
  borderRadius: '8px',
  '&:hover': {
    borderColor: '#2196f3',
    transform: 'translateY(-2px)',
    transition: 'all 0.3s ease',
  },
}));

const ModelComparisonPanel = ({ symbol, onModelSelect }) => {
  const [comparisonData, setComparisonData] = useState(null);
  const [performanceSummary, setPerformanceSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    if (symbol) {
      fetchComparisonData();
    }
  }, [symbol]);

  const fetchComparisonData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [comparisonResponse, summaryResponse] = await Promise.all([
        fetch(`http://127.0.0.1:8001/models/compare/${symbol}`),
        fetch(`http://127.0.0.1:8001/models/performance-summary/${symbol}`)
      ]);

      if (!comparisonResponse.ok || !summaryResponse.ok) {
        throw new Error('Failed to fetch comparison data');
      }

      const comparison = await comparisonResponse.json();
      const summary = await summaryResponse.json();

      setComparisonData(comparison);
      setPerformanceSummary(summary);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getPerformanceColor = (score) => {
    if (score >= 80) return '#4caf50'; // Green
    if (score >= 60) return '#ffeb3b'; // Yellow
    if (score >= 40) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  const getModelTypeColor = (type) => {
    switch (type) {
      case 'Traditional': return '#2196f3';
      case 'Neural Network': return '#9c27b0';
      case 'Ensemble': return '#ff5722';
      default: return '#666666';
    }
  };

  const formatMetric = (value) => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'number') {
      return value.toFixed(4);
    }
    return value;
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress sx={{ color: '#2196f3' }} />
        <Typography sx={{ ml: 2, color: '#AAA' }}>
          Loading model comparison...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Error loading model comparison: {error}
      </Alert>
    );
  }

  if (!comparisonData || !performanceSummary) {
    return (
      <Alert severity="info" sx={{ m: 2 }}>
        No comparison data available for {symbol}
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" sx={{ mb: 3, color: '#2196f3', fontWeight: 'bold' }}>
        🧠 AI Model Performance Analysis
      </Typography>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="📊 Performance Table" sx={{ color: '#AAA' }} />
        <Tab label="🏆 Rankings" sx={{ color: '#AAA' }} />
        <Tab label="📈 Summary" sx={{ color: '#AAA' }} />
      </Tabs>

      {activeTab === 0 && (
        <StyledTableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <StyledTableCell className="header">Model</StyledTableCell>
                <StyledTableCell className="header">Type</StyledTableCell>
                <StyledTableCell className="header">RMSE</StyledTableCell>
                <StyledTableCell className="header">MAE</StyledTableCell>
                <StyledTableCell className="header">MAPE (%)</StyledTableCell>
                <StyledTableCell className="header">Score</StyledTableCell>
                <StyledTableCell className="header">Last Trained</StyledTableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {Object.entries(comparisonData.models || {}).map(([modelName, data]) => (
                <TableRow key={modelName}>
                  <StyledTableCell>
                    <Typography sx={{ fontWeight: 'bold', color: '#E0E0E0' }}>
                      {modelName.replace('_', ' ').toUpperCase()}
                    </Typography>
                  </StyledTableCell>
                  <StyledTableCell>
                    <Chip
                      label={data.model_type}
                      size="small"
                      sx={{
                        backgroundColor: getModelTypeColor(data.model_type),
                        color: 'white',
                        fontWeight: 'bold'
                      }}
                    />
                  </StyledTableCell>
                  <StyledTableCell sx={{ color: '#4caf50' }}>
                    {formatMetric(data.rmse)}
                  </StyledTableCell>
                  <StyledTableCell sx={{ color: '#ffeb3b' }}>
                    {formatMetric(data.mae)}
                  </StyledTableCell>
                  <StyledTableCell sx={{ color: '#ff9800' }}>
                    {formatMetric(data.mape)}
                  </StyledTableCell>
                  <StyledTableCell>
                    <Chip
                      label={`${data.performance_score || 0}/100`}
                      size="small"
                      sx={{
                        backgroundColor: getPerformanceColor(data.performance_score),
                        color: 'white',
                        fontWeight: 'bold'
                      }}
                    />
                  </StyledTableCell>
                  <StyledTableCell sx={{ color: '#AAA', fontSize: '0.8rem' }}>
                    {new Date(data.last_trained).toLocaleDateString()}
                  </StyledTableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </StyledTableContainer>
      )}

      {activeTab === 1 && comparisonData.rankings && (
        <Grid container spacing={3}>
          {Object.entries(comparisonData.rankings).map(([metric, ranking]) => (
            <Grid item xs={12} md={4} key={metric}>
              <PerformanceCard>
                <CardContent>
                  <Typography variant="h6" sx={{ color: '#2196f3', mb: 2 }}>
                    🏆 Best {metric.toUpperCase()}
                  </Typography>
                  <Typography variant="h4" sx={{ color: '#4caf50', fontWeight: 'bold' }}>
                    {ranking.best?.replace('_', ' ').toUpperCase()}
                  </Typography>
                  <Typography sx={{ color: '#AAA', mt: 1 }}>
                    Score: {formatMetric(ranking.scores?.[ranking.best])}
                  </Typography>
                  <Typography sx={{ color: '#666', fontSize: '0.8rem', mt: 1 }}>
                    Worst: {ranking.worst?.replace('_', ' ').toUpperCase()}
                  </Typography>
                </CardContent>
              </PerformanceCard>
            </Grid>
          ))}
        </Grid>
      )}

      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <PerformanceCard>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#2196f3', mb: 2 }}>
                  📊 Summary Statistics
                </Typography>
                <Typography sx={{ color: '#AAA', mb: 1 }}>
                  Total Models: {performanceSummary.total_models}
                </Typography>
                <Typography sx={{ color: '#AAA', mb: 1 }}>
                  Symbols Tested: {performanceSummary.symbols_tested}
                </Typography>
                <Typography sx={{ color: '#AAA', mb: 1 }}>
                  Last Update: {new Date(performanceSummary.last_update).toLocaleString()}
                </Typography>
              </CardContent>
            </PerformanceCard>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <PerformanceCard>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#2196f3', mb: 2 }}>
                  💡 Recommendations
                </Typography>
                {comparisonData.recommendations?.map((rec, index) => (
                  <Typography key={index} sx={{ color: '#AAA', mb: 1, fontSize: '0.9rem' }}>
                    • {rec}
                  </Typography>
                ))}
              </CardContent>
            </PerformanceCard>
          </Grid>
        </Grid>
      )}

      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
        <Button
          variant="contained"
          onClick={fetchComparisonData}
          sx={{
            background: 'linear-gradient(45deg, #2196f3 30%, #21cbf3 90%)',
            fontWeight: 'bold',
            textTransform: 'uppercase',
            letterSpacing: 1,
          }}
        >
          🔄 Refresh Analysis
        </Button>
      </Box>
    </Box>
  );
};

export default ModelComparisonPanel;
