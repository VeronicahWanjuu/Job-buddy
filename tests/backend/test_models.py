"""
Complete Model Tests
Tests all models with expected outputs
Run: pytest tests/backend/test_models.py -v -s
"""

import pytest
import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime, date, timedelta

# Ensure project root is on sys.path so we can import backend.*
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.database.db import db, DatabaseError

from backend.models.user import User
from backend.models.company import Company
from backend.models.contact import Contact
from backend.models.application import Application
from backend.models.outreach import Outreach
from backend.models.goal import Goal
from backend.models.streak import Streak
from backend.models.user_quest import UserQuest
from backend.models.notification import Notification
from backend.models.cv_analysis import CVAnalysis


@pytest.fixture
def test_db():
    """Create test database with schema"""
    test_db_path = 'test_models.db'
    
    # Remove if exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Create database
    db.connect(test_db_path)
    
    # Execute schema
    schema_path = Path(__file__).parent.parent / 'backend' / 'database' / 'schema.sql'
    with open(schema_path, 'r') as f:
        db.connection.executescript(f.read())
    
    yield db
    
    # Cleanup
    db.close()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


# ================================================================
# TEST 1: USER MODEL
# ================================================================
def test_user_create_and_authenticate(test_db):
    """Test user creation and authentication"""
    print("\n" + "="*60)
    print("TEST 1: USER MODEL")
    print("="*60)
    
    # Create user
    user = User.create('test@example.com', 'Password123!', 'Test User')
    
    assert user is not None
    assert user.id is not None
    assert user.email == 'test@example.com'
    assert user.name == 'Test User'
    assert user.is_active is True
    
    print(f"✅ User created: ID={user.id}, Email={user.email}, Name={user.name}")
    
    # Authenticate
    auth_user = User.authenticate('test@example.com', 'Password123!')
    assert auth_user is not None
    assert auth_user.id == user.id
    
    print(f"✅ Authentication successful: User ID={auth_user.id}")
    
    # Test wrong password
    with pytest.raises(ValueError, match="Invalid email or password"):
        User.authenticate('test@example.com', 'WrongPassword!')
    
    print("✅ Wrong password rejected")
    
    # Test duplicate email
    with pytest.raises(ValueError, match="already registered"):
        User.create('test@example.com', 'NewPassword123!', 'Duplicate')
    
    print("✅ Duplicate email rejected")
    
    return user


# ================================================================
# TEST 3: COMPANY MODEL
# ================================================================
def test_company_crud(test_db):
    """Test company CRUD operations"""
    print("\n" + "="*60)
    print("TEST 3: COMPANY MODEL")
    print("="*60)
    
    # Create user
    user = User.create('company@example.com', 'Password123!', 'Company User')
    print(f"✅ User created: ID={user.id}")
    
    # Create company
    company = Company.create(
        user.id,
        'Google',
        'https://google.com',
        'Mountain View, CA',
        'Technology',
        'Interested in Cloud Platform team'
    )
    
    assert company is not None
    assert company.name == 'Google'
    assert company.website == 'https://google.com'
    assert company.location == 'Mountain View, CA'
    
    print(f"✅ Company created: ID={company.id}, Name={company.name}")
    
    # Test duplicate company name (case-insensitive)
    with pytest.raises(ValueError, match="already exists"):
        Company.create(user.id, 'google', 'https://google.com', 'CA', 'Tech')
    
    print("✅ Duplicate company name rejected")
    
    # Update company
    success = company.update(location='San Francisco, CA', notes='Updated notes')
    assert success is True
    
    print(f"✅ Company updated: Location={company.location}")
    
    # Find by user
    companies = Company.find_by_user(user.id)
    assert len(companies) == 1
    
    print(f"✅ Found {len(companies)} companies for user")
    
    return company


