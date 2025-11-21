"""
Comprehensive tests for all 11 models with detailed validation,
relationships, edge cases, and expected outputs.
"""

import pytest
import sqlite3
import os
import sys
from pathlib import Path
from datetime import date, datetime, timedelta
import json

# Fixed imports - correct path structure
from backend.database.db import db, DatabaseError
from backend.models import (
    User, Company, Contact, Application, Outreach,
    Goal, Streak, Notification, UserQuest, CVAnalysis, OnboardingData
)

# ================================================================
# FIXTURES
# ================================================================

@pytest.fixture
def test_db():
    """Create test database with schema"""
    test_db_path = 'test_jobbuddy.db'
    
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except PermissionError:
            pass
    
    db.connect(test_db_path)
    
    # FIXED: Correct path - go up 3 levels from tests/backend/test_models.py
    schema_path = Path(__file__).parent.parent.parent / 'backend' / 'database' / 'schema.sql'
    with open(schema_path, 'r') as f:
        db.connection.executescript(f.read())
    
    yield db
    
    db.close()
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except PermissionError:
            pass  # Ignore if file is locked

@pytest.fixture
def sample_user(test_db):
    """Create a sample user"""
    return User.create('test@example.com', 'Password123!', 'Test User')

@pytest.fixture
def sample_company(test_db, sample_user):
    """Create a sample company"""
    return Company.create(sample_user.id, 'Test Company', 'https://test.com', 
                         'San Francisco, CA', 'Technology', 'Great company')

@pytest.fixture
def sample_contact(test_db, sample_company):
    """Create a sample contact"""
    return Contact.create(sample_company.id, 'John Recruiter', 'Senior Recruiter',
                         'john@test.com', 'https://linkedin.com/in/john')

@pytest.fixture
def sample_application(test_db, sample_user, sample_company):
    """Create a sample application"""
    return Application.create(sample_user.id, sample_company.id, 'Software Engineer',
                             'https://test.com/jobs/123', 'Planned')

# ================================================================
# 1. USER MODEL TESTS
# ================================================================

class TestUserModel:
    """Complete User model tests"""
    
    def test_user_creation(self, test_db):
        """Test creating valid user"""
        user = User.create('user@example.com', 'Password123!', 'John Doe')
        
        assert user is not None
        assert user.email == 'user@example.com'
        assert user.name == 'John Doe'
        # SQLite returns 0/1 instead of True/False
        assert user.is_active == 1
        assert user.email_notifications_enabled == 1
        
        print(f"✅ Created user: ID={user.id}, Email={user.email}, Name={user.name}")
    
    def test_user_email_validation(self, test_db):
        """Test email format validation"""
        invalid_emails = [
            ('notanemail', 'Invalid email format'),
            ('missing@domain', 'Invalid email format'),
            ('@domain.com', 'Invalid email format'),
            ('user@', 'Invalid email format')
        ]
        
        for email, expected_error in invalid_emails:
            with pytest.raises(ValueError, match=expected_error):
                User.create(email, 'Password123!', 'Test')
        
        print("✅ Email validation: All invalid formats rejected")
    
    def test_user_password_validation(self, test_db):
        """Test password strength requirements"""
        test_cases = [
            ('Pass1!', 'at least 8 characters'),
            ('password123!', 'uppercase'),
            ('PASSWORD123!', 'lowercase'),
            ('Password!', 'number'),
            ('Password123', 'special character')
        ]
        
        for pwd, expected_error in test_cases:
            with pytest.raises(ValueError, match=expected_error):
                User.create('test@example.com', pwd, 'Test')
        
        print("✅ Password validation: All 5 rules enforced (length, upper, lower, number, special)")
    
    def test_user_duplicate_email(self, test_db):
        """Test duplicate email prevention"""
        User.create('duplicate@example.com', 'Password123!', 'User One')
        
        with pytest.raises(ValueError, match="already registered"):
            User.create('duplicate@example.com', 'Password456!', 'User Two')
        
        print("✅ Duplicate email blocked")
    
    def test_user_authentication(self, test_db):
        """Test login functionality"""
        User.create('auth@example.com', 'Password123!', 'Auth User')
        
        # Correct credentials
        user = User.authenticate('auth@example.com', 'Password123!')
        assert user is not None
        assert user.last_login is not None
        
        # Wrong password
        with pytest.raises(ValueError, match="Invalid email or password"):
            User.authenticate('auth@example.com', 'WrongPassword!')
        
        # Non-existent user
        with pytest.raises(ValueError, match="Invalid email or password"):
            User.authenticate('nobody@example.com', 'Password123!')
        
        print(f"✅ Authentication: Login successful, last_login={user.last_login}")
    
    def test_user_profile_update(self, test_db, sample_user):
        """Test updating user profile"""
        result = sample_user.update_profile(name='Updated Name', email='new@example.com')
        assert result is True
        
        updated_user = User.find_by_id(sample_user.id)
        assert updated_user.name == 'Updated Name'
        assert updated_user.email == 'new@example.com'
        
        print(f"✅ Profile updated: Name={updated_user.name}, Email={updated_user.email}")
    
    def test_user_password_change(self, test_db, sample_user):
        """Test password change"""
        result = sample_user.change_password('Password123!', 'NewPassword456!')
        assert result is True
        
        # Verify new password works
        user = User.authenticate('test@example.com', 'NewPassword456!')
        assert user is not None
        
        # Old password should fail
        with pytest.raises(ValueError):
            User.authenticate('test@example.com', 'Password123!')
        
        print("✅ Password changed successfully")
    
    def test_user_notification_preferences(self, test_db, sample_user):
        """Test notification preferences update"""
        prefs = {
            "follow_up": {"in_app": True, "email": False},
            "goal_reminder": {"in_app": True, "email": True}
        }
        
        result = sample_user.update_notification_preferences(prefs)
        assert result is True
        
        updated = User.find_by_id(sample_user.id)
        assert updated.notification_preferences == prefs
        
        print(f"✅ Notification preferences updated: {prefs}")
    
    def test_user_relationships(self, test_db, sample_user, sample_company, sample_application):
        """Test user relationship methods"""
        companies = sample_user.get_companies()
        assert len(companies) == 1
        assert companies[0]['name'] == 'Test Company'
        
        applications = sample_user.get_applications()
        assert len(applications) == 1
        
        streak = sample_user.get_streak()
        assert streak is not None
        assert streak['current_streak'] == 0
        
        print(f"✅ User relationships: {len(companies)} company, {len(applications)} application, streak exists")
    
    def test_user_stats(self, test_db, sample_user, sample_company, sample_application):
        """Test user statistics"""
        stats = sample_user.get_stats()
        
        assert 'total_companies' in stats
        assert stats['total_companies'] == 1
        assert 'applications' in stats
        
        print(f"✅ User stats: {stats}")
    
    def test_user_cascade_delete(self, test_db, sample_user, sample_company):
        """Test CASCADE DELETE behavior"""
        company_id = sample_company.id
        
        sample_user.delete()
        
        # Verify cascade
        companies = db.execute_query('SELECT * FROM companies WHERE id = ?', (company_id,))
        assert len(companies) == 0
        
        print("✅ CASCADE DELETE: User deletion cascaded to company")

