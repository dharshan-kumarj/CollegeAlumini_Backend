
# College Alumni System API Design



## 1️⃣ Auth Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| POST | `/api/auth/register` | Register as alumni or admin | No |
| POST | `/api/auth/login` | Login and receive bearer token | No |

**Register Request Format:**
- `username`: string
- `password`: string
- `email`: string
- `is_alumni`: boolean (true for alumni, false for admin)
- Additional fields based on type (alumni or admin)

**Login Response:**
- Returns JWT token for authentication
- User basic info (id, username, type)

## 2️⃣ Alumni Endpoints (Ultra-Simplified)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| GET | `/api/alumni/profile` | Get complete profile with all data | Yes (Alumni token) |
| POST | `/api/alumni/profile` | Create new entry (education/job) | Yes (Alumni token) |
| PUT | `/api/alumni/profile` | Update existing profile data | Yes (Alumni token) |
| DELETE | `/api/alumni/profile/{type}/{id}` | Delete specific item | Yes (Alumni token) |
| POST | `/api/alumni/profile/image` | Upload profile image | Yes (Alumni token) |

**GET Response:**
- Complete profile including basic info, education history, and job history in one JSON object

**POST Request:**
- `type`: string ("education" or "job")
- Fields relevant to the type being created

**PUT Request:**
- Can handle partial or complete updates
- Must include IDs of records being updated

**DELETE Path Parameters:**
- `type`: "education" or "job"
- `id`: ID of the specific record to delete

## 3️⃣ Admin Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|--------------|
| GET | `/api/admin/alumni` | Get all alumni (paginated) | Yes (Admin token) |
| GET | `/api/admin/alumni/{id}` | Get specific alumni details | Yes (Admin token) |
| PUT | `/api/admin/alumni/{id}` | Update any alumni profile | Yes (Admin token) |
| GET | `/api/admin/alumni/filter` | Filter alumni by criteria | Yes (Admin token) |
| DELETE | `/api/admin/alumni/{id}` | Delete alumni account | Yes (Admin token) |

**Filter Query Parameters:**
- `department`: Filter by department
- `graduation_year`: Filter by graduation year
- `location`: Filter by current location
- `available_for_mentorship`: Filter by mentorship availability

**Admin PUT Request:**
- Similar to alumni PUT but with admin privileges
- Can update any alumni profile data

# Curl Commands to Test Your API

Here are curl commands to test your FastAPI endpoints:

## 1. Register Admin User (dharshankumar)

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/api/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "dharshankumar",
  "password": "12345678",
  "email": "dharshankumar@example.com",
  "is_alumni": false,
  "department": "Computer Science",
  "designation": "System Administrator"
}'
```

## 2. Register Alumni User (dharshan)

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/api/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "dharshan",
  "password": "12345678",
  "email": "dharshan@example.com",
  "is_alumni": true,
  "full_name": "Dharshan Kumar",
  "education": {
    "degree": "Bachelor of Technology",
    "department": "Computer Science",
    "start_year": 2019,
    "end_year": 2023
  }
}'
```

## 3. Login as Admin

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/api/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=dharshankumar&password=12345678'
```

## 4. Login as Alumni

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/api/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=dharshan&password=12345678'
```

## 5. Get Alumni Profile (replace {TOKEN} with your actual token from login)

```bash
curl -X 'GET' \
  'http://0.0.0.0:8000/api/alumni/profile' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {TOKEN}'
```

## 6. Add Education Record to Alumni Profile

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/api/alumni/profile' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {TOKEN}' \
  -H 'Content-Type: application/json' \
  -d '{
  "type": "education",
  "degree": "Master of Science",
  "department": "Artificial Intelligence",
  "institution": "Our College",
  "start_year": 2023,
  "end_year": 2025,
  "achievements": "Research in Deep Learning",
  "cgpa": 3.9
}'
```

## 7. Add Job Record to Alumni Profile

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/api/alumni/profile' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {TOKEN}' \
  -H 'Content-Type: application/json' \
  -d '{
  "type": "job",
  "company_name": "TechCorp",
  "position": "Software Engineer",
  "location": "Bangalore",
  "start_date": "2023-06-01",
  "is_current": true,
  "description": "Full stack development"
}'
```

## 8. Update Alumni Profile

```bash
curl -X 'PUT' \
  'http://0.0.0.0:8000/api/alumni/profile' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {TOKEN}' \
  -H 'Content-Type: application/json' \
  -d '{
  "basic": {
    "full_name": "Dharshan Kumar J",
    "bio": "Software Developer passionate about creating clean code",
    "contact_number": "+91-9876543210",
    "current_location": "Chennai",
    "availability_for_mentorship": true
  }
}'
```

## 9. Admin: Get All Alumni (replace {ADMIN_TOKEN} with admin login token)

```bash
curl -X 'GET' \
  'http://0.0.0.0:8000/api/admin/alumni?page=1&per_page=10' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {ADMIN_TOKEN}'
```

