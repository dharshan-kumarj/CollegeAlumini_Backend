from config.main import get_db_connection, hash_password, verify_password, create_jwt_token
import json

# Authentication Services
class AuthService:
    @staticmethod
    def register_user(user_data):
        conn = get_db_connection()
        if not conn:
            return {"error": "Database connection failed"}
        
        try:
            cursor = conn.cursor()
            
            # Hash the password
            user_data["password"] = hash_password(user_data["password"])
            
            # Insert into users table
            cursor.execute(
                """
                INSERT INTO users (username, password, email, is_alumni)
                VALUES (%s, %s, %s, %s) RETURNING user_id
                """,
                (user_data["username"], user_data["password"], user_data["email"], user_data.get("is_alumni", True))
            )
            
            user_id = cursor.fetchone()["user_id"]
            
            # Insert into respective table based on user type
            if user_data.get("is_alumni", True):
                cursor.execute(
                    """
                    INSERT INTO alumni (user_id, full_name) 
                    VALUES (%s, %s) RETURNING alumni_id
                    """,
                    (user_id, user_data.get("full_name", user_data["username"]))
                )
                alumni_id = cursor.fetchone()["alumni_id"]
                
                # Create education record if provided
                if "education" in user_data:
                    edu = user_data["education"]
                    cursor.execute(
                        """
                        INSERT INTO education (alumni_id, degree, department, start_year, end_year)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (alumni_id, edu["degree"], edu["department"], edu["start_year"], edu["end_year"])
                    )
            else:
                # Admin user
                cursor.execute(
                    """
                    INSERT INTO admin (user_id, department, designation) 
                    VALUES (%s, %s, %s)
                    """,
                    (user_id, user_data.get("department", None), user_data.get("designation", None))
                )
            
            conn.commit()
            return {"user_id": user_id, "status": "success"}
        
        except Exception as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            conn.close()

    @staticmethod
    def login_user(username, password):
        conn = get_db_connection()
        if not conn:
            return {"error": "Database connection failed"}
        
        try:
            cursor = conn.cursor()
            
            # Get user from database
            cursor.execute(
                "SELECT user_id, username, password, is_alumni FROM users WHERE username = %s",
                (username,)
            )
            
            user = cursor.fetchone()
            if not user:
                return {"error": "Invalid credentials"}
            
            # Verify password
            if not verify_password(password, user["password"]):
                return {"error": "Invalid credentials"}
            
            # Create access token
            token_data = {
                "sub": str(user["user_id"]),
                "username": user["username"],
                "is_alumni": user["is_alumni"]
            }
            
            # Get specific role details
            if user["is_alumni"]:
                cursor.execute("SELECT alumni_id FROM alumni WHERE user_id = %s", (user["user_id"],))
                alumni = cursor.fetchone()
                token_data["alumni_id"] = alumni["alumni_id"] if alumni else None
            else:
                cursor.execute("SELECT admin_id FROM admin WHERE user_id = %s", (user["user_id"],))
                admin = cursor.fetchone()
                token_data["admin_id"] = admin["admin_id"] if admin else None
            
            token = create_jwt_token(token_data)
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "user_id": user["user_id"],
                "username": user["username"],
                "is_alumni": user["is_alumni"]
            }
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()


# Alumni Services
class AlumniService:
    @staticmethod
    def get_alumni_profile(alumni_id):
        conn = get_db_connection()
        if not conn:
            return {"error": "Database connection failed"}
        
        try:
            cursor = conn.cursor()
            
            # Get basic alumni profile
            cursor.execute("""
                SELECT a.*, u.email, u.username 
                FROM alumni a
                JOIN users u ON a.user_id = u.user_id
                WHERE a.alumni_id = %s
            """, (alumni_id,))
            
            profile = cursor.fetchone()
            if not profile:
                return {"error": "Profile not found"}
            
            # Get education records
            cursor.execute("SELECT * FROM education WHERE alumni_id = %s", (alumni_id,))
            education = cursor.fetchall()
            
            # Get job records
            cursor.execute("SELECT * FROM jobs WHERE alumni_id = %s", (alumni_id,))
            jobs = cursor.fetchall()
            
            # Combine all data
            complete_profile = dict(profile)
            complete_profile["education"] = [dict(edu) for edu in education]
            complete_profile["jobs"] = [dict(job) for job in jobs]
            
            return complete_profile
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def create_profile_entry(alumni_id, entry_data):
        conn = get_db_connection()
        if not conn:
            return {"error": "Database connection failed"}
        
        try:
            cursor = conn.cursor()
            
            # Determine entry type and insert accordingly
            entry_type = entry_data.get("type", "").lower()
            
            if entry_type == "education":
                cursor.execute("""
                    INSERT INTO education 
                    (alumni_id, degree, department, institution, start_year, end_year, achievements, cgpa)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING education_id
                """, (
                    alumni_id,
                    entry_data.get("degree"),
                    entry_data.get("department"),
                    entry_data.get("institution", "Our College"),
                    entry_data.get("start_year"),
                    entry_data.get("end_year"),
                    entry_data.get("achievements"),
                    entry_data.get("cgpa")
                ))
                result = cursor.fetchone()
                conn.commit()
                return {"education_id": result["education_id"], "status": "success"}
                
            elif entry_type == "job":
                cursor.execute("""
                    INSERT INTO jobs 
                    (alumni_id, company_name, position, location, start_date, end_date, is_current, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING job_id
                """, (
                    alumni_id,
                    entry_data.get("company_name"),
                    entry_data.get("position"),
                    entry_data.get("location"),
                    entry_data.get("start_date"),
                    entry_data.get("end_date"),
                    entry_data.get("is_current", False),
                    entry_data.get("description")
                ))
                result = cursor.fetchone()
                conn.commit()
                return {"job_id": result["job_id"], "status": "success"}
            else:
                return {"error": "Invalid entry type"}
            
        except Exception as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def update_alumni_profile(alumni_id, profile_data):
        conn = get_db_connection()
        if not conn:
            return {"error": "Database connection failed"}
        
        try:
            cursor = conn.cursor()
            
            # Update basic alumni information if provided
            if "basic" in profile_data:
                basic = profile_data["basic"]
                fields = []
                values = []
                
                # Dynamically build the update query based on provided fields
                for key, value in basic.items():
                    if key != "alumni_id" and key != "user_id":
                        fields.append(f"{key} = %s")
                        values.append(value)
                
                if fields:
                    values.append(alumni_id)
                    cursor.execute(
                        f"UPDATE alumni SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE alumni_id = %s",
                        values
                    )
            
            # Update education records if provided
            if "education" in profile_data:
                for edu in profile_data["education"]:
                    if "education_id" in edu:
                        # Update existing record
                        fields = []
                        values = []
                        
                        for key, value in edu.items():
                            if key != "education_id":
                                fields.append(f"{key} = %s")
                                values.append(value)
                        
                        if fields:
                            values.append(edu["education_id"])
                            cursor.execute(
                                f"UPDATE education SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE education_id = %s",
                                values
                            )
            
            # Update job records if provided
            if "jobs" in profile_data:
                for job in profile_data["jobs"]:
                    if "job_id" in job:
                        # Update existing record
                        fields = []
                        values = []
                        
                        for key, value in job.items():
                            if key != "job_id":
                                fields.append(f"{key} = %s")
                                values.append(value)
                        
                        if fields:
                            values.append(job["job_id"])
                            cursor.execute(
                                f"UPDATE jobs SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE job_id = %s",
                                values
                            )
            
            conn.commit()
            return {"status": "success"}
            
        except Exception as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def delete_profile_item(alumni_id, item_type, item_id):
        conn = get_db_connection()
        if not conn:
            return {"error": "Database connection failed"}
        
        try:
            cursor = conn.cursor()
            
            if item_type == "education":
                cursor.execute(
                    "DELETE FROM education WHERE education_id = %s AND alumni_id = %s",
                    (item_id, alumni_id)
                )
            elif item_type == "job":
                cursor.execute(
                    "DELETE FROM jobs WHERE job_id = %s AND alumni_id = %s",
                    (item_id, alumni_id)
                )
            else:
                return {"error": "Invalid item type"}
            
            if cursor.rowcount == 0:
                return {"error": "Item not found or unauthorized"}
            
            conn.commit()
            return {"status": "success"}
            
        except Exception as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            conn.close()


# Admin Services
class AdminService:
    @staticmethod
    def get_all_alumni(page=1, per_page=10):
        conn = get_db_connection()
        if not conn:
            return {"error": "Database connection failed"}
        
        try:
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute("SELECT COUNT(*) as total FROM alumni")
            total = cursor.fetchone()["total"]
            
            # Get paginated alumni list
            offset = (page - 1) * per_page
            cursor.execute("""
                SELECT a.*, u.email, u.username 
                FROM alumni a
                JOIN users u ON a.user_id = u.user_id
                ORDER BY a.full_name
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            
            alumni_list = cursor.fetchall()
            
            return {
                "total": total,
                "page": page,
                "per_page": per_page,
                "data": [dict(alumni) for alumni in alumni_list]
            }
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def get_alumni_by_id(alumni_id):
        # Reuse the alumni service method
        return AlumniService.get_alumni_profile(alumni_id)
    
    @staticmethod
    def update_alumni_by_admin(alumni_id, profile_data):
        # Similar to alumni update but with admin privileges
        return AlumniService.update_alumni_profile(alumni_id, profile_data)
    
    @staticmethod
    def filter_alumni(filters):
        conn = get_db_connection()
        if not conn:
            return {"error": "Database connection failed"}
        
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT DISTINCT a.*, u.email, u.username 
                FROM alumni a
                JOIN users u ON a.user_id = u.user_id
            """
            
            # Join with education and jobs tables if needed
            education_filters = ["department", "end_year", "start_year", "cgpa", "degree"]
            job_filters = ["company_name", "position"]
            
            has_education_filter = any(f in filters for f in education_filters)
            has_job_filter = any(f in filters for f in job_filters)
            
            if has_education_filter:
                query += " LEFT JOIN education e ON e.alumni_id = a.alumni_id"
            
            if has_job_filter:
                query += " LEFT JOIN jobs j ON j.alumni_id = a.alumni_id"
            
            query += " WHERE 1=1"
            params = []
            
            # Add alumni table filters
            if "full_name" in filters and filters["full_name"]:
                query += " AND a.full_name ILIKE %s"
                params.append(f"%{filters['full_name']}%")
            
            if "location" in filters and filters["location"]:
                query += " AND a.current_location ILIKE %s"
                params.append(f"%{filters['location']}%")
            
            if "availability_for_mentorship" in filters:
                query += " AND a.availability_for_mentorship = %s"
                params.append(filters["availability_for_mentorship"])
            
            # Add education table filters
            if "department" in filters:
                query += " AND e.department = %s"
                params.append(filters["department"])
            
            if "end_year" in filters:
                query += " AND e.end_year = %s"
                params.append(filters["end_year"])
            
            if "start_year" in filters:
                query += " AND e.start_year = %s"
                params.append(filters["start_year"])
            
            if "cgpa" in filters:
                query += " AND e.cgpa >= %s"
                params.append(filters["cgpa"])
            
            if "degree" in filters:
                query += " AND e.degree = %s"
                params.append(filters["degree"])
            
            # Add job table filters
            if "company_name" in filters:
                query += " AND j.company_name ILIKE %s"
                params.append(f"%{filters['company_name']}%")
            
            if "position" in filters:
                query += " AND j.position ILIKE %s"
                params.append(f"%{filters['position']}%")
            
            cursor.execute(query, params)
            alumni_list = cursor.fetchall()
            
            return {"data": [dict(alumni) for alumni in alumni_list]}
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()

    @staticmethod
    def get_filter_categories():
        conn = get_db_connection()
        if not conn:
            return {"error": "Database connection failed"}
        
        try:
            cursor = conn.cursor()
            categories = {}
            
            # Get all departments
            cursor.execute("SELECT DISTINCT department FROM education WHERE department IS NOT NULL")
            departments = [row["department"] for row in cursor.fetchall()]
            categories["departments"] = departments
            
            # Get all graduation years
            cursor.execute("SELECT DISTINCT end_year FROM education WHERE end_year IS NOT NULL ORDER BY end_year DESC")
            grad_years = [row["end_year"] for row in cursor.fetchall()]
            categories["graduation_years"] = grad_years
            
            # Get all start years
            cursor.execute("SELECT DISTINCT start_year FROM education WHERE start_year IS NOT NULL ORDER BY start_year DESC")
            start_years = [row["start_year"] for row in cursor.fetchall()]
            categories["start_years"] = start_years
            
            # Get all degrees
            cursor.execute("SELECT DISTINCT degree FROM education WHERE degree IS NOT NULL")
            degrees = [row["degree"] for row in cursor.fetchall()]
            categories["degrees"] = degrees
            
            # Get all companies
            cursor.execute("SELECT DISTINCT company_name FROM jobs WHERE company_name IS NOT NULL")
            companies = [row["company_name"] for row in cursor.fetchall()]
            categories["companies"] = companies
            
            # Get all positions
            cursor.execute("SELECT DISTINCT position FROM jobs WHERE position IS NOT NULL")
            positions = [row["position"] for row in cursor.fetchall()]
            categories["positions"] = positions
            
            # Get all locations from alumni
            cursor.execute("SELECT DISTINCT current_location FROM alumni WHERE current_location IS NOT NULL")
            locations = [row["current_location"] for row in cursor.fetchall()]
            categories["locations"] = locations
            
            return categories
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()
    
    @staticmethod
    def delete_alumni(alumni_id):
        conn = get_db_connection()
        if not conn:
            return {"error": "Database connection failed"}
        
        try:
            cursor = conn.cursor()
            
            # Get user_id for this alumni
            cursor.execute("SELECT user_id FROM alumni WHERE alumni_id = %s", (alumni_id,))
            result = cursor.fetchone()
            if not result:
                return {"error": "Alumni not found"}
                
            user_id = result["user_id"]
            
            # Delete the user (cascade will delete alumni record too)
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            
            conn.commit()
            return {"status": "success"}
            
        except Exception as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            conn.close()
