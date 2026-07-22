import React from 'react';
import { Container, Paper, Box, Typography, LinearProgress } from '@mui/material';

const Loading = () => {
  return (
    <Container>
      <Paper sx={{ p: 4, my: 4, textAlign: 'center' }}>
        <Typography variant="h6" gutterBottom>
          Loading...
        </Typography>
        <LinearProgress sx={{ mt: 2 }} />
      </Paper>
    </Container>
  );
};

export default Loading;
