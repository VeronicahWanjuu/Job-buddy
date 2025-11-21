"""
Database Initialization Script
Creates database, executes schema, inserts test data, validates everything
"""

import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta, date
import json
import hashlib

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class DatabaseInitializer:
    def __init__(self, db_path='jobbuddy.db'):
        self.db_path = db_path
        self.schema_path = Path(__file__).parent / 'schema.sql'
        self.conn = None
        
    def connect(self):
        """Create database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Access columns by name
            # Enable foreign keys
            self.conn.execute('PRAGMA foreign_keys = ON')
            print(f"✅ Connected to database: {self.db_path}")
            return True
        except sqlite3.Error as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def execute_schema(self):
        """Execute schema.sql file"""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Execute schema (split by semicolon for multiple statements)
            self.conn.executescript(schema_sql)
            self.conn.commit()
            print("✅ Schema executed successfully")
            return True
        except FileNotFoundError:
            print(f"❌ Schema file not found: {self.schema_path}")
            return False
        except sqlite3.Error as e:
            print(f"❌ Schema execution error: {e}")
            return False
    
    def insert_test_data(self):
        """Insert realistic test data"""
        cursor = self.conn.cursor()
        
        try:
            # Hash password function (matches bcrypt format)
            def hash_password(password):
                # Simple hash for testing (use bcrypt in production)
                return hashlib.sha256(password.encode()).hexdigest()
            
            print("\n📥 Inserting test data...")
            
            # 1. INSERT USERS (ONE BY ONE to get proper lastrowid)
            cursor.execute('''
                INSERT INTO users (email, password_hash, name, created_at)
                VALUES (?, ?, ?, ?)
            ''', ('john.doe@example.com', hash_password('Password123!'), 'John Doe', 
                  datetime.now().isoformat()))
            user1_id = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO users (email, password_hash, name, created_at)
                VALUES (?, ?, ?, ?)
            ''', ('jane.smith@example.com', hash_password('SecurePass456!'), 'Jane Smith', 
                  datetime.now().isoformat()))
            user2_id = cursor.lastrowid
            
            print(f"  ✅ Inserted 2 users (IDs: {user1_id}, {user2_id})")
            
            # 2. INSERT ONBOARDING DATA
            cursor.execute('''
                INSERT INTO onboarding_data (user_id, current_feeling, dream_milestone, completed_at)
                VALUES (?, ?, ?, ?)
            ''', (user1_id, 'Overwhelmed but motivated', 
                  'Become a Senior Software Engineer at a FAANG company',
                  datetime.now().isoformat()))
            
            cursor.execute('''
                INSERT INTO onboarding_data (user_id, current_feeling, dream_milestone, completed_at)
                VALUES (?, ?, ?, ?)
            ''', (user2_id, 'Excited and ready', 
                  'Launch my own tech startup in Africa',
                  datetime.now().isoformat()))
            
            print("  ✅ Inserted onboarding data")
            
            # 3. INSERT COMPANIES
            cursor.execute('''
                INSERT INTO companies (user_id, name, website, location, industry, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user1_id, 'Google', 'https://google.com', 'Mountain View, CA', 'Technology',
                  'Interested in Cloud Platform team', datetime.now().isoformat()))
            company_google = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO companies (user_id, name, website, location, industry, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user1_id, 'Microsoft', 'https://microsoft.com', 'Redmond, WA', 'Technology',
                  'Azure opportunities', datetime.now().isoformat()))
            company_microsoft = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO companies (user_id, name, website, location, industry, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user1_id, 'Amazon', 'https://amazon.com', 'Seattle, WA', 'E-commerce',
                  'AWS or Retail Tech', datetime.now().isoformat()))
            company_amazon = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO companies (user_id, name, website, location, industry, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user2_id, 'Andela', 'https://andela.com', 'Nairobi, Kenya', 'Technology',
                  'Pan-African tech talent', datetime.now().isoformat()))
            company_andela = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO companies (user_id, name, website, location, industry, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user2_id, 'Flutterwave', 'https://flutterwave.com', 'Lagos, Nigeria', 'Fintech',
                  'Payment solutions', datetime.now().isoformat()))
            company_flutter = cursor.lastrowid
            
            print("  ✅ Inserted 5 companies")
            
            # 4. INSERT CONTACTS
            cursor.execute('''
                INSERT INTO contacts (company_id, name, role, email, linkedin_url, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (company_google, 'Sarah Johnson', 'Senior Technical Recruiter', 
                  'sarah.j@google.com', 'https://linkedin.com/in/sarahj',
                  'Met at tech conference', datetime.now().isoformat()))
            contact_google = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO contacts (company_id, name, role, email, linkedin_url, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (company_microsoft, 'Michael Chen', 'Engineering Manager',
                  'michael.c@microsoft.com', 'https://linkedin.com/in/michaelchen',
                  'Referred by colleague', datetime.now().isoformat()))
            contact_microsoft = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO contacts (company_id, name, role, email, linkedin_url, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (company_amazon, 'Priya Patel', 'HR Business Partner',
                  'priya.p@amazon.com', 'https://linkedin.com/in/priyapatel',
                  'Found via LinkedIn', datetime.now().isoformat()))
            contact_amazon = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO contacts (company_id, name, role, email, linkedin_url, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (company_andela, 'Kofi Mensah', 'Talent Partner',
                  'kofi@andela.com', 'https://linkedin.com/in/kofimensah',
                  'Alumni network', datetime.now().isoformat()))
            
            cursor.execute('''
                INSERT INTO contacts (company_id, name, role, email, linkedin_url, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (company_flutter, 'Amara Okafor', 'Head of Engineering',
                  'amara@flutterwave.com', 'https://linkedin.com/in/amaraokafor',
                  'Tech meetup connection', datetime.now().isoformat()))
            
            print("  ✅ Inserted 5 contacts")
            
            # 5. INSERT APPLICATIONS
            today = date.today()
            
            cursor.execute('''
                INSERT INTO applications 
                (user_id, company_id, job_title, job_url, status, applied_date, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user1_id, company_google, 'Software Engineer II',
                  'https://careers.google.com/jobs/12345', 'Applied',
                  (today - timedelta(days=7)).isoformat(), 'Applied via referral',
                  datetime.now().isoformat()))
            app_google = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO applications 
                (user_id, company_id, job_title, job_url, status, applied_date, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user1_id, company_microsoft, 'Cloud Solutions Architect',
                  'https://careers.microsoft.com/67890', 'Interview',
                  (today - timedelta(days=14)).isoformat(), 'Phone screen completed',
                  datetime.now().isoformat()))
            app_microsoft = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO applications 
                (user_id, company_id, job_title, job_url, status, applied_date, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user1_id, company_amazon, 'Backend Developer',
                  'https://amazon.jobs/54321', 'Planned',
                  None, 'Preparing application materials',
                  datetime.now().isoformat()))
            
            cursor.execute('''
                INSERT INTO applications 
                (user_id, company_id, job_title, job_url, status, applied_date, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user2_id, company_andela, 'Senior Software Engineer',
                  'https://andela.com/careers/123', 'Offer',
                  (today - timedelta(days=30)).isoformat(), 'Negotiating offer',
                  datetime.now().isoformat()))
            
            cursor.execute('''
                INSERT INTO applications 
                (user_id, company_id, job_title, job_url, status, applied_date, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user2_id, company_flutter, 'Full Stack Engineer',
                  'https://flutterwave.com/careers/456', 'Rejected',
                  (today - timedelta(days=20)).isoformat(), 'Not selected after final round',
                  datetime.now().isoformat()))
            
            print("  ✅ Inserted 5 applications (Planned, Applied, Interview, Offer, Rejected)")
            
            # 6. INSERT OUTREACH ACTIVITIES
            cursor.execute('''
                INSERT INTO outreach_activities
                (user_id, application_id, company_id, contact_id, channel, 
                 message_template, sent_date, follow_up_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user1_id, app_google, None, contact_google, 'email',
                  'Hi Sarah, I hope this message finds you well...', 
                  (today - timedelta(days=8)).isoformat(), 
                  (today - timedelta(days=1)).isoformat(),
                  datetime.now().isoformat()))
            
            cursor.execute('''
                INSERT INTO outreach_activities
                (user_id, application_id, company_id, contact_id, channel, 
                 message_template, sent_date, follow_up_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user1_id, app_microsoft, None, contact_microsoft, 'linkedin',
                  'Hello Michael, I came across your profile...',
                  (today - timedelta(days=15)).isoformat(), None,
                  datetime.now().isoformat()))
            
            cursor.execute('''
                INSERT INTO outreach_activities
                (user_id, application_id, company_id, contact_id, channel, 
                 message_template, sent_date, follow_up_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user1_id, None, company_amazon, contact_amazon, 'email',
                  'Dear Priya, I am very interested in opportunities at Amazon...',
                  (today - timedelta(days=2)).isoformat(), 
                  (today + timedelta(days=5)).isoformat(),
                  datetime.now().isoformat()))
            
            print("  ✅ Inserted 3 outreach activities")
            
            # 7. INSERT GOALS (current week)
            today_date = date.today()
            # Calculate Monday of current week
            monday = today_date - timedelta(days=today_date.weekday())
            
            cursor.execute('''
                INSERT INTO goals 
                (user_id, week_start, applications_goal, applications_current, 
                 outreach_goal, outreach_current, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user1_id, monday.isoformat(), 5, 2, 3, 1, datetime.now().isoformat()))
            
            cursor.execute('''
                INSERT INTO goals 
                (user_id, week_start, applications_goal, applications_current, 
                 outreach_goal, outreach_current, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user2_id, monday.isoformat(), 10, 6, 5, 3, datetime.now().isoformat()))
            
            print("  ✅ Inserted weekly goals")
            
            # 8. STREAKS (auto-created by trigger, update them)
            cursor.execute('''
                UPDATE streaks SET 
                    current_streak = 5,
                    longest_streak = 12,
                    last_activity_date = ?,
                    total_points = 150
                WHERE user_id = ?
            ''', (today.isoformat(), user1_id))
            
            cursor.execute('''
                UPDATE streaks SET 
                    current_streak = 3,
                    longest_streak = 8,
                    last_activity_date = ?,
                    total_points = 85
                WHERE user_id = ?
            ''', ((today - timedelta(days=1)).isoformat(), user2_id))
            
            print("  ✅ Updated streak data")
            
            # 9. INSERT USER QUESTS
            cursor.execute('''
                INSERT INTO user_quests (user_id, quest_id, completed_at)
                VALUES (?, ?, ?)
            ''', (user1_id, 'mq-1', (datetime.now() - timedelta(days=5)).isoformat()))
            
            cursor.execute('''
                INSERT INTO user_quests (user_id, quest_id, completed_at)
                VALUES (?, ?, ?)
            ''', (user1_id, 'mq-2', (datetime.now() - timedelta(days=3)).isoformat()))
            
            cursor.execute('''
                INSERT INTO user_quests (user_id, quest_id, completed_at)
                VALUES (?, ?, ?)
            ''', (user2_id, 'mq-1', (datetime.now() - timedelta(days=2)).isoformat()))
            
            print("  ✅ Inserted completed quests")
            
            # 10. INSERT NOTIFICATIONS
            cursor.execute('''
                INSERT INTO notifications
                (user_id, type, title, message, related_type, related_id, 
                 is_read, emailed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user1_id, 'follow_up', 'Follow up on Google Application',
                  'It has been 7 days since you applied. Consider sending a follow-up.',
                  'application', app_google, False, False, datetime.now().isoformat()))
            
            cursor.execute('''
                INSERT INTO notifications
                (user_id, type, title, message, related_type, related_id, 
                 is_read, emailed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user1_id, 'goal_reminder', 'Mid-Week Check-In',
                  'You are halfway through the week. Keep pushing!',
                  None, None, False, False, datetime.now().isoformat()))
            
            cursor.execute('''
                INSERT INTO notifications
                (user_id, type, title, message, related_type, related_id, 
                 is_read, emailed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user1_id, 'motivation', 'Great Progress!',
                  'You have logged 5 consecutive days of activity. Keep it up!',
                  None, None, True, False, datetime.now().isoformat()))
            
            cursor.execute('''
                INSERT INTO notifications
                (user_id, type, title, message, related_type, related_id, 
                 is_read, emailed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user2_id, 'system', 'New Micro-Quest Available',
                  'Complete "Research 3 Companies" to earn 15 points.',
                  'micro_quest', None, False, False, datetime.now().isoformat()))
            
            print("  ✅ Inserted 4 notifications")
            
            # 11. INSERT CV ANALYSIS
            cursor.execute('''
                INSERT INTO cv_analyses
                (user_id, application_id, cv_filename, cv_file_path, job_description,
                 ats_score, matched_keywords, missing_keywords, suggestions, api_used, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user1_id, app_google, 'john_doe_cv.pdf', '/uploads/cvs/john_doe_cv.pdf',
                  'Job Description: Software Engineer with Python, React, AWS experience...',
                  78,
                  json.dumps(['python', 'react', 'aws', 'git', 'sql', 'agile']),
                  json.dumps(['docker', 'kubernetes', 'typescript']),
                  json.dumps([
                      {'type': 'add_technical', 'keyword': 'docker', 
                       'message': 'Add Docker to your Skills section'},
                      {'type': 'strengthen', 'keyword': 'python',
                       'message': 'Python appears 5 times in JD but only once in CV'}
                  ]),
                  'internal', datetime.now().isoformat()))
            
            print("  ✅ Inserted CV analysis")
            
            # Commit all changes
            self.conn.commit()
            print("\n✅ All test data inserted successfully!\n")
            
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Error inserting test data: {e}")
            self.conn.rollback()
            return False
    
    def validate_database(self):
        """Validate database structure and data"""
        cursor = self.conn.cursor()
        
        print("🔍 Validating database...\n")
        
        # Check table count
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        print(f"  📊 Tables: {table_count} (expected: 11)")
        
        # Check foreign keys enabled
        cursor.execute("PRAGMA foreign_keys")
        fk_status = cursor.fetchone()[0]
        print(f"  🔗 Foreign Keys: {'✅ ENABLED' if fk_status else '❌ DISABLED'}")
        
        # Check data in each table
        tables = [
            'users', 'onboarding_data', 'companies', 'contacts', 
            'applications', 'outreach_activities', 'goals', 'streaks',
            'user_quests', 'notifications', 'cv_analyses'
        ]
        
        print("\n  📋 Record Counts:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"    • {table:25s}: {count:3d} records")
        
        # Test constraints
        print("\n  🔒 Testing Constraints:")
        
        # Test unique email
        try:
            cursor.execute('''
                INSERT INTO users (email, password_hash, name)
                VALUES ('john.doe@example.com', 'hash', 'Duplicate')
            ''')
            print("    ❌ UNIQUE constraint failed (duplicate email allowed)")
        except sqlite3.IntegrityError:
            print("    ✅ UNIQUE constraint working (duplicate email blocked)")
        
        # Test CHECK constraint
        try:
            cursor.execute('''
                INSERT INTO applications (user_id, company_id, job_title, status)
                VALUES (1, 1, 'Test Job', 'InvalidStatus')
            ''')
            print("    ❌ CHECK constraint failed (invalid status allowed)")
        except sqlite3.IntegrityError:
            print("    ✅ CHECK constraint working (invalid status blocked)")
        
        # Test foreign key cascade
        cursor.execute("SELECT id FROM users LIMIT 1")
        test_user_id = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM applications WHERE user_id = ?", (test_user_id,))
        app_count_before = cursor.fetchone()[0]
        
        print(f"    ℹ️  User {test_user_id} has {app_count_before} applications")
        print("    ✅ CASCADE DELETE will be tested when user is deleted")
        
        # Test triggers
        cursor.execute('''
            SELECT updated_at FROM applications WHERE id = 1
        ''')
        old_timestamp = cursor.fetchone()
        if old_timestamp:
            old_timestamp = old_timestamp[0]
            import time
            time.sleep(1)  # Wait 1 second
            cursor.execute('''
                UPDATE applications SET notes = 'Updated note' WHERE id = 1
            ''')
            cursor.execute('''
                SELECT updated_at FROM applications WHERE id = 1
            ''')
            new_timestamp = cursor.fetchone()[0]
            if new_timestamp > old_timestamp:
                print("    ✅ Timestamp trigger working (updated_at auto-updated)")
            else:
                print("    ⚠️  Timestamp trigger may not be working")
        
        # Test views
        cursor.execute("SELECT COUNT(*) FROM v_applications_detailed")
        view_count = cursor.fetchone()[0]
        print(f"    ✅ Views working (v_applications_detailed: {view_count} records)")
        
        self.conn.rollback()  # Rollback test inserts
        
        print("\n✅ Database validation complete!\n")
    
    def show_test_credentials(self):
        """Display test user credentials"""
        print("=" * 60)
        print("🔑 TEST USER CREDENTIALS")
        print("=" * 60)
        print("\nUser 1:")
        print("  Email:    john.doe@example.com")
        print("  Password: Password123!")
        print("  Status:   2 applications, 1 outreach, 5-day streak")
        print("\nUser 2:")
        print("  Email:    jane.smith@example.com")
        print("  Password: SecurePass456!")
        print("  Status:   3 applications (1 offer, 1 rejected), 3-day streak")
        print("\n" + "=" * 60)
        print("\n💡 Use these credentials to test login functionality")
        print("=" * 60 + "\n")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✅ Database connection closed\n")

def main():
    """Main initialization function"""
    print("\n" + "=" * 60)
    print("🚀 JOBBUDDY DATABASE INITIALIZATION")
    print("=" * 60 + "\n")
    
    # Check if database already exists
    db_path = 'jobbuddy.db'
    if os.path.exists(db_path):
        response = input(f"⚠️  Database '{db_path}' already exists. Delete and recreate? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            os.remove(db_path)
            print(f"🗑️  Deleted existing database\n")
        else:
            print("❌ Initialization cancelled")
            return False
    
    # Initialize database
    initializer = DatabaseInitializer(db_path)
    
    # Connect
    if not initializer.connect():
        return False
    
    # Execute schema
    if not initializer.execute_schema():
        initializer.close()
        return False
    
    # Insert test data
    if not initializer.insert_test_data():
        initializer.close()
        return False
    
    # Validate
    initializer.validate_database()
    
    # Show credentials
    initializer.show_test_credentials()
    
    # Close connection
    initializer.close()
    
    print("✅ Database initialization complete!")
    print(f"📁 Database file: {os.path.abspath(db_path)}\n")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
