# Database Schema

## Tables

### voters
- id: UUID Primary Key
- username: String Unique
- voter_id: String Unique
- national_id: String Unique
- email: String
- phone: String
- date_of_birth: Date
- address: Text
- password_hash: String
- verification_status: Enum (pending, verified, rejected)
- has_voted: Boolean
- is_eligible: Boolean
- created_at: DateTime
- updated_at: DateTime
- last_login_attempt: DateTime
- failed_login_attempts: Integer

### candidates
- id: UUID Primary Key
- name: String
- party: String
- position: String
- photo: File
- bio: Text
- created_at: DateTime
- updated_at: DateTime

### elections
- id: UUID Primary Key
- title: String
- description: Text
- election_type: String
- start_date: DateTime
- end_date: DateTime
- status: Enum (draft, pending, active, closed, cancelled)
- max_votes_per_voter: Integer
- is_anonymous: Boolean
- allow_write_ins: Boolean
- created_by: String
- created_at: DateTime
- updated_at: DateTime

### votes
- id: UUID Primary Key
- election_id: UUID FK
- voter_id: UUID FK
- candidate_id: UUID FK
- encrypted_vote: Text
- digital_signature: Text
- timestamp: DateTime
- is_verified: Boolean
- verification_hash: String Unique
- ip_address: IP Address
- device_fingerprint: String

### vote_verification
- id: UUID Primary Key
- vote_id: UUID FK Unique
- verification_code: String Unique
- qr_code: File
- created_at: DateTime

### results
- id: UUID Primary Key
- election_id: UUID FK
- candidate_id: UUID FK
- vote_count: Integer
- percentage: Float
- rank: Integer
- last_updated: DateTime
- Unique: (election_id, candidate_id)

### results_reports
- id: UUID Primary Key
- election_id: UUID FK Unique
- total_votes: Integer
- total_registered: Integer
- turnout_percentage: Float
- invalid_votes: Integer
- winner_id: UUID FK
- report_status: Enum (draft, published, archived)
- pdf_report: File
- excel_report: File
- generated_at: DateTime
- published_at: DateTime
- signed_by: String
- digital_signature: Text

### otp_tokens
- id: Integer Primary Key
- voter_id: UUID FK Unique
- token: String
- created_at: DateTime
- expires_at: DateTime
- is_used: Boolean
- used_at: DateTime

### audit_logs
- id: UUID Primary Key
- voter_id: UUID FK
- action: String
- description: Text
- ip_address: IP Address
- user_agent: Text
- timestamp: DateTime
- status: String

## Indexes

- voters: national_id, voter_id, verification_status
- elections: status, start_date, end_date
- votes: (election_id, timestamp), voter_id, timestamp
- audit_logs: timestamp, (voter_id, timestamp), action
