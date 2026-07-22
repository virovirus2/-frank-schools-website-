import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Button,
  Box,
  RadioGroup,
  FormControlLabel,
  Radio,
  Typography,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import QRCode from 'qrcode.react';

const VotePage = () => {
  const { electionId } = useParams();
  const navigate = useNavigate();
  const [election, setElection] = useState(null);
  const [selectedCandidate, setSelectedCandidate] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [confirmDialog, setConfirmDialog] = useState(false);
  const [successDialog, setSuccessDialog] = useState(false);
  const [verificationCode, setVerificationCode] = useState('');

  useEffect(() => {
    fetchElection();
  }, [electionId]);

  const fetchElection = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`/api/elections/elections/${electionId}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setElection(response.data);
    } catch (err) {
      console.error('Error fetching election:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVoteSubmit = () => {
    if (!selectedCandidate) {
      alert('Please select a candidate');
      return;
    }
    setConfirmDialog(true);
  };

  const confirmVote = async () => {
    setConfirmDialog(false);
    setSubmitting(true);

    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        '/api/voting/votes/cast_vote/',
        {
          election_id: electionId,
          candidate_id: selectedCandidate,
          device_fingerprint: 'browser-fingerprint', // Add device fingerprinting library
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setVerificationCode(response.data.verification_code);
      setSuccessDialog(true);
    } catch (err) {
      alert(err.response?.data?.error || 'Error casting vote');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <LinearProgress />;
  if (!election) return <Typography>Election not found</Typography>;

  return (
    <Container maxWidth="md">
      <Box sx={{ py: 4 }}>
        <Paper elevation={2} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            {election.title}
          </Typography>
          <Typography variant="body1" paragraph color="textSecondary">
            {election.description}
          </Typography>

          <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
            Select Your Candidate
          </Typography>

          <RadioGroup
            value={selectedCandidate}
            onChange={(e) => setSelectedCandidate(e.target.value)}
          >
            {election.candidates?.map((candidate) => (
              <FormControlLabel
                key={candidate.id}
                value={candidate.id}
                control={<Radio />}
                label={
                  <Box>
                    <Typography variant="body1">{candidate.name}</Typography>
                    <Typography variant="caption" color="textSecondary">
                      {candidate.party} - {candidate.position}
                    </Typography>
                  </Box>
                }
                sx={{ mb: 2 }}
              />
            ))}
          </RadioGroup>

          <Box sx={{ mt: 4, display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={handleVoteSubmit}
              disabled={submitting || !selectedCandidate}
            >
              {submitting ? 'Submitting...' : 'Submit Vote'}
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate('/dashboard')}
            >
              Cancel
            </Button>
          </Box>
        </Paper>
      </Box>

      {/* Confirmation Dialog */}
      <Dialog open={confirmDialog} onClose={() => setConfirmDialog(false)}>
        <DialogTitle>Confirm Your Vote</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to vote for the selected candidate? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialog(false)}>Cancel</Button>
          <Button onClick={confirmVote} variant="contained" color="primary">
            Confirm
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success Dialog with Verification Code */}
      <Dialog open={successDialog} onClose={() => navigate('/dashboard')} maxWidth="sm" fullWidth>
        <DialogTitle>Vote Submitted Successfully</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, py: 2 }}>
            <Typography>Your vote has been securely recorded.</Typography>
            <Typography variant="body2" color="textSecondary">
              Verification Code:
            </Typography>
            <Typography variant="body1" sx={{ fontFamily: 'monospace', mb: 2 }}>
              {verificationCode}
            </Typography>
            {verificationCode && (
              <QRCode value={verificationCode} size={200} />
            )}
            <Typography variant="caption" color="textSecondary">
              Save this verification code to check your vote later.
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => navigate('/dashboard')}
            variant="contained"
            color="primary"
          >
            Done
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default VotePage;
