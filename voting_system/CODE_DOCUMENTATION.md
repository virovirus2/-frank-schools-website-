# Voting System - Complete Code Documentation

## Backend Architecture

### Project Structure
```
backend/
├── authentication/
│   ├── models.py      # Voter, OTPToken, AuditLog models
│   ├── views.py       # VoterViewSet with registration & OTP
│   ├── serializers.py # Serializers for voter data
│   └── urls.py        # URL routing
├── elections/
│   ├── models.py      # Election, Candidate, ElectionStats
│   ├── views.py       # ElectionViewSet, CandidateViewSet
│   ├── serializers.py # Serializers for elections
│   └── urls.py        # URL routing
├── voting/
│   ├── models.py      # Vote, VoteVerification models
│   ├── views.py       # VoteViewSet for vote casting
│   ├── serializers.py # Vote serializers
│   ├── encryption.py  # Encryption/decryption service
│   ├── utils.py       # Helper functions
│   └── urls.py        # URL routing
├── results/
│   ├── models.py      # Result, ResultsReport models
│   ├── views.py       # ResultsViewSet for viewing results
│   ├── serializers.py # Result serializers
│   └── urls.py        # URL routing
└── voting_system/
    ├── settings.py    # Django configuration
    ├── urls.py        # Main URL configuration
    ├── wsgi.py        # WSGI application
    ├── middleware.py  # Audit logging middleware
    ├── celery.py      # Celery configuration
    ├── tasks.py       # Async tasks
    └── admin.py       # Django admin configuration
```

## Key Models

### Voter (authentication/models.py)
```python
class Voter(AbstractUser):
    voter_id: Unique identifier
    national_id: Verified national ID
    verification_status: pending/verified/rejected
    has_voted: Boolean flag
    is_eligible: Eligibility status
    failed_login_attempts: Track failed attempts
```

### Election (elections/models.py)
```python
class Election(models.Model):
    title: Election name
    election_type: Type of election
    start_date/end_date: Voting period
    status: draft/pending/active/closed
    candidates: M2M relationship
    is_anonymous: Anonymous voting flag
```

### Vote (voting/models.py)
```python
class Vote(models.Model):
    election: FK to Election
    voter: FK to Voter
    candidate: FK to Candidate
    encrypted_vote: Encrypted vote data
    digital_signature: RSA signature
    verification_hash: Voter verification
    unique_together: (election, voter)
```

### Result (results/models.py)
```python
class Result(models.Model):
    election: FK to Election
    candidate: FK to Candidate
    vote_count: Total votes
    percentage: Vote percentage
    rank: Ranking
```

## API Endpoints

### Authentication Endpoints
- `POST /api/auth/voters/register/` - Register new voter
- `POST /api/auth/voters/send_otp/` - Send OTP code
- `POST /api/auth/voters/verify_otp/` - Verify OTP
- `GET /api/auth/voters/profile/` - Get voter profile
- `GET /api/auth/voters/audit_logs/` - Get audit logs

### Elections Endpoints
- `GET /api/elections/elections/` - List all elections
- `POST /api/elections/elections/` - Create election (Admin)
- `GET /api/elections/elections/{id}/` - Get election details
- `POST /api/elections/elections/{id}/activate/` - Activate
- `POST /api/elections/elections/{id}/close/` - Close
- `GET /api/elections/elections/{id}/statistics/` - Get stats

### Voting Endpoints
- `POST /api/voting/votes/cast_vote/` - Cast vote
- `GET /api/voting/votes/verify_vote/` - Verify vote

### Results Endpoints
- `GET /api/results/results/election_results/` - Get results
- `POST /api/results/results/generate_report/` - Generate report (Admin)

## Frontend Components

### Pages
- **Register.jsx**: Voter registration form
- **Dashboard.jsx**: Main voting interface
- **VotePage.jsx**: Vote casting with confirmation
- **ElectionResults.jsx**: Results with multiple visualizations
- **LiveTurnout.jsx**: Real-time turnout monitoring
- **AdminResults.jsx**: Admin results management

### Charts (using Recharts)

1. **Bar Chart**: Vote count distribution
   ```jsx
   <BarChart data={chartData}>
     <Bar dataKey="votes" fill="#8884d8" />
   </BarChart>
   ```

2. **Pie Chart**: Vote share percentages
   ```jsx
   <PieChart>
     <Pie data={chartData} dataKey="percentage" />
   </PieChart>
   ```

3. **Line Chart**: Turnout trends
   ```jsx
   <LineChart data={turnoutData}>
     <Line type="monotone" dataKey="percentage" />
   </LineChart>
   ```

4. **Area Chart**: Vote accumulation
   ```jsx
   <AreaChart data={turnoutData}>
     <Area type="monotone" dataKey="votes" />
   </AreaChart>
   ```

5. **Composed Chart**: Combined bars and lines
   ```jsx
   <ComposedChart data={data}>
     <Bar dataKey="votes" />
     <Line dataKey="percentage" />
   </ComposedChart>
   ```

## Security Implementation

### Encryption Service (voting/encryption.py)
```python
class EncryptionService:
    - AES-256 for vote encryption
    - RSA-2048 for digital signatures
    - Methods: encrypt(), decrypt(), sign(), verify()
```

### OTP Authentication
- 6-digit codes via SMS/Email
- 5-minute expiration
- Single-use tokens
- Rate limiting

### Audit Logging
- Immutable logs of all actions
- IP address tracking
- User agent recording
- Cannot be deleted

## Deployment

### Docker Setup
```bash
docker-compose up --build
```

Services:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Django Backend (port 8000)
- React Frontend (port 3000)

### Production Checklist
1. Set DEBUG=False
2. Change SECRET_KEY
3. Configure HTTPS
4. Set up database backups
5. Enable rate limiting
6. Configure CORS
7. Set up monitoring
8. Security audit

## Performance Optimization

- Database indexes on frequently queried fields
- Redis caching for session data
- Pagination (20 items per page)
- Rate limiting (100/hour anonymous, 1000/hour authenticated)
- Async tasks via Celery
- Static file compression

## Testing

### Backend Tests
```bash
python manage.py test
```

### Frontend Tests
```bash
npm test
```

## Troubleshooting

### Common Issues

1. **Database connection error**
   - Check PostgreSQL is running
   - Verify DB credentials

2. **CORS errors**
   - Update CORS_ALLOWED_ORIGINS
   - Check frontend API URL

3. **Port conflicts**
   - Change port in settings
   - Check process using port

4. **Redis connection**
   - Ensure Redis is running
   - Check Redis URL in settings

## Support & Documentation

- API Documentation: `docs/API.md`
- Setup Guide: `docs/SETUP.md`
- Security Guide: `docs/SECURITY.md`
- Complete Guide: `COMPLETE_GUIDE.md`