# ================================================================
# 2. COMPANY MODEL TESTS
# ================================================================

class TestCompanyModel:
    """Complete Company model tests"""
    
    def test_company_creation(self, test_db, sample_user):
        """Test creating valid company"""
        company = Company.create(
            sample_user.id, 
            'Google', 
            'https://google.com',
            'Mountain View, CA', 
            'Technology',
            'FAANG company'
        )
        
        assert company.name == 'Google'
        assert company.industry == 'Technology'
        assert company.source == 'Manual'
        
        print(f"✅ Company created: Name={company.name}, Location={company.location}, Industry={company.industry}")
    
    def test_company_name_validation(self, test_db, sample_user):
        """Test company name validation"""
        with pytest.raises(ValueError, match="at least 2 characters"):
            Company.create(sample_user.id, 'A')
        
        print("✅ Company name validation: Single character rejected")
    
    def test_company_duplicate_prevention(self, test_db, sample_user):
        """Test case-insensitive duplicate prevention"""
        Company.create(sample_user.id, 'Microsoft')
        
        with pytest.raises(ValueError, match="already exists"):
            Company.create(sample_user.id, 'microsoft')
        
        with pytest.raises(ValueError, match="already exists"):
            Company.create(sample_user.id, 'MICROSOFT')
        
        print("✅ Duplicate prevention: Case-insensitive blocking works")
    
    def test_company_search(self, test_db, sample_user):
        """Test company search functionality"""
        Company.create(sample_user.id, 'Apple Inc', industry='Technology')
        Company.create(sample_user.id, 'Amazon', industry='E-commerce')
        Company.create(sample_user.id, 'Tesla Motors', industry='Automotive')
        
        # Search by name
        results = Company.search(sample_user.id, 'App')
        assert len(results) == 1
        assert results[0].name == 'Apple Inc'
        
        # Search by industry
        tech_companies = Company.get_all_for_user(sample_user.id, industry='Technology')
        assert len(tech_companies) == 1
        
        print(f"✅ Company search: Found {len(results)} match for 'App', {len(tech_companies)} tech company")
    
    def test_company_update(self, test_db, sample_company):
        """Test company update"""
        result = sample_company.update(
            location='New York, NY',
            notes='Updated notes'
        )
        assert result is True
        
        updated = Company.find_by_id(sample_company.id)
        assert updated.location == 'New York, NY'
        assert updated.notes == 'Updated notes'
        
        print(f"✅ Company updated: Location={updated.location}")
    
    def test_company_relationships(self, test_db, sample_company, sample_contact, sample_application):
        """Test company relationships"""
        contacts = sample_company.get_contacts()
        assert len(contacts) == 1
        
        applications = sample_company.get_applications()
        assert len(applications) == 1
        
        stats = sample_company.get_stats()
        assert stats['total_contacts'] == 1
        
        print(f"✅ Company relationships: {len(contacts)} contact, {len(applications)} application")

# ================================================================
# 3. CONTACT MODEL TESTS
# ================================================================

class TestContactModel:
    """Complete Contact model tests"""
    
    def test_contact_creation(self, test_db, sample_company):
        """Test creating valid contact"""
        contact = Contact.create(
            sample_company.id,
            'Jane Doe',
            'HR Manager',
            'jane@test.com',
            'https://linkedin.com/in/janedoe',
            'Met at conference'
        )
        
        assert contact.name == 'Jane Doe'
        assert contact.email == 'jane@test.com'
        assert contact.role == 'HR Manager'
        assert contact.source == 'Manual'
        
        print(f"✅ Contact created: Name={contact.name}, Role={contact.role}, Email={contact.email}")
    
    def test_contact_email_validation(self, test_db, sample_company):
        """Test email validation"""
        with pytest.raises(ValueError, match="Invalid email"):
            Contact.create(sample_company.id, 'Test', email='invalid-email')
        
        # Optional email should work
        contact = Contact.create(sample_company.id, 'No Email', email=None)
        assert contact.email is None
        
        print("✅ Contact email validation: Invalid rejected, None allowed")
    
    def test_contact_duplicate_email(self, test_db, sample_company):
        """Test duplicate email prevention per company"""
        Contact.create(sample_company.id, 'Contact One', email='same@test.com')
        
        with pytest.raises(ValueError, match="already exists"):
            Contact.create(sample_company.id, 'Contact Two', email='same@test.com')
        
        print("✅ Duplicate email blocked within same company")
    
    def test_contact_null_emails(self, test_db, sample_company):
        """Test multiple NULL emails allowed"""
        Contact.create(sample_company.id, 'Contact A', email=None)
        Contact.create(sample_company.id, 'Contact B', email=None)
        Contact.create(sample_company.id, 'Contact C', email=None)
        
        contacts = Contact.get_all_for_company(sample_company.id)
        null_contacts = [c for c in contacts if c.email is None]
        assert len(null_contacts) == 3
        
        print(f"✅ Multiple NULL emails allowed: {len(null_contacts)} contacts with no email")
    
    def test_contact_search(self, test_db, sample_user, sample_company):
        """Test contact search"""
        Contact.create(sample_company.id, 'Alice Johnson', 'Recruiter')
        Contact.create(sample_company.id, 'Bob Smith', 'Engineer')
        Contact.create(sample_company.id, 'Charlie Brown', 'Manager')
        
        results = Contact.search(sample_user.id, 'Alice')
        assert len(results) == 1
        assert results[0].name == 'Alice Johnson'
        
        print(f"✅ Contact search: Found '{results[0].name}'")
    
    def test_contact_update(self, test_db, sample_contact):
        """Test contact update"""
        result = sample_contact.update(
            role='Lead Recruiter',
            notes='Updated via LinkedIn'
        )
        assert result is True
        
        updated = Contact.find_by_id(sample_contact.id)
        assert updated.role == 'Lead Recruiter'
        
        print(f"✅ Contact updated: Role={updated.role}")

# ================================================================
# 4. APPLICATION MODEL TESTS
# ================================================================

