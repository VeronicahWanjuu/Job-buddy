"""
Database Schema Tests
Tests database structure, constraints, triggers, and views
"""

import pytest
import sqlite3
from pathlib import Path

@pytest.fixture()
def test_db():
    """Create a fresh test database with schema"""
    # FIXED: Correct path to schema.sql
    schema_path = Path(__file__).parent.parent.parent / 'backend' / 'database' / 'schema.sql'
    
    # Create in-memory database
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    
    # Load and execute schema
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
        conn.executescript(schema_sql)
    
    yield conn
    
    # Cleanup
    conn.close()


def test_database_creation(test_db):
    """Test that all required tables are created"""
    cursor = test_db.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        ORDER BY name
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = [
        'users',
        'onboarding_data',
        'companies',
        'contacts',
        'applications',
        'outreach_activities',
        'goals',
        'streaks',
        'user_quests',
        'notifications',
        'cv_analyses'
    ]
    
    for table in required_tables:
        assert table in tables, f"Table {table} not found in database"


def test_foreign_keys_enabled(test_db):
    """Test that foreign key constraints are enabled"""
    cursor = test_db.cursor()
    cursor.execute("PRAGMA foreign_keys")
    result = cursor.fetchone()
    assert result[0] == 1, "Foreign keys are not enabled"


def test_user_creation(test_db):
    """Test user table and basic insert"""
    cursor = test_db.cursor()
    
    cursor.execute("""
        INSERT INTO users (email, password_hash, name)
        VALUES ('test@example.com', 'hashedpass123', 'Test User')
    """)
    
    cursor.execute("SELECT * FROM users WHERE email = 'test@example.com'")
    user = cursor.fetchone()
    
    assert user is not None
    assert user['email'] == 'test@example.com'
    assert user['name'] == 'Test User'
    assert user['is_active'] == 1


def test_password_validation(test_db):
    """Test that password_hash is required"""
    cursor = test_db.cursor()
    
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO users (email, name)
            VALUES ('test@example.com', 'Test User')
        """)


def test_email_validation(test_db):
    """Test email format constraint"""
    cursor = test_db.cursor()
    
    # Valid email should work
    cursor.execute("""
        INSERT INTO users (email, password_hash, name)
        VALUES ('valid@example.com', 'hash', 'User')
    """)
    
    # Invalid email should fail
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO users (email, password_hash, name)
            VALUES ('invalid-email', 'hash', 'User')
        """)


def test_user_authentication(test_db):
    """Test user table supports authentication flow"""
    cursor = test_db.cursor()
    
    # Create user
    cursor.execute("""
        INSERT INTO users (email, password_hash, name, created_at)
        VALUES ('auth@test.com', 'hashed', 'Auth User', datetime('now'))
    """)
    
    # Verify user can be found
    cursor.execute("""
        SELECT * FROM users 
        WHERE email = 'auth@test.com' AND is_active = 1
    """)
    user = cursor.fetchone()
    
    assert user is not None
    assert user['email'] == 'auth@test.com'


def test_cascade_delete(test_db):
    """Test cascade deletion of related records"""
    cursor = test_db.cursor()
    
    # Create user
    cursor.execute("""
        INSERT INTO users (email, password_hash, name)
        VALUES ('cascade@test.com', 'hash', 'Cascade User')
    """)
    user_id = cursor.lastrowid
    
    # Create company for user
    cursor.execute("""
        INSERT INTO companies (user_id, name)
        VALUES (?, 'Test Company')
    """, (user_id,))
    
    # Create application
    company_id = cursor.lastrowid
    cursor.execute("""
        INSERT INTO applications (user_id, company_id, job_title, status)
        VALUES (?, ?, 'Job Title', 'Planned')
    """, (user_id, company_id))
    
    # Delete user
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    
    # Check that companies and applications are deleted
    cursor.execute("SELECT COUNT(*) FROM companies WHERE user_id = ?", (user_id,))
    assert cursor.fetchone()[0] == 0
    
    cursor.execute("SELECT COUNT(*) FROM applications WHERE user_id = ?", (user_id,))
    assert cursor.fetchone()[0] == 0


def test_unique_constraints(test_db):
    """Test unique constraints"""
    cursor = test_db.cursor()
    
    # Create first user
    cursor.execute("""
        INSERT INTO users (email, password_hash, name)
        VALUES ('unique@test.com', 'hash', 'User One')
    """)
    
    # Try to create duplicate email
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO users (email, password_hash, name)
            VALUES ('unique@test.com', 'hash', 'User Two')
        """)


def test_check_constraints(test_db):
    """Test CHECK constraints"""
    cursor = test_db.cursor()
    
    # Create user
    cursor.execute("""
        INSERT INTO users (email, password_hash, name)
        VALUES ('check@test.com', 'hash', 'Check User')
    """)
    user_id = cursor.lastrowid
    
    # Create company
    cursor.execute("""
        INSERT INTO companies (user_id, name)
        VALUES (?, 'Company')
    """, (user_id,))
    company_id = cursor.lastrowid
    
    # Test invalid status
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO applications (user_id, company_id, job_title, status)
            VALUES (?, ?, 'Job', 'InvalidStatus')
        """, (user_id, company_id))