# ================================================================
# TEST 4: CONTACT MODEL
# ================================================================
def test_contact_crud(test_db):
    """Test contact CRUD operations"""
    print("\n" + "="*60)
    print("TEST 4: CONTACT MODEL")
    print("="*60)
    
    # Create user and company
    user = User.create('contact@example.com', 'Password123!', 'Contact User')
    company = Company.create(user.id, 'Microsoft', 'https://microsoft.com')
    
    print(f"✅ User created: ID={user.id}")
    print(f"✅ Company created: ID={company.id}, Name={company.name}")
    
    # Create contact
    contact = Contact.create(
        company.id,
        'John Doe',
        'Senior Recruiter',
        'john@microsoft.com',
        'https://linkedin.com/in/johndoe',
        'Met at tech conference'
    )
    
    assert contact is not None
    assert contact.name == 'John Doe'
    assert contact.email == 'john@microsoft.com'
    
    print(f"✅ Contact created: ID={contact.id}, Name={contact.name}")
    print(f"   Role: {contact.role}")
    print(f"   Email: {contact.email}")
    
    # Test duplicate email at same company
    with pytest.raises(ValueError, match="already exists"):
        Contact.create(company.id, 'Jane Doe', 'Manager', 'john@microsoft.com')
    
    print("✅ Duplicate email rejected")
    
    # Test invalid email
    with pytest.raises(ValueError, match="Invalid email"):
        Contact.create(company.id, 'Invalid', 'Role', 'not-an-email')
    
    print("✅ Invalid email rejected")
    
    # Test multiple NULL emails (should work)
    contact2 = Contact.create(company.id, 'Contact 2', 'Role', None)
    contact3 = Contact.create(company.id, 'Contact 3', 'Role', None)
    
    print("✅ Multiple NULL emails allowed")
    
    return contact


# ================================================================
# TEST 5: APPLICATION MODEL
# ================================================================
def test_application_status_flow(test_db):
    """Test application status management"""
    print("\n" + "="*60)
    print("TEST 5: APPLICATION MODEL")
    print("="*60)
    
    # Create user and company
    user = User.create('app@example.com', 'Password123!', 'App User')
    company = Company.create(user.id, 'Amazon', 'https://amazon.com')
    
    print(f"✅ User created: ID={user.id}")
    print(f"✅ Company created: ID={company.id}")
    
    # Create application
    app = Application.create(
        user.id,
        company.id,
        'Backend Developer',
        'https://amazon.jobs/12345',
        'Planned',
        'Preparing application'
    )
    
    assert app is not None
    assert app.status == 'Planned'
    assert app.applied_date is None
    
    print(f"✅ Application created: ID={app.id}, Status={app.status}")
    
    # Update status to Applied
    success = app.update_status('Applied')
    assert success is True
    assert app.status == 'Applied'
    assert app.applied_date is not None
    
    print(f"✅ Status updated to Applied, Date set: {app.applied_date}")
    
    # Update to Interview
    app.update_status('Interview')
    print("✅ Status updated to Interview")
    
    # Update to Offer
    app.update_status('Offer')
    print("✅ Status updated to Offer")
    
    # Test invalid status
    with pytest.raises(ValueError, match="Invalid status"):
        app.update_status('InvalidStatus')
    
    print("✅ Invalid status rejected")
    
    # Test get with company details
    apps = Application.get_with_company_details(user.id)
    assert len(apps) == 1
    assert apps[0]['company_name'] == 'Amazon'
    
    print("✅ Retrieved application with company details")
    
    return app