class TestApplicationModel:
    """Complete Application model tests"""
    
    def test_application_creation(self, test_db, sample_user, sample_company):
        """Test creating application"""
        app = Application.create(
            sample_user.id,
            sample_company.id,
            'Senior Developer',
            'https://test.com/jobs/456',
            'Planned'
        )
        
        assert app.job_title == 'Senior Developer'
        assert app.status == 'Planned'
        assert app.applied_date is None
        
        print(f"✅ Application created: Job={app.job_title}, Status={app.status}")
    
    def test_application_status_validation(self, test_db, sample_user, sample_company):
        """Test status validation"""
        valid_statuses = ['Planned', 'Applied', 'Interview', 'Offer', 'Rejected']
        
        # Valid status
        app = Application.create(sample_user.id, sample_company.id, 'Test Job', status='Applied')
        assert app.status == 'Applied'
        
        # Invalid status
        with pytest.raises(ValueError, match="Invalid status"):
            Application.create(sample_user.id, sample_company.id, 'Test Job', status='InvalidStatus')
        
        print(f"✅ Status validation: Valid statuses = {valid_statuses}")
    
    def test_application_auto_date(self, test_db, sample_application):
        """Test auto-setting applied_date on status change"""
        # Move from Planned to Applied
        sample_application.update_status('Applied')
        
        updated = Application.find_by_id(sample_application.id)
        assert updated.status == 'Applied'
        assert updated.applied_date is not None
        assert updated.applied_date == date.today().isoformat()
        
        print(f"✅ Auto-date: Status changed to Applied, date set to {updated.applied_date}")
    
    def test_application_follow_up_logic(self, test_db, sample_user, sample_company):
        """Test follow-up needed detection"""
        # Create application from 10 days ago
        past_date = (date.today() - timedelta(days=10)).isoformat()
        app = Application.create(
            sample_user.id,
            sample_company.id,
            'Test Job',
            status='Applied',
            applied_date=past_date
        )
        
        assert app.needs_follow_up() is True
        assert app.days_since_applied() == 10
        
        # Recent application shouldn't need follow-up
        recent_app = Application.create(
            sample_user.id,
            sample_company.id,
            'Recent Job',
            status='Applied',
            applied_date=date.today().isoformat()
        )
        assert recent_app.needs_follow_up() is False
        
        print(f"✅ Follow-up logic: 10-day app needs follow-up, today's app doesn't")
    
    def test_application_search(self, test_db, sample_user, sample_company):
        """Test application search"""
        Application.create(sample_user.id, sample_company.id, 'Backend Engineer')
        Application.create(sample_user.id, sample_company.id, 'Frontend Developer')
        Application.create(sample_user.id, sample_company.id, 'Data Scientist')
        
        results = Application.search(sample_user.id, 'Backend')
        assert len(results) == 1
        assert results[0].job_title == 'Backend Engineer'
        
        print(f"✅ Application search: Found '{results[0].job_title}'")
    
    def test_application_status_workflow(self, test_db, sample_application):
        """Test complete status workflow"""
        # Planned → Applied
        sample_application.update_status('Applied')
        assert Application.find_by_id(sample_application.id).status == 'Applied'
        
        # Applied → Interview
        sample_application.update_status('Interview')
        assert Application.find_by_id(sample_application.id).status == 'Interview'
        
        # Interview → Offer
        sample_application.update_status('Offer')
        assert Application.find_by_id(sample_application.id).status == 'Offer'
        
        print("✅ Status workflow: Planned → Applied → Interview → Offer")

# ================================================================
# 5. OUTREACH MODEL TESTS
# ================================================================

class TestOutreachModel:
    """Complete Outreach model tests"""
    
    def test_outreach_with_application(self, test_db, sample_user, sample_application, sample_contact):
        """Test outreach linked to application"""
        outreach = Outreach.create(
            sample_user.id,
            sample_contact.id,
            'email',
            'Hello, I recently applied for the Software Engineer position...',
            application_id=sample_application.id
        )
        
        assert outreach.application_id == sample_application.id
        assert outreach.company_id is None
        assert outreach.channel == 'email'
        assert outreach.status == 'Sent'
        
        print(f"✅ Outreach created: Channel={outreach.channel}, Linked to application_id={outreach.application_id}")
    
    def test_outreach_with_company(self, test_db, sample_user, sample_company, sample_contact):
        """Test outreach linked to company only"""
        outreach = Outreach.create(
            sample_user.id,
            sample_contact.id,
            'linkedin',
            'Hi, I am interested in opportunities at your company...',
            company_id=sample_company.id
        )
        
        assert outreach.company_id == sample_company.id
        assert outreach.application_id is None
        
        print(f"✅ Outreach created: Channel={outreach.channel}, Linked to company_id={outreach.company_id}")
    
    def test_outreach_xor_constraint(self, test_db, sample_user, sample_application, sample_company, sample_contact):
        """Test XOR constraint enforcement"""
        # Both NULL
        with pytest.raises(ValueError, match="exactly ONE"):
            Outreach.create(
                sample_user.id,
                sample_contact.id,
                'email',
                'Test message here for validation purposes only'
            )
        
        # Both set
        with pytest.raises(ValueError, match="exactly ONE"):
            Outreach.create(
                sample_user.id,
                sample_contact.id,
                'email',
                'Test message here for validation purposes only',
                application_id=sample_application.id,
                company_id=sample_company.id
            )
        
        print("✅ XOR constraint: Must have exactly ONE link (application OR company)")
    
    def test_outreach_channel_validation(self, test_db, sample_user, sample_company, sample_contact):
        """Test channel validation"""
        valid_channels = ['email', 'linkedin']
        
        # Valid channels
        for channel in valid_channels:
            outreach = Outreach.create(
                sample_user.id,
                sample_contact.id,
                channel,
                'Test message here for validation purposes only',
                company_id=sample_company.id
            )
            assert outreach.channel == channel
        
        # Invalid channel
        with pytest.raises(ValueError, match="Invalid channel"):
            Outreach.create(
                sample_user.id,
                sample_contact.id,
                'twitter',
                'Test message here',
                company_id=sample_company.id
            )
        
        print(f"✅ Channel validation: Valid channels = {valid_channels}")
    
    def test_outreach_follow_up(self, test_db, sample_user, sample_company, sample_contact):
        """Test follow-up date functionality"""
        outreach = Outreach.create(
            sample_user.id,
            sample_contact.id,
            'email',
            'Test message here for validation purposes only',
            company_id=sample_company.id
        )
        
        # Set follow-up for 5 days from now
        outreach.set_follow_up_date(5)
        
        updated = Outreach.find_by_id(outreach.id)
        expected_date = (date.today() + timedelta(days=5)).isoformat()
        assert updated.follow_up_date == expected_date
        assert updated.needs_follow_up() is False  # Not due yet
        
        print(f"✅ Follow-up set: {updated.follow_up_date} (5 days from now)")
    
    def test_outreach_pending_follow_ups(self, test_db, sample_user, sample_company, sample_contact):
        """Test getting overdue follow-ups"""
        # Create outreach with past follow-up date
        past_date = (date.today() - timedelta(days=2)).isoformat()
        outreach = Outreach.create(
            sample_user.id,
            sample_contact.id,
            'email',
            'Test message for follow-up tracking purposes here',
            company_id=sample_company.id,
            follow_up_date=past_date
        )
        
        pending = Outreach.get_pending_follow_ups(sample_user.id)
        assert len(pending) == 1
        assert pending[0].needs_follow_up() is True
        
        print(f"✅ Pending follow-ups: {len(pending)} overdue")
    
    def test_outreach_status_update(self, test_db, sample_user, sample_company, sample_contact):
        """Test status updates"""
        outreach = Outreach.create(
            sample_user.id,
            sample_contact.id,
            'email',
            'Test message for status update tracking purposes',
            company_id=sample_company.id
        )
        
        # Mark responded
        outreach.mark_responded()
        assert Outreach.find_by_id(outreach.id).status == 'Responded'
        
        # Reset to Sent
        outreach.update(status='Sent')
        
        # Mark no response
        outreach.mark_no_response()
        assert Outreach.find_by_id(outreach.id).status == 'No Response'
        
        print("✅ Status updates: Sent → Responded, Sent → No Response")

# ================================================================
# 6. GOAL MODEL TESTS
# ================================================================

