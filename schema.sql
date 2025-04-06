-- Create users table for PostgreSQL
CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL CHECK (email ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
  is_alumni BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data for users
INSERT INTO users (username, password, email, is_alumni) VALUES
('johndoe', 'e10adc3949ba59abbe56e057f20f883e', 'john.doe@example.com', true),
('janedoe', '25d55ad283aa400af464c76d713c07ad', 'jane.doe@example.com', true),
('adminuser', '5f4dcc3b5aa765d61d8327deb882cf99', 'admin@college.edu', false),
('sarahsmith', '827ccb0eea8a706c4c34a16891f84e7b', 'sarah.smith@example.com', true),
('mikeross', '25f9e794323b453885f5181f1b624d0b', 'mike.ross@example.com', true);
/* Add indexes for frequently queried columns */
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_username ON users (username);

-- Create admin table for PostgreSQL
CREATE TABLE admin (
  admin_id SERIAL PRIMARY KEY,
  user_id INTEGER UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  department VARCHAR(100),
  designation VARCHAR(100),
  privileges JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data for admin
INSERT INTO admin (user_id, department, designation, privileges) VALUES
(3, 'Computer Science', 'Department Head', '{"can_delete_users": true, "can_modify_all": true}');
/* Add index for frequently queried columns */
CREATE INDEX idx_admin_department ON admin (department);

-- Create alumni table for PostgreSQL
CREATE TABLE alumni (
  alumni_id SERIAL PRIMARY KEY,
  user_id INTEGER UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  full_name VARCHAR(100) NOT NULL,
  date_of_birth DATE,
  gender VARCHAR(10) CHECK (gender IN ('Male', 'Female', 'Other')),
  bio TEXT,
  contact_number VARCHAR(20),
  address TEXT,
  graduation_year INTEGER CHECK (graduation_year >= 1900 AND graduation_year <= EXTRACT(YEAR FROM CURRENT_DATE) + 5),
  current_location VARCHAR(100),
  profile_image VARCHAR(255),
  social_media_links JSONB,
  availability_for_mentorship BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data for alumni
INSERT INTO alumni (user_id, full_name, date_of_birth, gender, bio, contact_number, address, graduation_year, current_location, social_media_links, availability_for_mentorship) VALUES
(1, 'John Doe', '1995-05-15', 'Male', 'Software Engineer with passion for web development', '+1-555-123-4567', '123 Main St, San Francisco, CA', 2017, 'San Francisco', '{"linkedin": "linkedin.com/in/johndoe", "github": "github.com/johndoe"}', true),
(2, 'Jane Doe', '1996-08-22', 'Female', 'AI researcher focusing on natural language processing', '+1-555-987-6543', '456 Oak Ave, New York, NY', 2018, 'New York', '{"linkedin": "linkedin.com/in/janedoe", "twitter": "twitter.com/janedoe"}', false),
(4, 'Sarah Smith', '1994-03-12', 'Female', 'Product manager at a leading tech company', '+1-555-222-3333', '789 Pine Blvd, Seattle, WA', 2016, 'Seattle', '{"linkedin": "linkedin.com/in/sarahsmith", "instagram": "instagram.com/sarahsmith"}', true),
(5, 'Mike Ross', '1997-11-08', 'Male', 'Data scientist specializing in machine learning models', '+1-555-444-5555', '101 Cedar St, Boston, MA', 2019, 'Boston', '{"linkedin": "linkedin.com/in/mikeross", "github": "github.com/mikeross"}', true);
/* Add indexes for frequently queried columns */
CREATE INDEX idx_alumni_full_name ON alumni (full_name);
CREATE INDEX idx_alumni_graduation_year ON alumni (graduation_year);
CREATE INDEX idx_alumni_current_location ON alumni (current_location);

-- Create education table for PostgreSQL
CREATE TABLE education (
  education_id SERIAL PRIMARY KEY,
  alumni_id INTEGER NOT NULL REFERENCES alumni(alumni_id) ON DELETE CASCADE,
  degree VARCHAR(100) NOT NULL,
  department VARCHAR(100) NOT NULL,
  institution VARCHAR(100) NOT NULL DEFAULT 'Our College',
  start_year INTEGER NOT NULL CHECK (start_year >= 1900 AND start_year <= EXTRACT(YEAR FROM CURRENT_DATE) + 5),
  end_year INTEGER NOT NULL CHECK (end_year >= start_year AND end_year <= EXTRACT(YEAR FROM CURRENT_DATE) + 8),
  achievements TEXT,
  cgpa DECIMAL(3,2) CHECK (cgpa >= 0 AND cgpa <= 4.0),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data for education
INSERT INTO education (alumni_id, degree, department, institution, start_year, end_year, achievements, cgpa) VALUES
(1, 'Bachelor of Science', 'Computer Science', 'Our College', 2013, 2017, 'Dean''s List all semesters, Winner of Hackathon 2016', 3.85),
(2, 'Bachelor of Engineering', 'Computer Engineering', 'Our College', 2014, 2018, 'Research Assistant, Published paper on AI', 3.92),
(4, 'Master of Science', 'Artificial Intelligence', 'MIT', 2018, 2020, 'Graduate with honors', 3.95),
(4, 'Bachelor of Technology', 'Information Technology', 'Our College', 2012, 2016, 'Class Representative, Winner of Code Competition', 3.75),
(1, 'Master of Science', 'Software Engineering', 'Stanford University', 2017, 2019, 'Thesis on scalable cloud architectures', 3.90);
/* Add indexes for frequently queried columns */
CREATE INDEX idx_education_degree ON education (degree);
CREATE INDEX idx_education_department ON education (department);

-- Create jobs table for PostgreSQL
CREATE TABLE jobs (
  job_id SERIAL PRIMARY KEY,
  alumni_id INTEGER NOT NULL REFERENCES alumni(alumni_id) ON DELETE CASCADE,
  company_name VARCHAR(100) NOT NULL,
  position VARCHAR(100) NOT NULL,
  location VARCHAR(100),
  start_date DATE NOT NULL,
  end_date DATE CHECK (end_date IS NULL OR end_date >= start_date),
  is_current BOOLEAN DEFAULT false,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data for jobs
INSERT INTO jobs (alumni_id, company_name, position, location, start_date, end_date, is_current, description) VALUES
(1, 'Google', 'Software Engineer', 'Mountain View, CA', '2017-06-15', NULL, true, 'Working on Google Cloud Platform services'),
(1, 'Microsoft', 'Junior Developer', 'Redmond, WA', '2017-01-10', '2017-06-10', false, 'Worked on Office 365 integration features'),
(2, 'Facebook', 'AI Researcher', 'Menlo Park, CA', '2018-08-01', NULL, true, 'Developing natural language processing models'),
(3, 'Amazon', 'Product Manager', 'Seattle, WA', '2020-02-15', NULL, true, 'Managing e-commerce analytics products'),
(4, 'Apple', 'UX Designer', 'Cupertino, CA', '2016-07-01', '2021-03-15', false, 'Designed interfaces for iOS applications');

/* Add indexes for frequently queried columns */
CREATE INDEX idx_jobs_company_name ON jobs (company_name);
CREATE INDEX idx_jobs_position ON jobs (position);
CREATE INDEX idx_jobs_is_current ON jobs (is_current);

ALTER TABLE `admin` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

ALTER TABLE `alumni` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

ALTER TABLE `education` ADD FOREIGN KEY (`alumni_id`) REFERENCES `alumni` (`alumni_id`) ON DELETE CASCADE;

ALTER TABLE `jobs` ADD FOREIGN KEY (`alumni_id`) REFERENCES `alumni` (`alumni_id`) ON DELETE CASCADE;