# ================================================================
# TEST 6: OUTREACH MODEL
# ================================================================
def test_outreach_activity(test_db):
    """Test outreach activity creation and constraints"""
    print("\n" + "="*60)
    print("TEST 6: OUTREACH MODEL")
    print("="*60)
    
    # Setup
    user = User.create('outreach@example.com', 'Password123!', 'Outreach User')
    company = Company.create(user.id, 'Tesla', 'https://tesla.com')
    contact = Contact.create(company.id, 'Elon Musk', 'CEO', 'elon@tesla.com')
    app = Application.create(user.id, company.id, 'Engineer', status='Applied')
    
    print(f"✅ Setup complete: User={user.id}, Company={company.id}, Contact={contact.id}")
    
    # Create outreach linked to application
    outreach = Outreach.create(
        user.id,
        contact.id,
        'email',
        'Dear Elon, I am very interested in the Engineer position...',
        date.today().isoformat(),
        application_id=app.id
    )
    
    assert outreach is not None
    assert outreach.application_id == app.id
    assert outreach.company_id is None
    assert outreach.channel == 'email'
    
    print(f"✅ Outreach created: ID={outreach.id}, Channel={outreach.channel}")
    
    # Test exactly-one constraint (both NULL should fail)
    with pytest.raises(ValueError, match="EXACTLY ONE"):
        Outreach.create(
            user.id, contact.id, 'email', 'Test message',
            date.today().isoformat()
        )
    
    print("✅ Both NULL rejected")
    
    # Test both set should fail
    with pytest.raises(ValueError, match="EXACTLY ONE"):
        Outreach.create(
            user.id, contact.id, 'email', 'Test message',
            date.today().isoformat(),
            application_id=app.id,
            company_id=company.id
        )
    
    print("✅ Both set rejected")
    
    # Test invalid channel
    with pytest.raises(ValueError, match="Invalid channel"):
        Outreach.create(
            user.id, contact.id, 'phone', 'Test',
            date.today().isoformat(), company_id=company.id
        )
    
    print("✅ Invalid channel rejected")
    
    return outreach


# ================================================================
# TEST 7: GOAL MODEL
# ================================================================
def test_goal_tracking(test_db):
    """Test weekly goal tracking"""
    print("\n" + "="*60)
    print("TEST 7: GOAL MODEL")
    print("="*60)
    
    # Create user
    user = User.create('goal@example.com', 'Password123!', 'Goal User')
    print(f"✅ User created: ID={user.id}")
    
    # Create goal
    goal = Goal.create(user.id, applications_goal=10, outreach_goal=5)
    
    assert goal is not None
    assert goal.applications_goal == 10
    assert goal.outreach_goal == 5
    assert goal.applications_current == 0
    assert goal.outreach_current == 0
    
    print(f"✅ Goal created: ID={goal.id}")
    print(f"   Applications: {goal.applications_current}/{goal.applications_goal}")
    print(f"   Outreach: {goal.outreach_current}/{goal.outreach_goal}")
    
    # Increment applications
    goal.increment_applications()
    goal.increment_applications()
    
    assert goal.applications_current == 2
    print(f"✅ Incremented applications: {goal.applications_current}/{goal.applications_goal}")
    
    # Increment outreach
    goal.increment_outreach()
    
    assert goal.outreach_current == 1
    print(f"✅ Incremented outreach: {goal.outreach_current}/{goal.outreach_goal}")
    
    # Get progress
    progress = goal.get_progress()
    
    assert progress['applications_current'] == 2
    assert progress['outreach_current'] == 1
    
    print("✅ Progress calculated:")
    print(f"   Applications: {progress['applications_percentage']}%")
    print(f"   Outreach: {progress['outreach_percentage']}%")
    print(f"   Overall: {progress['overall_percentage']}%")
    
    return goal


# ================================================================
# TEST 8: STREAK MODEL
# ================================================================
def test_streak_logic(test_db):
    """Test streak calculation and milestones"""
    print("\n" + "="*60)
    print("TEST 8: STREAK MODEL")
    print("="*60)
    
    # Create user (streak auto-created by trigger)
    user = User.create('streak@example.com', 'Password123!', 'Streak User')
    print(f"✅ User created: ID={user.id}")
    
    # Get streak (should be auto-created)
    streak = Streak.find_by_user(user.id)
    
    assert streak is not None
    assert streak.current_streak == 0
    assert streak.total_points == 0
    
    print(f"✅ Streak auto-created: ID={streak.id}")
    print(f"   Current Streak: {streak.current_streak} days")
    print(f"   Total Points: {streak.total_points}")
    
    # Update streak (first activity)
    Streak.update_streak(user.id)
    streak = Streak.find_by_user(user.id)
    
    assert streak.current_streak == 1
    assert streak.total_points == 10
    
    print("✅ First activity logged:")
    print(f"   Current Streak: {streak.current_streak} days")
    print(f"   Total Points: {streak.total_points}")
    
    # Get level
    level_info = streak.get_level()
    
    assert level_info['level'] == 'Getting Started'
    print(f"✅ Level: {level_info['level']}")
    
    # Add points
    streak.add_points(150)
    
    assert streak.total_points == 160
    print(f"✅ Added 150 points: Total={streak.total_points}")
    
    # Check new level
    level_info = streak.get_level()
    assert level_info['level'] == 'Rising Star'
    print(f"✅ New Level: {level_info['level']}")
    
    return streak