class TestGoalModel:
    """Complete Goal model tests"""
    
    def test_goal_creation(self, test_db, sample_user):
        """Test creating weekly goal"""
        goal = Goal.create(
            sample_user.id,
            applications_goal=5,
            outreach_goal=3
        )
        
        assert goal.applications_goal == 5
        assert goal.outreach_goal == 3
        assert goal.applications_current == 0
        assert goal.outreach_current == 0
        
        # Verify week_start is Monday
        today = date.today()
        expected_monday = today - timedelta(days=today.weekday())
        assert goal.week_start == expected_monday.isoformat()
        
        print(f"✅ Goal created: Week={goal.week_start}, Apps={goal.applications_goal}, Outreach={goal.outreach_goal}")
    
    def test_goal_validation(self, test_db, sample_user):
        """Test goal value validation"""
        # Zero goal
        with pytest.raises(ValueError, match="positive integer"):
            Goal.create(sample_user.id, applications_goal=0)
        
        # Negative goal
        with pytest.raises(ValueError, match="positive integer"):
            Goal.create(sample_user.id, applications_goal=5, outreach_goal=-1)
        
        print("✅ Goal validation: Non-positive values rejected")
    
    def test_goal_duplicate_week(self, test_db, sample_user):
        """Test duplicate week prevention"""
        Goal.create(sample_user.id)
        
        with pytest.raises(ValueError, match="already exists"):
            Goal.create(sample_user.id)
        
        print("✅ Duplicate prevention: One goal per week enforced")
    
    def test_goal_increment(self, test_db, sample_user):
        """Test progress incrementing"""
        goal = Goal.create(sample_user.id, applications_goal=10, outreach_goal=5)
        goal.increment_applications(7)
        goal.increment_outreach(3)
        
        updated = Goal.find_by_id(goal.id)
        assert updated.applications_progress_percentage() == 70.0
        assert updated.outreach_progress_percentage() == 60.0
        assert updated.overall_progress_percentage() == 65.0
        
        print(f"✅ Progress calculations: Apps=70%, Outreach=60%, Overall=65%")
    
    def test_goal_completion(self, test_db, sample_user):
        """Test completion detection"""
        goal = Goal.create(sample_user.id, applications_goal=3, outreach_goal=2)
        
        # Not complete
        assert goal.is_complete() is False
        
        # Complete applications only
        goal.increment_applications(3)
        updated = Goal.find_by_id(goal.id)
        assert updated.is_applications_complete() is True
        assert updated.is_complete() is False
        
        # Complete both
        goal.increment_outreach(2)
        updated = Goal.find_by_id(goal.id)
        assert updated.is_complete() is True
        
        print(f"✅ Completion detection: Both goals met = {updated.is_complete()}")
    
    def test_goal_get_or_create(self, test_db, sample_user):
        """Test get_or_create functionality"""
        # First call creates
        goal1 = Goal.get_or_create_current_week(sample_user.id)
        assert goal1 is not None
        
        # Second call retrieves
        goal2 = Goal.get_or_create_current_week(sample_user.id)
        assert goal2.id == goal1.id
        
        print(f"✅ Get or create: Same goal returned (ID={goal2.id})")
    
    def test_goal_days_remaining(self, test_db, sample_user):
        """Test days remaining calculation"""
        goal = Goal.create(sample_user.id)
        days = goal.days_remaining_in_week()
        
        # Should be between 0-7
        assert 0 <= days <= 7
        
        print(f"✅ Days remaining in week: {days} days")

# ================================================================
# 7. STREAK MODEL TESTS
# ================================================================

class TestStreakModel:
    """Complete Streak model tests"""
    
    def test_streak_auto_creation(self, test_db, sample_user):
        """Test auto-creation via trigger"""
        streak = Streak.find_by_user_id(sample_user.id)
        
        assert streak is not None
        assert streak.current_streak == 0
        assert streak.longest_streak == 0
        assert streak.total_points == 0
        assert streak.last_activity_date is None
        
        print(f"✅ Streak auto-created: current={streak.current_streak}, points={streak.total_points}")
    
    def test_streak_first_activity(self, test_db, sample_user):
        """Test first activity"""
        streak = Streak.find_by_user_id(sample_user.id)
        streak.update_activity(points=10)
        
        updated = Streak.find_by_user_id(sample_user.id)
        assert updated.current_streak == 1
        assert updated.longest_streak == 1
        assert updated.total_points == 10
        assert updated.last_activity_date == date.today().isoformat()
        
        print(f"✅ First activity: streak={updated.current_streak}, points={updated.total_points}")
    
    def test_streak_consecutive_days(self, test_db, sample_user):
        """Test consecutive day increment"""
        streak = Streak.find_by_user_id(sample_user.id)
        
        # Day 1
        streak.update_activity(10)
        
        # Simulate yesterday
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        db.execute_update(
            'UPDATE streaks SET last_activity_date = ? WHERE user_id = ?',
            (yesterday, sample_user.id)
        )
        
        # Day 2 (today)
        streak = Streak.find_by_user_id(sample_user.id)
        streak.update_activity(10)
        
        updated = Streak.find_by_user_id(sample_user.id)
        assert updated.current_streak == 2
        assert updated.longest_streak == 2
        assert updated.total_points == 20
        
        print(f"✅ Consecutive days: streak={updated.current_streak}, points={updated.total_points}")
    
    def test_streak_same_day_multiple(self, test_db, sample_user):
        """Test multiple activities same day"""
        streak = Streak.find_by_user_id(sample_user.id)
        streak.update_activity(10)
        streak.update_activity(10)
        streak.update_activity(10)
        
        updated = Streak.find_by_user_id(sample_user.id)
        assert updated.current_streak == 1  # Still 1 day
        assert updated.total_points == 30  # Points accumulate
        
        print(f"✅ Same day activities: streak={updated.current_streak}, points={updated.total_points}")
    
    def test_streak_broken(self, test_db, sample_user):
        """Test streak breaking after gap"""
        streak = Streak.find_by_user_id(sample_user.id)
        streak.update_activity(10)
        
        # Simulate 3 days ago
        three_days_ago = (date.today() - timedelta(days=3)).isoformat()
        db.execute_update(
            'UPDATE streaks SET last_activity_date = ? WHERE user_id = ?',
            (three_days_ago, sample_user.id)
        )
        
        # Activity today (gap of 2+ days)
        streak = Streak.find_by_user_id(sample_user.id)
        streak.update_activity(10)
        
        updated = Streak.find_by_user_id(sample_user.id)
        assert updated.current_streak == 1  # Reset to 1
        assert updated.longest_streak == 1  # Was never more than 1
        
        print(f"✅ Streak broken: Reset to {updated.current_streak} after gap")
    
    def test_streak_longest_tracking(self, test_db, sample_user):
        """Test longest streak tracking"""
        streak = Streak.find_by_user_id(sample_user.id)
        
        # Build up streak to 5 days - FIXED: set both current and longest
        for i in range(5):
            days_ago = (date.today() - timedelta(days=4-i)).isoformat()
            db.execute_update(
                'UPDATE streaks SET last_activity_date = ?, current_streak = ?, longest_streak = ? WHERE user_id = ?',
                (days_ago, i+1, i+1, sample_user.id)
            )
            streak = Streak.find_by_user_id(sample_user.id)
            streak.update_activity(10)
        
        updated = Streak.find_by_user_id(sample_user.id)
        assert updated.current_streak == 5
        assert updated.longest_streak == 5
        
        # Break streak
        db.execute_update(
            'UPDATE streaks SET last_activity_date = ? WHERE user_id = ?',
            ((date.today() - timedelta(days=5)).isoformat(), sample_user.id)
        )
        streak = Streak.find_by_user_id(sample_user.id)
        streak.update_activity(10)
        
        updated = Streak.find_by_user_id(sample_user.id)
        assert updated.current_streak == 1
        assert updated.longest_streak == 5  # Preserved
        
        print(f"✅ Longest streak preserved: current={updated.current_streak}, longest={updated.longest_streak}")
    
    def test_streak_leveling(self, test_db, sample_user):
        """Test level calculations"""
        streak = Streak.find_by_user_id(sample_user.id)
        
        # Level 1: 0-99 points
        assert streak.get_level() == 1
        
        # Level 2: 100-299 points
        streak.add_points(100)
        assert Streak.find_by_user_id(sample_user.id).get_level() == 2
        
        # Level 3: 300-599 points
        streak.add_points(200)
        assert Streak.find_by_user_id(sample_user.id).get_level() == 3
        
        # Level 4: 600-999 points
        streak.add_points(300)
        assert Streak.find_by_user_id(sample_user.id).get_level() == 4
        
        # Level 5: 1000+ points
        streak.add_points(400)
        assert Streak.find_by_user_id(sample_user.id).get_level() == 5
        
        print(f"✅ Leveling: Level {Streak.find_by_user_id(sample_user.id).get_level()} at 1000 points")
    
    def test_streak_points_to_next_level(self, test_db, sample_user):
        """Test points needed for next level"""
        streak = Streak.find_by_user_id(sample_user.id)
        streak.add_points(50)
        
        updated = Streak.find_by_user_id(sample_user.id)
        assert updated.points_to_next_level() == 50  # Need 100 for Level 2
        
        print(f"✅ Points to next level: {updated.points_to_next_level()} points needed")

