import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { Grid } from 'react-loader-spinner';

const Loader = ({ message = 'ANALYZING MARKETS...' }) => {
  return (
    <Paper 
      sx={{ 
        p: 4, 
        textAlign: 'center',
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        zIndex: 9999,
        backgroundColor: 'rgba(0, 0, 0, 0.95)',
        backdropFilter: 'blur(10px)',
        border: '2px solid #2196f3',
        borderRadius: 3,
      }}
    >
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Grid
          height="100"
          width="100"
          color="#2196f3"
          ariaLabel="grid-loading"
          radius="12.5"
          wrapperStyle={{}}
          wrapperClass=""
          visible={true}
        />
        <Typography variant="h4" sx={{ 
          mt: 3, 
          color: '#2196f3',
          fontWeight: 'bold',
          textTransform: 'uppercase',
          letterSpacing: 2,
          background: 'linear-gradient(45deg, #2196f3, #ffeb3b)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}>
          {message}
        </Typography>
        <Typography variant="h6" sx={{ 
          mt: 2, 
          color: '#b0b0b0',
          fontWeight: 'bold',
        }}>
          ⚡ AI MODELS PROCESSING...
        </Typography>
        <Typography variant="body2" sx={{ 
          mt: 1, 
          color: '#666666',
          fontStyle: 'italic',
        }}>
          Neural networks analyzing market patterns and sentiment data
        </Typography>
      </Box>
    </Paper>
  );
};

export default Loader;
