"""
Database Tests
Validates schema, constraints, and operations
"""

import pytest
import sqlite3
import os
import sys
from pathlib import Path

# Add backend to path - FIXED
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from database.db import db, DatabaseError
from models.user import User

@pytest.fixture
def test_db():
    """Create test database"""
    test_db_path = 'test_jobbuddy.db'
    
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

def test_database_creation(test_db):
    """Test database and tables are created"""
    tables = test_db.execute_query('''
        SELECT name FROM sqlite_master WHERE type='table' ORDER BY name
    ''')
    
    table_names = [t['name'] for t in tables]
    
    expected_tables = [
        'users', 'onboarding_data', 'companies', 'contacts',
        'applications', 'outreach_activities', 'goals', 'streaks',
        'user_quests', 'notifications', 'cv_analyses'
    ]
    
    for table in expected_tables:
        assert table in table_names, f"Table {table} not found"

def test_foreign_keys_enabled(test_db):
    """Test foreign key enforcement is enabled"""
    result = test_db.execute_one('PRAGMA foreign_keys')
    assert result['foreign_keys'] == 1, "Foreign keys not enabled"

def test_user_creation(test_db):
    """Test user creation with validation"""
    # Valid user
    user = User.create('test@example.com', 'Password123!', 'Test User')
    assert user is not None
    assert user.email == 'test@example.com'
    assert user.name == 'Test User'
    
    # Duplicate email should fail
    with pytest.raises(ValueError, match="already registered"):
        User.create('test@example.com', 'Password456!', 'Another User')

def test_password_validation(test_db):
    """Test password validation rules"""
    # Too short
    with pytest.raises(ValueError, match="at least 8 characters"):
        User.create('test@example.com', 'Pass1!', 'Test')
    
    # No uppercase
    with pytest.raises(ValueError, match="uppercase"):
        User.create('test@example.com', 'password123!', 'Test')
    
    # No lowercase
    with pytest.raises(ValueError, match="lowercase"):
        User.create('test@example.com', 'PASSWORD123!', 'Test')
    
    # No number
    with pytest.raises(ValueError, match="number"):
        User.create('test@example.com', 'Password!', 'Test')
    
    # No special char
    with pytest.raises(ValueError, match="special character"):
        User.create('test@example.com', 'Password123', 'Test')

def test_email_validation(test_db):
    """Test email format validation"""
    # Invalid formats
    with pytest.raises(ValueError, match="Invalid email"):
        User.create('notanemail', 'Password123!', 'Test')
    
    with pytest.raises(ValueError, match="Invalid email"):
        User.create('missing@domain', 'Password123!', 'Test')

def test_user_authentication(test_db):
    """Test user login"""
    # Create user
    User.create('auth@example.com', 'Password123!', 'Auth User')
    
    # Correct credentials
    user = User.authenticate('auth@example.com', 'Password123!')
    assert user is not None
    assert user.email == 'auth@example.com'
    
    # Wrong password
    with pytest.raises(ValueError, match="Invalid email or password"):
        User.authenticate('auth@example.com', 'WrongPassword!')
    
    # Non-existent user
    with pytest.raises(ValueError, match="Invalid email or password"):
        User.authenticate('nonexistent@example.com', 'Password123!')

def test_cascade_delete(test_db):
    """Test CASCADE DELETE on user deletion"""
    # Create user
    user = User.create('cascade@example.com', 'Password123!', 'Cascade Test')
    
    # Create related data
    company_id = test_db.execute_insert('''
        INSERT INTO companies (user_id, name) VALUES (?, ?)
    ''', (user.id, 'Test Company'))
    
    app_id = test_db.execute_insert('''
        INSERT INTO applications (user_id, company_id, job_title, status)
        VALUES (?, ?, ?, ?)
    ''', (user.id, company_id, 'Test Job', 'Planned'))
    
    # Verify data exists
    apps = test_db.execute_query('SELECT * FROM applications WHERE user_id = ?', (user.id,))
    assert len(apps) == 1
    
    # Delete user
    user.delete()
    
    # Verify CASCADE delete worked
    apps_after = test_db.execute_query('SELECT * FROM applications WHERE user_id = ?', (user.id,))
    assert len(apps_after) == 0, "CASCADE DELETE failed"
    
    companies_after = test_db.execute_query('SELECT * FROM companies WHERE user_id = ?', (user.id,))
    assert len(companies_after) == 0, "CASCADE DELETE failed for companies"

