import React from 'react';
import { Alert, AlertTitle, IconButton, Collapse } from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';

const ErrorAlert = ({ message, onClose, severity = 'error' }) => {
  return (
    <Collapse in={!!message}>
      <Alert
        severity={severity}
        action={
          <IconButton
            aria-label="close"
            color="inherit"
            size="small"
            onClick={onClose}
          >
            <CloseIcon fontSize="inherit" />
          </IconButton>
        }
        sx={{ 
          mb: 2,
          backgroundColor: 'rgba(244, 67, 54, 0.1)',
          border: '1px solid #f44336',
          color: '#ffffff',
          '& .MuiAlert-icon': {
            color: '#f44336',
          },
        }}
      >
        <AlertTitle sx={{ color: '#f44336', fontWeight: 'bold' }}>
          🚨 {severity === 'error' ? 'SYSTEM ERROR' : 
           severity === 'warning' ? 'WARNING' : 'INFO'}
        </AlertTitle>
        {message}
      </Alert>
    </Collapse>
  );
};

export default ErrorAlert;