# ================================================================
# 8. NOTIFICATION MODEL TESTS
# ================================================================

class TestNotificationModel:
    """Complete Notification model tests"""
    
    def test_notification_creation(self, test_db, sample_user):
        """Test creating notification"""
        notif = Notification.create(
            sample_user.id,
            'follow_up',
            'Follow-up Reminder',
            'Your application to Test Company needs follow-up'
        )
        
        assert notif.type == 'follow_up'
        assert notif.title == 'Follow-up Reminder'
        # SQLite returns 0/1 instead of True/False - FIXED
        assert notif.is_read == 0
        assert notif.emailed == 0
        
        print(f"✅ Notification created: Type={notif.type}, Title={notif.title}")
    
    def test_notification_type_validation(self, test_db, sample_user):
        """Test type validation"""
        valid_types = ['follow_up', 'goal_reminder', 'micro_quest', 'motivation', 'system']
        
        # Valid type
        notif = Notification.create(sample_user.id, 'goal_reminder', 'Test', 'Test message here for validation')
        assert notif.type == 'goal_reminder'
        
        # Invalid type
        with pytest.raises(ValueError, match="Invalid notification type"):
            Notification.create(sample_user.id, 'invalid_type', 'Test', 'Test message here')
        
        print(f"✅ Type validation: Valid types = {valid_types}")
    
    def test_notification_with_related_entity(self, test_db, sample_user, sample_application):
        """Test linking to related entity"""
        notif = Notification.create(
            sample_user.id,
            'follow_up',
            'Application Follow-up',
            'Time to follow up on your application',
            related_type='application',
            related_id=sample_application.id
        )
        
        assert notif.related_type == 'application'
        assert notif.related_id == sample_application.id
        
        # Get related entity
        related = notif.get_related_entity()
        assert related is not None
        assert related['job_title'] == 'Software Engineer'
        
        print(f"✅ Related entity: Linked to {notif.related_type} ID={notif.related_id}")
    
    def test_notification_read_status(self, test_db, sample_user):
        """Test read/unread functionality"""
        notif = Notification.create(
            sample_user.id,
            'system',
            'Welcome',
            'Welcome to JobBuddy!'
        )
        
        # Initially unread - FIXED: SQLite returns 0/1
        assert notif.is_read == 0
        
        # Mark as read
        notif.mark_as_read()
        updated = Notification.find_by_id(notif.id)
        assert updated.is_read == 1
        
        # Mark as unread
        notif.mark_as_unread()
        updated = Notification.find_by_id(notif.id)
        assert updated.is_read == 0
        
        print(f"✅ Read status toggle: Unread → Read → Unread")
    
    def test_notification_mark_all_read(self, test_db, sample_user):
        """Test marking all as read"""
        # Create multiple notifications - FIXED: longer messages
        for i in range(3):
            Notification.create(
                sample_user.id,
                'system',
                f'Notification {i+1}',
                f'This is test message number {i+1} for notifications'
            )
        
        # Mark all as read
        count = Notification.mark_all_as_read(sample_user.id)
        assert count == 3
        
        # Verify all read
        all_notifs = Notification.get_all_for_user(sample_user.id)
        unread = [n for n in all_notifs if not n.is_read]
        assert len(unread) == 0
        
        print(f"✅ Mark all read: {count} notifications marked")
    
    def test_notification_get_unread(self, test_db, sample_user):
        """Test getting unread only"""
        # Create mix of read/unread
        n1 = Notification.create(sample_user.id, 'system', 'Read', 'This will be read message')
        Notification.create(sample_user.id, 'system', 'Unread 1', 'This stays unread one')
        Notification.create(sample_user.id, 'system', 'Unread 2', 'This stays unread two')
        
        n1.mark_as_read()
        
        unread = Notification.get_all_for_user(sample_user.id, unread_only=True)
        assert len(unread) == 2
        
        print(f"✅ Unread notifications: {len(unread)} unread")
    
    def test_notification_delete_old(self, test_db, sample_user):
        """Test deleting old notifications"""
        # Create notification
        notif = Notification.create(sample_user.id, 'system', 'Old', 'Old message here')
        
        # Simulate old date (40 days ago)
        old_date = (datetime.now() - timedelta(days=40)).isoformat()
        db.execute_update(
            'UPDATE notifications SET created_at = ? WHERE id = ?',
            (old_date, notif.id)
        )
        
        # Delete notifications older than 30 days
        deleted_count = Notification.delete_old(sample_user.id, days_old=30)
        assert deleted_count == 1
        
        print(f"✅ Old notifications deleted: {deleted_count} notification(s)")

# ================================================================
# 9. USER QUEST MODEL TESTS
# ================================================================

