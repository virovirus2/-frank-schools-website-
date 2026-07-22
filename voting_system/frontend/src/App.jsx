import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box, AppBar, Toolbar, Typography, Button, Menu, MenuItem } from '@mui/material';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import VotePage from './pages/VotePage';
import ElectionResults from './pages/ElectionResults';
import LiveTurnout from './pages/LiveTurnout';
import AdminResults from './pages/AdminResults';

const App = () => {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const token = localStorage.getItem('access_token');

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/register';
  };

  return (
    <Router>
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        {token && (
          <AppBar position="static">
            <Toolbar>
              <Typography variant="h6" sx={{ flexGrow: 1 }}>
                Voting System
              </Typography>
              <Button
                color="inherit"
                onClick={handleMenuOpen}
              >
                Menu
              </Button>
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
              >
                <MenuItem onClick={() => window.location.href = '/dashboard'}>Dashboard</MenuItem>
                <MenuItem onClick={() => window.location.href = '/admin/results'}>Admin Results</MenuItem>
                <MenuItem onClick={handleLogout}>Logout</MenuItem>
              </Menu>
            </Toolbar>
          </AppBar>
        )}
        <Box sx={{ flex: 1 }}>
          <Routes>
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={token ? <Dashboard /> : <Navigate to="/register" />} />
            <Route path="/vote/:electionId" element={token ? <VotePage /> : <Navigate to="/register" />} />
            <Route path="/results/:electionId" element={token ? <ElectionResults /> : <Navigate to="/register" />} />
            <Route path="/turnout/:electionId" element={token ? <LiveTurnout /> : <Navigate to="/register" />} />
            <Route path="/admin/results" element={token ? <AdminResults /> : <Navigate to="/register" />} />
            <Route path="/" element={<Navigate to={token ? "/dashboard" : "/register"} />} />
          </Routes>
        </Box>
      </Box>
    </Router>
  );
};

export default App;
