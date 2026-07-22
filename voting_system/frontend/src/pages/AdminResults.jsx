import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
} from '@mui/material';
import axios from 'axios';

const AdminResults = () => {
  const [elections, setElections] = useState([]);
  const [selectedElection, setSelectedElection] = useState(null);
  const [results, setResults] = useState([]);
  const [reportDialog, setReportDialog] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchElections();
  }, []);

  const fetchElections = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('/api/elections/elections/?status=closed', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setElections(response.data.results || response.data);
    } catch (err) {
      console.error('Error fetching elections:', err);
    }
  };

  const handleViewResults = async (electionId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(
        `/api/results/results/election_results/?election_id=${electionId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setResults(response.data.results);
      setSelectedElection(electionId);
    } catch (err) {
      console.error('Error fetching results:', err);
    }
  };

  const handleGenerateReport = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        '/api/results/results/generate_report/',
        { election_id: selectedElection },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      alert('Report generated successfully!');
      setReportDialog(false);
    } catch (err) {
      alert('Error: ' + err.response?.data?.error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Election Results Management
        </Typography>

        <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Closed Elections
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                  <TableCell>Election</TableCell>
                  <TableCell align="right">Total Votes</TableCell>
                  <TableCell align="right">Turnout</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {elections.map((election) => (
                  <TableRow key={election.id}>
                    <TableCell>{election.title}</TableCell>
                    <TableCell align="right">{election.stats?.total_votes_cast || 0}</TableCell>
                    <TableCell align="right">
                      {election.stats?.turnout_percentage.toFixed(2)}%
                    </TableCell>
                    <TableCell align="center">
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => handleViewResults(election.id)}
                      >
                        View Results
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>

        {selectedElection && (
          <Paper elevation={2} sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">Results Details</Typography>
              <Button
                variant="contained"
                color="primary"
                onClick={() => setReportDialog(true)}
              >
                Generate Report
              </Button>
            </Box>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                    <TableCell>Rank</TableCell>
                    <TableCell>Candidate</TableCell>
                    <TableCell align="right">Votes</TableCell>
                    <TableCell align="right">Percentage</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {results.map((result, index) => (
                    <TableRow key={index}>
                      <TableCell sx={{ fontWeight: 'bold' }}>{result.rank}</TableCell>
                      <TableCell>{result.candidate_name}</TableCell>
                      <TableCell align="right">{result.vote_count}</TableCell>
                      <TableCell align="right">{result.percentage.toFixed(2)}%</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        )}
      </Box>

      {/* Generate Report Dialog */}
      <Dialog open={reportDialog} onClose={() => setReportDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Generate Results Report</DialogTitle>
        <DialogContent>
          {loading && <LinearProgress />}
          <Typography sx={{ mt: 2 }}>
            This will generate a final certified report of the election results that can be exported to PDF or Excel.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReportDialog(false)}>Cancel</Button>
          <Button
            onClick={handleGenerateReport}
            variant="contained"
            color="primary"
            disabled={loading}
          >
            {loading ? 'Generating...' : 'Generate'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default AdminResults;