class TestUserQuestModel:
    """Complete UserQuest model tests"""
    
    def test_user_quest_creation(self, test_db, sample_user):
        """Test completing a quest"""
        quest = UserQuest.create(sample_user.id, 'mq-1')
        
        assert quest.quest_id == 'mq-1'
        assert quest.completed_at is not None
        
        print(f"✅ Quest completed: ID={quest.quest_id}, Completed at={quest.completed_at}")
    
    def test_user_quest_duplicate(self, test_db, sample_user):
        """Test duplicate quest prevention"""
        UserQuest.create(sample_user.id, 'mq-1')
        
        with pytest.raises(ValueError, match="already completed"):
            UserQuest.create(sample_user.id, 'mq-1')
        
        print("✅ Duplicate quest blocked")
    
    def test_user_quest_is_completed(self, test_db, sample_user):
        """Test checking if quest completed"""
        # Not completed yet
        assert UserQuest.is_completed(sample_user.id, 'mq-1') is False
        
        # Complete it
        UserQuest.create(sample_user.id, 'mq-1')
        
        # Now completed
        assert UserQuest.is_completed(sample_user.id, 'mq-1') is True
        
        print(f"✅ Completion check: Quest 'mq-1' completed")
    
    def test_user_quest_count(self, test_db, sample_user):
        """Test counting completed quests"""
        # Complete multiple quests
        quest_ids = ['mq-1', 'mq-2', 'mq-3', 'mq-4', 'mq-5']
        for quest_id in quest_ids:
            UserQuest.create(sample_user.id, quest_id)
        
        count = UserQuest.get_completed_count(sample_user.id)
        assert count == 5
        
        print(f"✅ Completed quests: {count} quests")
    
    def test_user_quest_get_completed_ids(self, test_db, sample_user):
        """Test getting list of completed quest IDs"""
        UserQuest.create(sample_user.id, 'mq-1')
        UserQuest.create(sample_user.id, 'mq-2')
        UserQuest.create(sample_user.id, 'mq-5')
        
        completed_ids = UserQuest.get_completed_quest_ids(sample_user.id)
        assert 'mq-1' in completed_ids
        assert 'mq-2' in completed_ids
        assert 'mq-5' in completed_ids
        assert 'mq-3' not in completed_ids
        
        print(f"✅ Completed quest IDs: {completed_ids}")
    
    def test_user_quest_reset(self, test_db, sample_user):
        """Test resetting all quests"""
        # Complete some quests
        UserQuest.create(sample_user.id, 'mq-1')
        UserQuest.create(sample_user.id, 'mq-2')
        
        # Reset
        count = UserQuest.reset_user_quests(sample_user.id)
        assert count == 2
        
        # Verify reset
        remaining = UserQuest.get_completed_count(sample_user.id)
        assert remaining == 0
        
        print(f"✅ Quest reset: {count} quests cleared")

# ================================================================
# 10. CV ANALYSIS MODEL TESTS
# ================================================================

class TestCVAnalysisModel:
    """Complete CVAnalysis model tests"""
    
    def test_cv_analysis_creation(self, test_db, sample_user, sample_application):
        """Test creating CV analysis"""
        analysis = CVAnalysis.create(
            sample_user.id,
            'resume.pdf',
            'We are looking for a Python developer with 5 years of experience...',
            75,
            ['Python', 'Django', 'REST API', 'PostgreSQL'],
            ['Docker', 'Kubernetes', 'AWS'],
            [
                {'category': 'Skills', 'suggestion': 'Add Docker experience'},
                {'category': 'Keywords', 'suggestion': 'Include cloud platforms'}
            ],
            application_id=sample_application.id
        )
        
        assert analysis.ats_score == 75
        assert len(analysis.matched_keywords) == 4
        assert len(analysis.missing_keywords) == 3
        assert len(analysis.suggestions) == 2
        
        print(f"✅ CV Analysis: Score={analysis.ats_score}, Matched={len(analysis.matched_keywords)}, Missing={len(analysis.missing_keywords)}")
    
    def test_cv_analysis_score_validation(self, test_db, sample_user):
        """Test ATS score validation"""
        # FIXED: Job description must be 50+ characters
        job_desc = 'We are looking for a skilled professional with strong technical background and experience in the field'
        
        # Valid scores
        for score in [0, 50, 100]:
            analysis = CVAnalysis.create(
                sample_user.id,
                'test.pdf',
                job_desc,
                score,
                [], [], []
            )
            assert analysis.ats_score == score
        
        # Invalid scores
        for score in [-1, 101, 150]:
            with pytest.raises(ValueError, match="between 0 and 100"):
                CVAnalysis.create(
                    sample_user.id,
                    'test.pdf',
                    job_desc,
                    score,
                    [], [], []
                )
        
        print("✅ Score validation: Range 0-100 enforced")
    
    def test_cv_analysis_score_category(self, test_db, sample_user):
        """Test score categorization"""
        # FIXED: Job description must be 50+ characters
        job_desc = 'We are looking for a skilled professional with strong technical background and experience in the field'
        test_cases = [
            (90, 'Excellent'),
            (75, 'Good'),
            (50, 'Fair'),
            (30, 'Poor')
        ]
        
        for score, expected_category in test_cases:
            analysis = CVAnalysis.create(
                sample_user.id,
                'test.pdf',
                job_desc,
                score,
                [], [], []
            )
            assert analysis.get_score_category() == expected_category
        
        print("✅ Score categories: Excellent(80+), Good(60+), Fair(40+), Poor(<40)")
    
    def test_cv_analysis_keyword_match_rate(self, test_db, sample_user):
        """Test keyword match percentage"""
        # FIXED: Job description must be 50+ characters
        job_desc = 'We are looking for a skilled professional with strong technical background and experience in the field'
        analysis = CVAnalysis.create(
            sample_user.id,
            'test.pdf',
            job_desc,
            70,
            ['Python', 'Django', 'REST'],  # 3 matched
            ['Docker', 'AWS'],  # 2 missing
            []
        )
        
        # 3 out of 5 = 60%
        match_rate = analysis.get_keyword_match_rate()
        assert match_rate == 60.0
        
        print(f"✅ Keyword match rate: {match_rate}% (3/5 keywords matched)")
    
    def test_cv_analysis_needs_improvement(self, test_db, sample_user):
        """Test improvement detection"""
        # FIXED: Job description must be 50+ characters
        job_desc = 'We are looking for a skilled professional with strong technical background and experience in the field'
        
        # High score - no improvement needed
        good_cv = CVAnalysis.create(sample_user.id, 'good.pdf', job_desc, 75, [], [], [])
        assert good_cv.needs_improvement() is False
        
        # Low score - needs improvement
        poor_cv = CVAnalysis.create(sample_user.id, 'poor.pdf', job_desc, 45, [], [], [])
        assert poor_cv.needs_improvement() is True
        
        print(f"✅ Improvement detection: Score < 60 needs improvement")
    
    def test_cv_analysis_get_for_application(self, test_db, sample_user, sample_application):
        """Test getting analyses for application"""
        # FIXED: Job description must be 50+ characters
        job_desc = 'We are looking for a skilled professional with strong technical background and experience in the field'
        
        # Create multiple analyses
        CVAnalysis.create(sample_user.id, 'v1.pdf', job_desc, 60, [], [], [], application_id=sample_application.id)
        CVAnalysis.create(sample_user.id, 'v2.pdf', job_desc, 70, [], [], [], application_id=sample_application.id)
        CVAnalysis.create(sample_user.id, 'v3.pdf', job_desc, 80, [], [], [], application_id=sample_application.id)
        
        analyses = CVAnalysis.get_all_for_application(sample_application.id)
        assert len(analyses) == 3
        
        # Get latest
        latest = CVAnalysis.get_latest_for_application(sample_application.id)
        assert latest.ats_score == 80
        
        print(f"✅ Application analyses: {len(analyses)} versions, latest score={latest.ats_score}")