# ================================================================
# TEST 9: USER QUEST MODEL
# ================================================================
def test_user_quest(test_db):
    """Test quest completion tracking"""
    print("\n" + "="*60)
    print("TEST 9: USER QUEST MODEL")
    print("="*60)
    
    # Create user
    user = User.create('quest@example.com', 'Password123!', 'Quest User')
    print(f"✅ User created: ID={user.id}")
    
    # Complete a quest
    quest = UserQuest.create(user.id, 'mq-1')
    
    assert quest is not None
    assert quest.quest_id == 'mq-1'
    
    print(f"✅ Quest completed: ID={quest.id}, Quest={quest.quest_id}")
    
    # Check if completed
    is_completed = UserQuest.is_completed(user.id, 'mq-1')
    assert is_completed is True
    
    print("✅ Quest marked as completed")
    
    # Try to complete again (should fail)
    with pytest.raises(ValueError, match="already completed"):
        UserQuest.create(user.id, 'mq-1')
    
    print("✅ Duplicate completion rejected")
    
    # Complete another quest
    UserQuest.create(user.id, 'mq-2')
    UserQuest.create(user.id, 'mq-3')
    
    # Get completed quests
    completed = UserQuest.get_completed_quest_ids(user.id)
    assert len(completed) == 3
    assert 'mq-1' in completed
    assert 'mq-2' in completed
    assert 'mq-3' in completed
    
    print(f"✅ Total quests completed: {len(completed)}")
    print(f"   Quest IDs: {', '.join(completed)}")
    
    return quest


# ================================================================
# TEST 10: NOTIFICATION MODEL
# ================================================================
def test_notification_system(test_db):
    """Test notification creation and management"""
    print("\n" + "="*60)
    print("TEST 10: NOTIFICATION MODEL")
    print("="*60)
    
    # Create user
    user = User.create('notif@example.com', 'Password123!', 'Notif User')
    print(f"✅ User created: ID={user.id}")
    
    # Create notification
    notif = Notification.create(
        user.id,
        'motivation',
        'Great Progress!',
        'You are doing amazing! Keep it up! 🚀',
        is_read=False
    )
    
    assert notif is not None
    assert notif.type == 'motivation'
    assert notif.is_read is False
    
    print(f"✅ Notification created: ID={notif.id}")
    print(f"   Type: {notif.type}")
    print(f"   Title: {notif.title}")
    print(f"   Message: {notif.message}")
    
    # Get unread count
    unread_count = Notification.get_unread_count(user.id)
    assert unread_count == 1
    
    print(f"✅ Unread notifications: {unread_count}")
    
    # Mark as read
    notif.mark_as_read()
    assert notif.is_read is True
    
    print("✅ Notification marked as read")
    
    # Check unread count again
    unread_count = Notification.get_unread_count(user.id)
    assert unread_count == 0
    
    print(f"✅ Unread notifications after read: {unread_count}")
    
    # Create multiple notifications
    Notification.create(user.id, 'system', 'System Update', 'New features available')
    Notification.create(user.id, 'follow_up', 'Follow Up', 'Check your applications')
    
    # Find all
    all_notifs = Notification.find_by_user(user.id)
    assert len(all_notifs) == 3
    
    print(f"✅ Total notifications: {len(all_notifs)}")
    
    return notif


