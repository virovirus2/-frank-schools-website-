import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Box,
  Typography,
  LinearProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { useParams } from 'react-router-dom';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Bar,
} from 'recharts';
import axios from 'axios';

const LiveTurnout = () => {
  const { electionId } = useParams();
  const [turnoutData, setTurnoutData] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [exportDialog, setExportDialog] = useState(false);

  useEffect(() => {
    fetchTurnoutData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchTurnoutData, 30000);
    return () => clearInterval(interval);
  }, [electionId]);

  const fetchTurnoutData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(
        `/api/elections/elections/${electionId}/statistics/`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setStats(response.data);

      // Mock time-series data - in production, get actual hourly data
      const mockData = generateMockTurnoutData(response.data);
      setTurnoutData(mockData);
    } catch (err) {
      console.error('Error fetching turnout data:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateMockTurnoutData = (currentStats) => {
    const data = [];
    const hours = 24;
    const totalVoters = currentStats.total_registered_voters;
    const currentVotes = currentStats.total_votes_cast;

    for (let i = 0; i <= hours; i++) {
      data.push({
        time: `${i}:00`,
        votes: Math.floor((currentVotes / hours) * i),
        percentage: ((currentVotes / hours) * i / totalVoters) * 100,
        cumulative: Math.floor((currentVotes / hours) * i),
      });
    }
    return data;
  };

  const handleExport = async (format) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        '/api/results/results/generate_report/',
        { election_id: electionId },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      alert('Report generated successfully!');
      setExportDialog(false);
    } catch (err) {
      alert('Error generating report: ' + err.message);
    }
  };

  if (loading) return <LinearProgress />;
  if (!stats) return <Typography>No data available</Typography>;

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Typography variant="h4" component="h1">
            Live Turnout Monitor
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={() => setExportDialog(true)}
          >
            Export Report
          </Button>
        </Box>

        {/* Key Metrics */}
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' },
            gap: 2,
            mb: 4,
          }}
        >
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography color="textSecondary" variant="body2">
              Total Registered Voters
            </Typography>
            <Typography variant="h5" sx={{ mt: 1 }}>
              {stats.total_registered_voters.toLocaleString()}
            </Typography>
          </Paper>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography color="textSecondary" variant="body2">
              Total Votes Cast
            </Typography>
            <Typography variant="h5" sx={{ mt: 1 }}>
              {stats.total_votes_cast.toLocaleString()}
            </Typography>
          </Paper>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography color="textSecondary" variant="body2">
              Turnout Percentage
            </Typography>
            <Typography variant="h5" sx={{ mt: 1, color: '#4CAF50' }}>
              {stats.turnout_percentage.toFixed(2)}%
            </Typography>
          </Paper>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography color="textSecondary" variant="body2">
              Still to Vote
            </Typography>
            <Typography variant="h5" sx={{ mt: 1 }}>
              {(
                stats.total_registered_voters - stats.total_votes_cast
              ).toLocaleString()}
            </Typography>
          </Paper>
        </Box>

        {/* Turnout Trend Chart */}
        <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Turnout Trend
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={turnoutData}>
              <defs>
                <linearGradient id="colorVotes" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="votes"
                stroke="#8884d8"
                fillOpacity={1}
                fill="url(#colorVotes)"
                name="Votes Cast"
              />
            </AreaChart>
          </ResponsiveContainer>
        </Paper>

        {/* Turnout Percentage Chart */}
        <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Turnout Percentage Over Time
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={turnoutData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Bar yAxisId="left" dataKey="votes" fill="#82ca9d" name="Total Votes" />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="percentage"
                stroke="#ff7300"
                name="Turnout %"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </Paper>
      </Box>

      {/* Export Dialog */}
      <Dialog open={exportDialog} onClose={() => setExportDialog(false)}>
        <DialogTitle>Export Results Report</DialogTitle>
        <DialogContent>
          <Typography gutterBottom>
            Choose format to export the final results:
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExportDialog(false)}>Cancel</Button>
          <Button
            onClick={() => handleExport('pdf')}
            variant="contained"
          >
            Export as PDF
          </Button>
          <Button
            onClick={() => handleExport('excel')}
            variant="contained"
            color="success"
          >
            Export as Excel
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default LiveTurnout;