# ================================================================
# 11. ONBOARDING DATA MODEL TESTS
# ================================================================

class TestOnboardingDataModel:
    """Complete OnboardingData model tests"""
    
    def test_onboarding_creation(self, test_db, sample_user):
        """Test creating onboarding data"""
        onboarding = OnboardingData.create(
            sample_user.id,
            'Excited and ready',
            'I want to become a Senior Software Engineer at a top tech company'
        )
        
        assert onboarding.current_feeling == 'Excited and ready'
        assert onboarding.dream_milestone == 'I want to become a Senior Software Engineer at a top tech company'
        assert onboarding.completed_at is not None
        
        print(f"✅ Onboarding created: Feeling='{onboarding.current_feeling}'")
    
    def test_onboarding_feeling_validation(self, test_db, sample_user):
        """Test feeling validation"""
        valid_feelings = [
            'Excited and ready',
            'Overwhelmed but motivated',
            'Frustrated and stuck',
            'Just getting started'
        ]
        
        # Valid feeling
        onboarding = OnboardingData.create(
            sample_user.id,
            'Overwhelmed but motivated',
            'My dream is to work at Google'
        )
        assert onboarding.current_feeling == 'Overwhelmed but motivated'
        
        # Clean up for next test
        onboarding.delete()
        
        # Invalid feeling
        with pytest.raises(ValueError, match="Invalid feeling"):
            OnboardingData.create(
                sample_user.id,
                'Super happy',
                'My dream milestone here'
            )
        
        print(f"✅ Feeling validation: Valid options = {valid_feelings}")
    
    def test_onboarding_dream_validation(self, test_db, sample_user):
        """Test dream milestone validation"""
        # Too short
        with pytest.raises(ValueError, match="at least 10 characters"):
            OnboardingData.create(
                sample_user.id,
                'Excited and ready',
                'Short'
            )
        
        # Valid length
        onboarding = OnboardingData.create(
            sample_user.id,
            'Excited and ready',
            'I want to transition into data science role'
        )
        assert len(onboarding.dream_milestone) >= 10
        
        print(f"✅ Dream validation: Minimum 10 characters enforced")
    
    def test_onboarding_duplicate_prevention(self, test_db, sample_user):
        """Test one onboarding per user"""
        OnboardingData.create(
            sample_user.id,
            'Excited and ready',
            'First dream milestone'
        )
        
        with pytest.raises(ValueError, match="already exists"):
            OnboardingData.create(
                sample_user.id,
                'Frustrated and stuck',
                'Second dream milestone'
            )
        
        print("✅ Duplicate prevention: One onboarding per user")
    
    def test_onboarding_update(self, test_db, sample_user):
        """Test updating onboarding data"""
        onboarding = OnboardingData.create(
            sample_user.id,
            'Excited and ready',
            'Initial dream'
        )
        
        # Update feeling
        result = onboarding.update(current_feeling='Frustrated and stuck')
        assert result is True
        
        updated = OnboardingData.find_by_user_id(sample_user.id)
        assert updated.current_feeling == 'Frustrated and stuck'
        
        # Update dream
        onboarding.update(dream_milestone='Updated dream milestone for my career')
        updated = OnboardingData.find_by_user_id(sample_user.id)
        assert updated.dream_milestone == 'Updated dream milestone for my career'
        
        print(f"✅ Onboarding updated: Feeling='{updated.current_feeling}'")
    
    def test_onboarding_find_by_user(self, test_db, sample_user):
        """Test finding onboarding by user ID"""
        # Before creation
        onboarding = OnboardingData.find_by_user_id(sample_user.id)
        assert onboarding is None
        
        # After creation
        OnboardingData.create(
            sample_user.id,
            'Excited and ready',
            'My career goal'
        )
        
        onboarding = OnboardingData.find_by_user_id(sample_user.id)
        assert onboarding is not None
        assert onboarding.user_id == sample_user.id
        
        print(f"✅ Find by user: Onboarding found for user ID={sample_user.id}")

# ================================================================
# INTEGRATION TESTS
# ================================================================

