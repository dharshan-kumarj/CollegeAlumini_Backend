-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_alumni BOOLEAN DEFAULT FALSE,
    is_college_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create alumni table
CREATE TABLE alumni (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    phone VARCHAR(15),
    date_of_birth DATE,
    gender VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50),
    postal_code VARCHAR(20),
    profile_picture VARCHAR(255),
    bio TEXT,
    linkedin_url VARCHAR(255),
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_date TIMESTAMP WITH TIME ZONE,
    verified_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL
);

-- Create departments table
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    hod_name VARCHAR(100),
    established_year INTEGER
);

-- Create education table
CREATE TABLE education (
    id SERIAL PRIMARY KEY,
    alumni_id INTEGER NOT NULL REFERENCES alumni(id) ON DELETE CASCADE,
    department_id INTEGER NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
    degree VARCHAR(100) NOT NULL,
    batch_year_start INTEGER NOT NULL,
    batch_year_end INTEGER NOT NULL,
    major VARCHAR(100),
    minor VARCHAR(100),
    gpa DECIMAL(3,2),
    achievements TEXT
);

-- Create employment table
CREATE TABLE employment (
    id SERIAL PRIMARY KEY,
    alumni_id INTEGER NOT NULL REFERENCES alumni(id) ON DELETE CASCADE,
    company_name VARCHAR(100) NOT NULL,
    job_title VARCHAR(100) NOT NULL,
    industry VARCHAR(100),
    employment_type VARCHAR(20),
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    description TEXT,
    location VARCHAR(100)
);

-- Create skills table
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50)
);

-- Create alumni_skills table
CREATE TABLE alumni_skills (
    id SERIAL PRIMARY KEY,
    alumni_id INTEGER NOT NULL REFERENCES alumni(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    proficiency_level VARCHAR(20),
    UNIQUE(alumni_id, skill_id)
);

-- Create events table
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    event_date DATE NOT NULL,
    event_time TIME,
    location VARCHAR(255),
    event_type VARCHAR(50),
    organizer VARCHAR(100),
    max_participants INTEGER,
    registration_deadline DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create event_participants table
CREATE TABLE event_participants (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    alumni_id INTEGER NOT NULL REFERENCES alumni(id) ON DELETE CASCADE,
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    attendance_status VARCHAR(20) DEFAULT 'Registered',
    feedback TEXT,
    UNIQUE(event_id, alumni_id)
);

-- Create achievements table
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    alumni_id INTEGER NOT NULL REFERENCES alumni(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    achievement_date DATE,
    achievement_type VARCHAR(50),
    organization VARCHAR(100),
    reference_link VARCHAR(255)
);

-- Create job_postings table
CREATE TABLE job_postings (
    id SERIAL PRIMARY KEY,
    alumni_id INTEGER REFERENCES alumni(id) ON DELETE SET NULL,
    company_name VARCHAR(100) NOT NULL,
    job_title VARCHAR(100) NOT NULL,
    job_description TEXT NOT NULL,
    required_skills TEXT,
    experience_years INTEGER,
    location VARCHAR(100),
    job_type VARCHAR(20),
    salary_range VARCHAR(100),
    application_link VARCHAR(255),
    contact_email VARCHAR(100),
    posting_date DATE DEFAULT CURRENT_DATE,
    closing_date DATE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create alumni_connections table
CREATE TABLE alumni_connections (
    id SERIAL PRIMARY KEY,
    initiator_id INTEGER NOT NULL REFERENCES alumni(id) ON DELETE CASCADE,
    receiver_id INTEGER NOT NULL REFERENCES alumni(id) ON DELETE CASCADE, 
    connection_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'Pending',
    UNIQUE(initiator_id, receiver_id)
);