def test_outreach_exactly_one_constraint(test_db):
    """Test outreach must have exactly one of application_id or company_id"""
    cursor = test_db.cursor()
    
    # Setup
    cursor.execute("""
        INSERT INTO users (email, password_hash, name)
        VALUES ('outreach@test.com', 'hash', 'User')
    """)
    user_id = cursor.lastrowid
    
    cursor.execute("""
        INSERT INTO companies (user_id, name)
        VALUES (?, 'Company')
    """, (user_id,))
    company_id = cursor.lastrowid
    
    cursor.execute("""
        INSERT INTO contacts (company_id, name)
        VALUES (?, 'Contact')
    """, (company_id,))
    contact_id = cursor.lastrowid
    
    cursor.execute("""
        INSERT INTO applications (user_id, company_id, job_title, status)
        VALUES (?, ?, 'Job', 'Planned')
    """, (user_id, company_id))
    app_id = cursor.lastrowid
    
    # Valid: company_id only
    cursor.execute("""
        INSERT INTO outreach_activities 
        (user_id, company_id, contact_id, channel, message_template, sent_date)
        VALUES (?, ?, ?, 'email', 'Message', date('now'))
    """, (user_id, company_id, contact_id))
    
    # Valid: application_id only
    cursor.execute("""
        INSERT INTO outreach_activities 
        (user_id, application_id, contact_id, channel, message_template, sent_date)
        VALUES (?, ?, ?, 'email', 'Message', date('now'))
    """, (user_id, app_id, contact_id))
    
    # Invalid: both
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO outreach_activities 
            (user_id, application_id, company_id, contact_id, channel, message_template, sent_date)
            VALUES (?, ?, ?, ?, 'email', 'Message', date('now'))
        """, (user_id, app_id, company_id, contact_id))


def test_triggers(test_db):
    """Test that triggers exist and fire correctly"""
    cursor = test_db.cursor()
    
    # Create user - should auto-create streak
    cursor.execute("""
        INSERT INTO users (email, password_hash, name)
        VALUES ('trigger@test.com', 'hash', 'Trigger User')
    """)
    user_id = cursor.lastrowid
    
    # Check streak was created
    cursor.execute("SELECT * FROM streaks WHERE user_id = ?", (user_id,))
    streak = cursor.fetchone()
    
    assert streak is not None
    assert streak['current_streak'] == 0
    assert streak['total_points'] == 0


def test_streak_auto_creation(test_db):
    """Test that streak is automatically created on user registration"""
    cursor = test_db.cursor()
    
    cursor.execute("""
        INSERT INTO users (email, password_hash, name)
        VALUES ('streak@test.com', 'hash', 'Streak User')
    """)
    user_id = cursor.lastrowid
    
    cursor.execute("SELECT * FROM streaks WHERE user_id = ?", (user_id,))
    streak = cursor.fetchone()
    
    assert streak is not None
    assert streak['user_id'] == user_id


def test_views(test_db):
    """Test that views are created and work correctly"""
    cursor = test_db.cursor()
    
    # Check views exist
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='view'
    """)
    views = [row[0] for row in cursor.fetchall()]
    
    assert 'v_applications_detailed' in views
    assert 'v_contacts_detailed' in views


def test_contact_null_email_uniqueness(test_db):
    """Test that multiple contacts can have NULL email"""
    cursor = test_db.cursor()
    
    cursor.execute("""
        INSERT INTO users (email, password_hash, name)
        VALUES ('contact@test.com', 'hash', 'User')
    """)
    user_id = cursor.lastrowid
    
    cursor.execute("""
        INSERT INTO companies (user_id, name)
        VALUES (?, 'Company')
    """, (user_id,))
    company_id = cursor.lastrowid
    
    # Insert two contacts with NULL email
    cursor.execute("""
        INSERT INTO contacts (company_id, name, email)
        VALUES (?, 'Contact 1', NULL)
    """, (company_id,))
    
    cursor.execute("""
        INSERT INTO contacts (company_id, name, email)
        VALUES (?, 'Contact 2', NULL)
    """, (company_id,))
    
    # Both should succeed
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE company_id = ?", (company_id,))
    assert cursor.fetchone()[0] == 2


def test_transaction_rollback(test_db):
    """Test transaction rollback works correctly - FIXED"""
    cursor = test_db.cursor()
    
    cursor.execute("""
        INSERT INTO users (email, password_hash, name)
        VALUES ('trans@test.com', 'hash', 'Trans User')
    """)
    user_id = cursor.lastrowid
    
    # Commit the user first
    test_db.commit()
    
    try:
        # Now try to insert companies in a transaction
        cursor.execute("""
            INSERT INTO companies (user_id, name)
            VALUES (?, 'Company 1')
        """, (user_id,))
        
        # This should fail (invalid source)
        cursor.execute("""
            INSERT INTO companies (user_id, name, source)
            VALUES (?, 'Company 2', 'InvalidSource')
        """, (user_id,))
        
        test_db.commit()
    except sqlite3.IntegrityError:
        test_db.rollback()
    
    # Check that no companies were created (rollback should have reverted both inserts)
    cursor.execute("SELECT COUNT(*) FROM companies WHERE user_id = ?", (user_id,))
    assert cursor.fetchone()[0] == 0