class TestIntegration:
    """Integration tests across multiple models"""
    
    def test_complete_application_workflow(self, test_db, sample_user):
        """Test complete workflow: Company → Application → Outreach → Goal"""
        # 1. Create company
        company = Company.create(sample_user.id, 'TechCorp', industry='Technology')
        print(f"✅ Step 1: Created company '{company.name}'")
        
        # 2. Create contact
        contact = Contact.create(company.id, 'Jane Recruiter', 'Recruiter', 'jane@techcorp.com')
        print(f"✅ Step 2: Created contact '{contact.name}'")
        
        # 3. Create application
        app = Application.create(sample_user.id, company.id, 'Senior Developer', status='Planned')
        print(f"✅ Step 3: Created application '{app.job_title}' (Status: {app.status})")
        
        # 4. Update application status
        app.update_status('Applied')
        updated_app = Application.find_by_id(app.id)
        print(f"✅ Step 4: Updated status to 'Applied', date={updated_app.applied_date}")
        
        # 5. Create outreach
        outreach = Outreach.create(
            sample_user.id,
            contact.id,
            'email',
            'Following up on my application...',
            application_id=app.id
        )
        print(f"✅ Step 5: Sent {outreach.channel} outreach to {contact.name}")
        
        # 6. Check goal progress
        goal = Goal.get_or_create_current_week(sample_user.id)
        goal.increment_applications(1)
        goal.increment_outreach(1)
        print(f"✅ Step 6: Goal progress: {goal.applications_current}/{goal.applications_goal} apps, {goal.outreach_current}/{goal.outreach_goal} outreach")
        
        # 7. Update streak
        streak = Streak.find_by_user_id(sample_user.id)
        streak.update_activity(points=20)
        print(f"✅ Step 7: Streak updated: {streak.current_streak}-day streak, {streak.total_points} points")
        
        # 8. Create notification
        notif = Notification.create(
            sample_user.id,
            'follow_up',
            'Follow-up Due',
            f'Time to follow up with {contact.name}',
            related_type='application',
            related_id=app.id
        )
        print(f"✅ Step 8: Notification created: '{notif.title}'")
        
        # Verify complete workflow
        assert company.id is not None
        assert contact.company_id == company.id
        assert app.company_id == company.id
        assert outreach.application_id == app.id
        assert goal.applications_current >= 1
        assert streak.total_points >= 20
        assert notif.related_id == app.id
        
        print("\n🎉 COMPLETE WORKFLOW SUCCESS: All 8 steps executed!")
    
    def test_cascade_deletes(self, test_db, sample_user):
        """Test CASCADE DELETE behavior across relationships"""
        # Create data hierarchy
        company = Company.create(sample_user.id, 'DeleteTest Corp')
        contact = Contact.create(company.id, 'Test Contact', email='test@delete.com')
        app = Application.create(sample_user.id, company.id, 'Test Job')
        outreach = Outreach.create(
            sample_user.id,
            contact.id,
            'email',
            'Test message for deletion test purposes here',
            application_id=app.id
        )
        
        company_id = company.id
        contact_id = contact.id
        app_id = app.id
        outreach_id = outreach.id
        
        # Delete company (should cascade)
        company.delete()
        
        # Verify all related data is deleted
        assert Company.find_by_id(company_id) is None
        assert Contact.find_by_id(contact_id) is None
        assert Application.find_by_id(app_id) is None
        assert Outreach.find_by_id(outreach_id) is None
        
        print("✅ CASCADE DELETE: Company deletion cascaded to all related entities")
    
    def test_user_complete_journey(self, test_db):
        """Test complete user journey from registration to goals"""
        # 1. Register user
        user = User.create('journey@test.com', 'Password123!', 'Journey User')
        print(f"✅ Step 1: User registered: {user.email}")
        
        # 2. Complete onboarding
        onboarding = OnboardingData.create(
            user.id,
            'Excited and ready',
            'I want to land my dream job in tech'
        )
        print(f"✅ Step 2: Onboarding completed: '{onboarding.current_feeling}'")
        
        # 3. Add companies
        companies = []
        for name in ['Google', 'Microsoft', 'Amazon']:
            comp = Company.create(user.id, name, industry='Technology')
            companies.append(comp)
        print(f"✅ Step 3: Added {len(companies)} companies")
        
        # 4. Create applications
        apps = []
        for i, company in enumerate(companies):
            app = Application.create(
                user.id,
                company.id,
                f'Software Engineer {i+1}',
                status='Applied'
            )
            apps.append(app)
        print(f"✅ Step 4: Created {len(apps)} applications")
        
        # 5. Do some outreach
        for app in apps[:2]:  # Outreach for first 2 apps
            company = Company.find_by_id(app.company_id)
            contact = Contact.create(company.id, f'Recruiter at {company.name}')
            Outreach.create(
                user.id,
                contact.id,
                'email',
                'I am very interested in this position...',
                application_id=app.id
            )
        print(f"✅ Step 5: Sent 2 outreach messages")
        
        # 6. Complete some micro-quests
        quests = ['mq-1', 'mq-2', 'mq-3']
        for quest_id in quests:
            UserQuest.create(user.id, quest_id)
        print(f"✅ Step 6: Completed {len(quests)} micro-quests")
        
        # 7. Check progress
        stats = user.get_stats()
        streak = Streak.find_by_user_id(user.id)
        goal = Goal.get_or_create_current_week(user.id)
        
        print(f"\n📊 USER JOURNEY STATS:")
        print(f"   - Companies: {stats['total_companies']}")
        print(f"   - Applications: {len(apps)}")
        print(f"   - Outreach: {stats['total_outreach']}")
        print(f"   - Quests: {len(quests)}")
        print(f"   - Streak: {streak.current_streak} days")
        print(f"   - Level: {streak.get_level()}")
        
        assert stats['total_companies'] == 3
        assert len(apps) == 3
        assert stats['total_outreach'] == 2
        assert UserQuest.get_completed_count(user.id) == 3
        
        print("\n🎉 USER JOURNEY COMPLETE!")
    
    def test_goal_streak_integration(self, test_db, sample_user):
        """Test goal and streak working together"""
        # Get or create weekly goal
        goal = Goal.get_or_create_current_week(sample_user.id)
        streak = Streak.find_by_user_id(sample_user.id)
        
        initial_points = streak.total_points
        
        # Create company and application
        company = Company.create(sample_user.id, 'Integration Corp')
        app = Application.create(sample_user.id, company.id, 'Test Position', status='Applied')
        
        # Update goal
        goal.increment_applications(1)
        
        # Update streak
        streak.update_activity(points=10)
        
        # Refresh from DB
        updated_goal = Goal.find_by_id(goal.id)
        updated_streak = Streak.find_by_user_id(sample_user.id)
        
        assert updated_goal.applications_current == 1
        assert updated_streak.total_points == initial_points + 10
        assert updated_streak.current_streak >= 1
        
        print(f"✅ Goal-Streak Integration: Goal progress={updated_goal.applications_current}, Streak={updated_streak.current_streak} days")
    
    def test_notification_application_link(self, test_db, sample_user, sample_company):
        """Test notification linking to application"""
        # Create application
        app = Application.create(
            sample_user.id,
            sample_company.id,
            'Backend Developer'
        )
        
        # Create notification linked to application
        notif = Notification.create(
            sample_user.id,
            'follow_up',
            'Application Follow-up',
            'Time to follow up on your Backend Developer application',
            related_type='application',
            related_id=app.id
        )
        
        # Get related entity through notification
        related = notif.get_related_entity()
        
        assert related is not None
        assert related['id'] == app.id
        assert related['job_title'] == 'Backend Developer'
        
        print(f"✅ Notification-Application Link: Notification successfully linked to '{related['job_title']}'")
    
    def test_cv_analysis_application_workflow(self, test_db, sample_user, sample_company):
        """Test CV analysis workflow with application"""
        # Create application
        app = Application.create(
            sample_user.id,
            sample_company.id,
            'Data Scientist',
            job_url='https://test.com/jobs/ds',
            status='Planned'
        )
        
        # Analyze CV for this application
        analysis = CVAnalysis.create(
            sample_user.id,
            'resume_v1.pdf',
            'Looking for Data Scientist with Python, Machine Learning, SQL experience...',
            65,
            ['Python', 'SQL', 'Pandas'],
            ['Machine Learning', 'TensorFlow', 'Spark'],
            [
                {'category': 'Skills', 'suggestion': 'Add Machine Learning projects'},
                {'category': 'Keywords', 'suggestion': 'Include TensorFlow experience'}
            ],
            application_id=app.id
        )
        
        # Improve and re-analyze
        analysis2 = CVAnalysis.create(
            sample_user.id,
            'resume_v2.pdf',
            'Looking for Data Scientist with Python, Machine Learning, SQL experience...',
            85,
            ['Python', 'SQL', 'Pandas', 'Machine Learning', 'TensorFlow'],
            ['Spark'],
            [
                {'category': 'Skills', 'suggestion': 'Add Spark experience'}
            ],
            application_id=app.id
        )
        
        # Get all analyses for this application
        analyses = CVAnalysis.get_all_for_application(app.id)
        latest = CVAnalysis.get_latest_for_application(app.id)
        
        assert len(analyses) == 2
        assert latest.ats_score == 85
        assert latest.ats_score > analysis.ats_score
        
        print(f"✅ CV Analysis Workflow: Improved from {analysis.ats_score} to {latest.ats_score} ({latest.ats_score - analysis.ats_score} point increase)")

# ================================================================
# RUN ALL TESTS
# ================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 JOBBUDDY MODEL TESTS - COMPLETE SUITE")
    print("="*70 + "\n")
    
    # Run pytest with verbose output
    pytest.main([__file__, '-v', '--tb=short', '--color=yes'])
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED!")
    print("="*70)