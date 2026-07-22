import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Button,
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Dashboard = () => {
  const [elections, setElections] = useState([]);
  const [voter, setVoter] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchVoterProfile();
    fetchElections();
  }, []);

  const fetchVoterProfile = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('/api/auth/voters/profile/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setVoter(response.data);
    } catch (err) {
      console.error('Error fetching profile:', err);
    }
  };

  const fetchElections = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('/api/elections/elections/?status=active', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setElections(response.data.results || response.data);
    } catch (err) {
      console.error('Error fetching elections:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  if (loading) return <LinearProgress />;

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Typography variant="h4" component="h1">
            Welcome, {voter?.full_name}!
          </Typography>
          <Button variant="contained" color="error" onClick={handleLogout}>
            Logout
          </Button>
        </Box>

        <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Your Information
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="textSecondary">
                Voter ID
              </Typography>
              <Typography variant="body1">{voter?.voter_id}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="textSecondary">
                Verification Status
              </Typography>
              <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>
                {voter?.verification_status}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="textSecondary">
                Email
              </Typography>
              <Typography variant="body1">{voter?.email}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="textSecondary">
                Voting Status
              </Typography>
              <Typography variant="body1">
                {voter?.has_voted ? 'Already Voted' : 'Not Yet Voted'}
              </Typography>
            </Grid>
          </Grid>
        </Paper>

        <Typography variant="h6" gutterBottom>
          Active Elections
        </Typography>
        {elections.length === 0 ? (
          <Typography>No active elections at this time.</Typography>
        ) : (
          <Grid container spacing={3}>
            {elections.map((election) => (
              <Grid item xs={12} md={6} key={election.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h5" component="h2" gutterBottom>
                      {election.title}
                    </Typography>
                    <Typography color="textSecondary" gutterBottom>
                      {election.election_type}
                    </Typography>
                    <Typography variant="body2" paragraph>
                      {election.description}
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" color="textSecondary">
                        Candidates: {election.candidates?.length || 0}
                      </Typography>
                    </Box>
                    <Button
                      variant="contained"
                      color="primary"
                      fullWidth
                      onClick={() => navigate(`/vote/${election.id}`)}
                      disabled={voter?.has_voted}
                    >
                      {voter?.has_voted ? 'Already Voted' : 'Vote Now'}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>
    </Container>
  );
};

export default Dashboard;
