import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Box,
  Typography,
  LinearProgress,
  Grid,
  Card,
  CardContent,
  Button,
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import axios from 'axios';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF7C7C'];

const ElectionResults = () => {
  const { electionId } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchResults();
  }, [electionId]);

  const fetchResults = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(
        `/api/results/results/election_results/?election_id=${electionId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      setResults(response.data);
      
      // Transform data for charts
      const chartFormat = response.data.results.map((result) => ({
        name: result.candidate_name,
        votes: result.vote_count,
        percentage: result.percentage,
        rank: result.rank,
      }));
      setChartData(chartFormat);
    } catch (err) {
      setError(err.response?.data?.error || 'Error fetching results');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LinearProgress />;
  if (error) return <Typography color="error">{error}</Typography>;
  if (!results) return <Typography>No results available</Typography>;

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Typography variant="h4" component="h1">
            Election Results
          </Typography>
          <Button variant="outlined" onClick={() => navigate('/admin/elections')}>
            Back
          </Button>
        </Box>

        {/* Summary Statistics */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Votes
                </Typography>
                <Typography variant="h5">{results.total_votes}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Turnout Rate
                </Typography>
                <Typography variant="h5">{results.turnout.toFixed(2)}%</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Candidates
                </Typography>
                <Typography variant="h5">{chartData.length}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Leading
                </Typography>
                <Typography variant="h5" sx={{ fontSize: '0.9rem' }}>
                  {chartData.length > 0 ? chartData[0].name : 'N/A'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Bar Chart - Vote Count */}
        <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Vote Distribution by Candidate
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="votes" fill="#8884d8" name="Total Votes" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>

        {/* Pie Chart - Vote Percentage */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Vote Share Percentage
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percentage }) => `${name}: ${percentage.toFixed(1)}%`}
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="percentage"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `${value.toFixed(2)}%`} />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          {/* Results Table */}
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Detailed Results
              </Typography>
              <Box sx={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid #ddd' }}>
                      <th style={{ textAlign: 'left', padding: '12px' }}>Rank</th>
                      <th style={{ textAlign: 'left', padding: '12px' }}>Candidate</th>
                      <th style={{ textAlign: 'right', padding: '12px' }}>Votes</th>
                      <th style={{ textAlign: 'right', padding: '12px' }}>%</th>
                    </tr>
                  </thead>
                  <tbody>
                    {chartData.map((candidate, index) => (
                      <tr
                        key={index}
                        style={{
                          borderBottom: '1px solid #eee',
                          backgroundColor: index === 0 ? '#e3f2fd' : 'transparent',
                        }}
                      >
                        <td style={{ textAlign: 'left', padding: '12px', fontWeight: 'bold' }}>
                          {index + 1}
                        </td>
                        <td style={{ textAlign: 'left', padding: '12px' }}>{candidate.name}</td>
                        <td style={{ textAlign: 'right', padding: '12px' }}>{candidate.votes}</td>
                        <td style={{ textAlign: 'right', padding: '12px' }}>
                          {candidate.percentage.toFixed(2)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Box>
            </Paper>
          </Grid>
        </Grid>

        {/* Horizontal Bar Chart - Comparison */}
        <Paper elevation={2} sx={{ p: 3, mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Candidate Comparison
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              layout="vertical"
              data={chartData}
              margin={{ top: 5, right: 30, left: 200 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={180} />
              <Tooltip />
              <Bar dataKey="votes" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>
      </Box>
    </Container>
  );
};

export default ElectionResults;
