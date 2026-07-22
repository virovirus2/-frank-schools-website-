import React from 'react';
import { Box, Skeleton, Grid } from '@mui/material';

const SkeletonLoader = ({ count = 3 }) => {
  return (
    <Grid container spacing={2}>
      {Array.from({ length: count }).map((_, index) => (
        <Grid item xs={12} key={index}>
          <Box>
            <Skeleton variant="text" height={30} sx={{ mb: 1 }} />
            <Skeleton variant="rectangular" height={100} />
          </Box>
        </Grid>
      ))}
    </Grid>
  );
};

export default SkeletonLoader;