def test_unique_constraints(test_db):
    """Test UNIQUE constraints"""
    # Create user
    user = User.create('unique@example.com', 'Password123!', 'Unique Test')
    
    # Create company
    test_db.execute_insert('''
        INSERT INTO companies (user_id, name) VALUES (?, ?)
    ''', (user.id, 'Google'))
    
    # Duplicate company name should fail (case-insensitive)
    with pytest.raises(DatabaseError):
        test_db.execute_insert('''
            INSERT INTO companies (user_id, name) VALUES (?, ?)
        ''', (user.id, 'google'))

def test_check_constraints(test_db):
    """Test CHECK constraints"""
    user = User.create('check@example.com', 'Password123!', 'Check Test')
    company_id = test_db.execute_insert('''
        INSERT INTO companies (user_id, name) VALUES (?, ?)
    ''', (user.id, 'Test Company'))
    
    # Invalid application status
    with pytest.raises(DatabaseError):
        test_db.execute_insert('''
            INSERT INTO applications (user_id, company_id, job_title, status)
            VALUES (?, ?, ?, ?)
        ''', (user.id, company_id, 'Test Job', 'InvalidStatus'))
    
    # Invalid notification type
    with pytest.raises(DatabaseError):
        test_db.execute_insert('''
            INSERT INTO notifications (user_id, type, title, message)
            VALUES (?, ?, ?, ?)
        ''', (user.id, 'invalid_type', 'Test', 'Message'))