# ================================================================
# TEST 11: CV ANALYSIS MODEL
# ================================================================
def test_cv_analysis(test_db):
    """Test CV analysis creation and scoring"""
    print("\n" + "="*60)
    print("TEST 11: CV ANALYSIS MODEL")
    print("="*60)
    
    # Setup
    user = User.create('cv@example.com', 'Password123!', 'CV User')
    company = Company.create(user.id, 'Facebook', 'https://facebook.com')
    app = Application.create(user.id, company.id, 'Software Engineer')
    
    print(f"✅ Setup complete: User={user.id}, Application={app.id}")
    
    # Create CV analysis
    analysis = CVAnalysis.create(
        user.id,
        'john_cv.pdf',
        'Job Description: Looking for a Software Engineer with Python, React, AWS experience...',
        78,
        ['python', 'react', 'aws', 'git'],
        ['docker', 'kubernetes', 'typescript'],
        [
            {'type': 'add_technical', 'keyword': 'docker', 'message': 'Add Docker to skills'},
            {'type': 'strengthen', 'keyword': 'python', 'message': 'Mention Python more'}
        ],
        application_id=app.id
    )
    
    assert analysis is not None
    assert analysis.ats_score == 78
    assert len(analysis.matched_keywords) == 4
    assert len(analysis.missing_keywords) == 3
    
    print(f"✅ CV Analysis created: ID={analysis.id}")
    print(f"   ATS Score: {analysis.ats_score}/100")
    print(f"   Matched Keywords: {len(analysis.matched_keywords)}")
    print(f"   Missing Keywords: {len(analysis.missing_keywords)}")
    
    # Get score category
    category = analysis.get_score_category()
    
    assert category['category'] == 'Good'
    print(f"✅ Score Category: {category['emoji']} {category['category']}")
    print(f"   Message: {category['message']}")
    
    # Test invalid score
    with pytest.raises(ValueError, match="between 0 and 100"):
        CVAnalysis.create(
            user.id, 'test.pdf', 'Job description', 150,
            [], [], []
        )
    
    print("✅ Invalid score rejected")
    
    # Get average score
    avg = CVAnalysis.get_average_score(user.id)
    assert avg == 78.0
    
    print(f"✅ Average ATS Score: {avg}")
    
    return analysis


# ================================================================
# TEST 12: CASCADE DELETE
# ================================================================
def test_cascade_delete(test_db):
    """Test CASCADE DELETE relationships"""
    print("\n" + "="*60)
    print("TEST 12: CASCADE DELETE")
    print("="*60)
    
    # Create full chain
    user = User.create('cascade@example.com', 'Password123!', 'Cascade User')
    company = Company.create(user.id, 'Netflix', 'https://netflix.com')
    contact = Contact.create(company.id, 'Reed Hastings', 'CEO')
    app = Application.create(user.id, company.id, 'DevOps Engineer')
    outreach = Outreach.create(
        user.id, contact.id, 'email', 'Test message',
        date.today().isoformat(), application_id=app.id
    )
    
    print("✅ Created chain:")
    print(f"   User ID: {user.id}")
    print(f"   Company ID: {company.id}")
    print(f"   Contact ID: {contact.id}")
    print(f"   Application ID: {app.id}")
    print(f"   Outreach ID: {outreach.id}")
    
    # Verify all exist
    assert User.find_by_id(user.id) is not None
    assert Company.find_by_id(company.id) is not None
    assert Contact.find_by_id(contact.id) is not None
    assert Application.find_by_id(app.id) is not None
    assert Outreach.find_by_id(outreach.id) is not None
    
    print("✅ All records exist")
    
    # Delete user (should cascade delete everything)
    user.delete()
    
    print("✅ User deleted")
    
    # Verify cascade delete
    assert User.find_by_id(user.id) is None
    assert Company.find_by_id(company.id) is None
    assert Contact.find_by_id(contact.id) is None
    assert Application.find_by_id(app.id) is None
    assert Outreach.find_by_id(outreach.id) is None
    
    print("✅ CASCADE DELETE successful - all related records deleted")


# ================================================================
# MAIN TEST RUNNER
# ================================================================
if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
