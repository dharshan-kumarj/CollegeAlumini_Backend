
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