def test_outreach_exactly_one_constraint(test_db):
    """Test outreach activities must link to EXACTLY ONE of application/company"""
    user = User.create('outreach@example.com', 'Password123!', 'Outreach Test')
    company_id = test_db.execute_insert('''
        INSERT INTO companies (user_id, name) VALUES (?, ?)
    ''', (user.id, 'Test Company'))
    
    contact_id = test_db.execute_insert('''
        INSERT INTO contacts (company_id, name) VALUES (?, ?)
    ''', (company_id, 'Test Contact'))
    
    app_id = test_db.execute_insert('''
        INSERT INTO applications (user_id, company_id, job_title, status)
        VALUES (?, ?, ?, ?)
    ''', (user.id, company_id, 'Test Job', 'Planned'))
    
    # Both NULL should fail
    with pytest.raises(DatabaseError):
        test_db.execute_insert('''
            INSERT INTO outreach_activities 
            (user_id, application_id, company_id, contact_id, channel, message_template, sent_date)
            VALUES (?, NULL, NULL, ?, ?, ?, ?)
        ''', (user.id, contact_id, 'email', 'Test message', '2025-01-01'))
    
    # Both set should fail
    with pytest.raises(DatabaseError):
        test_db.execute_insert('''
            INSERT INTO outreach_activities 
            (user_id, application_id, company_id, contact_id, channel, message_template, sent_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user.id, app_id, company_id, contact_id, 'email', 'Test message', '2025-01-01'))

def test_triggers(test_db):
    """Test auto-update triggers"""
    user = User.create('trigger@example.com', 'Password123!', 'Trigger Test')
    company_id = test_db.execute_insert('''
        INSERT INTO companies (user_id, name) VALUES (?, ?)
    ''', (user.id, 'Test Company'))
    
    app_id = test_db.execute_insert('''
        INSERT INTO applications (user_id, company_id, job_title, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
    ''', (user.id, company_id, 'Test Job', 'Planned'))
    
    # Get initial timestamp
    app_before = test_db.execute_one('SELECT updated_at FROM applications WHERE id = ?', (app_id,))
    
    import time
    time.sleep(1)  # Wait 1 second
    
    # Update application
    test_db.execute_update('''
        UPDATE applications SET notes = ? WHERE id = ?
    ''', ('Updated notes', app_id))
    
    # Check timestamp updated
    app_after = test_db.execute_one('SELECT updated_at FROM applications WHERE id = ?', (app_id,))
    
    assert app_after['updated_at'] > app_before['updated_at'], "Trigger didn't update timestamp"

def test_streak_auto_creation(test_db):
    """Test streak record auto-created when user is created"""
    user = User.create('streak@example.com', 'Password123!', 'Streak Test')
    
    # Check streak was created
    streak = test_db.execute_one('SELECT * FROM streaks WHERE user_id = ?', (user.id,))
    
    assert streak is not None, "Streak not auto-created"
    assert streak['current_streak'] == 0
    assert streak['longest_streak'] == 0
    assert streak['total_points'] == 0

def test_views(test_db):
    """Test database views work correctly"""
    user = User.create('view@example.com', 'Password123!', 'View Test')
    company_id = test_db.execute_insert('''
        INSERT INTO companies (user_id, name, location) VALUES (?, ?, ?)
    ''', (user.id, 'Google', 'Mountain View'))
    
    app_id = test_db.execute_insert('''
        INSERT INTO applications (user_id, company_id, job_title, status)
        VALUES (?, ?, ?, ?)
    ''', (user.id, company_id, 'Software Engineer', 'Applied'))
    
    # Query view
    results = test_db.execute_query('SELECT * FROM v_applications_detailed WHERE id = ?', (app_id,))
    
    assert len(results) == 1
    assert results[0]['company_name'] == 'Google'
    assert results[0]['company_location'] == 'Mountain View'
    assert results[0]['job_title'] == 'Software Engineer'

def test_contact_null_email_uniqueness(test_db):
    """Test contacts can have multiple NULL emails"""
    user = User.create('contact@example.com', 'Password123!', 'Contact Test')
    company_id = test_db.execute_insert('''
        INSERT INTO companies (user_id, name) VALUES (?, ?)
    ''', (user.id, 'Test Company'))
    
    # Insert first contact with NULL email
    test_db.execute_insert('''
        INSERT INTO contacts (company_id, name, email) VALUES (?, ?, NULL)
    ''', (company_id, 'Contact 1'))
    
    # Insert second contact with NULL email (should succeed)
    test_db.execute_insert('''
        INSERT INTO contacts (company_id, name, email) VALUES (?, ?, NULL)
    ''', (company_id, 'Contact 2'))
    
    # Both should exist
    contacts = test_db.execute_query('''
        SELECT * FROM contacts WHERE company_id = ? AND email IS NULL
    ''', (company_id,))
    
    assert len(contacts) == 2, "Multiple NULL emails not allowed"

def test_transaction_rollback(test_db):
    """Test transaction rollback on error"""
    user = User.create('trans@example.com', 'Password123!', 'Transaction Test')
    
    try:
        with test_db.transaction() as cursor:
            # Insert company
            cursor.execute('''
                INSERT INTO companies (user_id, name) VALUES (?, ?)
            ''', (user.id, 'Transaction Company'))
            
            # This should fail (invalid status)
            cursor.execute('''
                INSERT INTO applications (user_id, company_id, job_title, status)
                VALUES (?, ?, ?, ?)
            ''', (user.id, cursor.lastrowid, 'Test Job', 'InvalidStatus'))
    except:
        pass
    
    # Company should NOT exist (rollback)
    companies = test_db.execute_query('''
        SELECT * FROM companies WHERE user_id = ? AND name = ?
    ''', (user.id, 'Transaction Company'))
    
    assert len(companies) == 0, "Transaction not rolled back"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])