## 10. Admin: Filter Alumni by Department

### 5. curl commands to test the endpoints:

#### Get filter categories:
```bash
curl -X GET "http://127.0.0.1:8000/api/admin/filter-categories" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Filter alumni with various criteria:

```bash
# Filter by department and end year
curl -X GET "http://127.0.0.1:8000/api/admin/alumni/filter?department=Computer%20Science&end_year=2023" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by CGPA (>=3.5)
curl -X GET "http://127.0.0.1:8000/api/admin/alumni/filter?cgpa=3.5" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by company name
curl -X GET "http://127.0.0.1:8000/api/admin/alumni/filter?company_name=Google" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by position
curl -X GET "http://127.0.0.1:8000/api/admin/alumni/filter?position=Software%20Engineer" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by full name
curl -X GET "http://127.0.0.1:8000/api/admin/alumni/filter?full_name=John" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter with multiple criteria
curl -X GET "http://127.0.0.1:8000/api/admin/alumni/filter?department=Computer%20Science&end_year=2023&company_name=Google&position=Software%20Engineer" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

These changes will allow you to filter alumni based on fields from the alumni table (full_name, location), education table (department, start_year, end_year, cgpa, degree), and jobs table (company_name, position). The new endpoint will also provide all available filter options to populate dropdowns and other UI elements in your frontend.

Remember to replace `YOUR_ACCESS_TOKEN` with an actual admin token obtained from logging in.

# Additional Curl Commands for Alumni System API

Here are the requested endpoints for deleting resources, updating images, and admin operations:

## Delete Endpoints

### 1. Delete Alumni Profile (by alumni)

```bash
curl -X 'DELETE' \
  'http://0.0.0.0:8000/api/alumni/profile' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {TOKEN}'
```

### 2. Delete Education Record

```bash
curl -X 'DELETE' \
  'http://0.0.0.0:8000/api/alumni/education/{education_id}' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {TOKEN}'
```

### 3. Delete Job Record

```bash
curl -X 'DELETE' \
  'http://0.0.0.0:8000/api/alumni/job/{job_id}' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {TOKEN}'
```

### 4. Delete Alumni (by admin)

```bash
curl -X 'DELETE' \
  'http://0.0.0.0:8000/api/admin/alumni/{alumni_id}' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {ADMIN_TOKEN}'
```

## Image Update Endpoint

### Update Profile Image

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/api/alumni/profile/image' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {TOKEN}' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/path/to/your/image.jpg'
```

## Admin Operations

### 1. Update Alumni by Admin

```bash
curl -X 'PUT' \
  'http://0.0.0.0:8000/api/admin/alumni/{alumni_id}' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {ADMIN_TOKEN}' \
  -H 'Content-Type: application/json' \
  -d '{
  "basic": {
    "full_name": "Updated Full Name",
    "bio": "Updated bio information",
    "contact_number": "+91-9876543210",
    "current_location": "Bangalore",
    "availability_for_mentorship": true
  },
  "verification_status": "verified"
}'
```

### 2. Get Alumni by ID (for admin)

```bash
curl -X 'GET' \
  'http://0.0.0.0:8000/api/admin/alumni/{alumni_id}' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {ADMIN_TOKEN}'
```

### 3. Add Education Record by Admin

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/api/admin/alumni/{alumni_id}/education' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {ADMIN_TOKEN}' \
  -H 'Content-Type: application/json' \
  -d '{
  "degree": "Master of Technology",
  "department": "Data Science",
  "institution": "Our College",
  "start_year": 2023,
  "end_year": 2025,
  "achievements": "Top of class",
  "cgpa": 3.95
}'
```

### 4. Add Job Record by Admin

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/api/admin/alumni/{alumni_id}/job' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {ADMIN_TOKEN}' \
  -H 'Content-Type: application/json' \
  -d '{
  "company_name": "Google",
  "position": "Senior Developer",
  "location": "Hyderabad",
  "start_date": "2024-01-15",
  "is_current": true,
  "description": "Working on Google Cloud services"
}'
```

### 5. Delete Education Record by Admin

```bash
curl -X 'DELETE' \
  'http://0.0.0.0:8000/api/admin/alumni/{alumni_id}/education/{education_id}' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {ADMIN_TOKEN}'
```

### 6. Delete Job Record by Admin

```bash
curl -X 'DELETE' \
  'http://0.0.0.0:8000/api/admin/alumni/{alumni_id}/job/{job_id}' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {ADMIN_TOKEN}'
```

Remember to replace:
- `{TOKEN}` with the JWT token from alumni login
- `{ADMIN_TOKEN}` with the JWT token from admin login
- `{alumni_id}`, `{education_id}`, and `{job_id}` with actual IDs
- `/path/to/your/image.jpg` with the actual path to your image file

These endpoints follow RESTful API best practices and should integrate well with your PostgreSQL database schema.


