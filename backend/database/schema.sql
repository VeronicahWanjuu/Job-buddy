-- ================================================================
-- JOBBUDDY DATABASE SCHEMA 

-- Database: SQLite

-- ================================================================

PRAGMA foreign_keys = ON;

-- ================================================================
-- TABLE 1: USERS
-- ================================================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    email_notifications_enabled BOOLEAN DEFAULT TRUE,
    notification_preferences TEXT NULL,
    CONSTRAINT chk_email CHECK (email LIKE '%@%')
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- ================================================================
-- TABLE 2: ONBOARDING_DATA
-- ================================================================
CREATE TABLE IF NOT EXISTS onboarding_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    current_feeling VARCHAR(100) NOT NULL,
    dream_milestone TEXT NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_feeling CHECK (
        current_feeling IN (
            'Excited and ready',
            'Overwhelmed but motivated',
            'Frustrated and stuck',
            'Just getting started'
        )
    )
);

CREATE INDEX IF NOT EXISTS idx_onboarding_user ON onboarding_data(user_id);

-- ================================================================
-- TABLE 3: COMPANIES
-- ================================================================
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    website VARCHAR(500) NULL,
    location VARCHAR(255) NULL,
    industry VARCHAR(100) NULL,
    notes TEXT NULL,
    source VARCHAR(50) DEFAULT 'Manual',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_source CHECK (source IN ('Manual', 'CSV', 'API')),
    UNIQUE(user_id, name COLLATE NOCASE)
);

CREATE INDEX IF NOT EXISTS idx_companies_user ON companies(user_id);
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry);

-- ================================================================
-- TABLE 4: CONTACTS
-- ================================================================
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(255) NULL,
    email VARCHAR(255) NULL,
    linkedin_url VARCHAR(500) NULL,
    notes TEXT NULL,
    source VARCHAR(50) DEFAULT 'Manual',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    CONSTRAINT chk_contact_source CHECK (source IN ('Manual', 'API'))
);

-- Partial unique index: only enforce uniqueness when email is NOT NULL
CREATE UNIQUE INDEX IF NOT EXISTS idx_contacts_company_email 
ON contacts(company_id, email COLLATE NOCASE) 
WHERE email IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company_id);
CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(name);

-- ================================================================
-- TABLE 5: APPLICATIONS
-- ================================================================
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    job_url VARCHAR(500) NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Planned',
    applied_date DATE NULL,
    notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    CONSTRAINT chk_status CHECK (
        status IN ('Planned', 'Applied', 'Interview', 'Offer', 'Rejected')
    ),
    CONSTRAINT chk_applied_date CHECK (
        (status = 'Applied' AND applied_date IS NOT NULL) OR
        (status != 'Applied')
    )
);

CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_company ON applications(company_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_applied_date ON applications(applied_date);

-- ================================================================
-- TABLE 6: OUTREACH_ACTIVITIES
-- ================================================================
CREATE TABLE IF NOT EXISTS outreach_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    application_id INTEGER NULL,
    company_id INTEGER NULL,
    contact_id INTEGER NOT NULL,
    channel VARCHAR(50) NOT NULL,
    message_template TEXT NOT NULL,
    sent_date DATE NOT NULL,
    follow_up_date DATE NULL,
    status VARCHAR(50) DEFAULT 'Sent',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    CONSTRAINT chk_exactly_one_link CHECK (
        (application_id IS NOT NULL AND company_id IS NULL) OR 
        (application_id IS NULL AND company_id IS NOT NULL)
    ),
    CONSTRAINT chk_channel CHECK (channel IN ('email', 'linkedin')),
    CONSTRAINT chk_outreach_status CHECK (status IN ('Sent', 'Responded', 'No Response'))
);

CREATE INDEX IF NOT EXISTS idx_outreach_user ON outreach_activities(user_id);
CREATE INDEX IF NOT EXISTS idx_outreach_application ON outreach_activities(application_id);
CREATE INDEX IF NOT EXISTS idx_outreach_company ON outreach_activities(company_id);
CREATE INDEX IF NOT EXISTS idx_outreach_contact ON outreach_activities(contact_id);
CREATE INDEX IF NOT EXISTS idx_outreach_follow_up ON outreach_activities(follow_up_date);

-- ================================================================
-- TABLE 7: GOALS
-- ================================================================
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    week_start DATE NOT NULL,
    applications_goal INTEGER NOT NULL DEFAULT 5,
    applications_current INTEGER DEFAULT 0,
    outreach_goal INTEGER NOT NULL DEFAULT 3,
    outreach_current INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, week_start),
    CONSTRAINT chk_goals_positive CHECK (
        applications_goal > 0 AND outreach_goal > 0
    ),
    CONSTRAINT chk_current_not_negative CHECK (
        applications_current >= 0 AND outreach_current >= 0
    )
);

CREATE INDEX IF NOT EXISTS idx_goals_user ON goals(user_id);
CREATE INDEX IF NOT EXISTS idx_goals_week_start ON goals(week_start);

-- ================================================================
-- TABLE 8: STREAKS
-- ================================================================
CREATE TABLE IF NOT EXISTS streaks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE NULL,
    total_points INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_streak_positive CHECK (
        current_streak >= 0 AND longest_streak >= 0 AND total_points >= 0
    )
);

CREATE INDEX IF NOT EXISTS idx_streaks_user ON streaks(user_id);

-- ================================================================
-- TABLE 9: USER_QUESTS
-- ================================================================
CREATE TABLE IF NOT EXISTS user_quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    quest_id VARCHAR(20) NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, quest_id)
);

CREATE INDEX IF NOT EXISTS idx_user_quests_user ON user_quests(user_id);
CREATE INDEX IF NOT EXISTS idx_user_quests_quest ON user_quests(quest_id);

-- ================================================================
-- TABLE 10: NOTIFICATIONS
-- ================================================================
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    related_type VARCHAR(50) NULL,
    related_id INTEGER NULL,
    is_read BOOLEAN DEFAULT FALSE,
    emailed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_notification_type CHECK (
        type IN ('follow_up', 'goal_reminder', 'micro_quest', 'motivation', 'system')
    ),
    CONSTRAINT chk_related_type CHECK (
        related_type IS NULL OR 
        related_type IN ('application', 'outreach', 'micro_quest', 'goal')
    )
);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_emailed ON notifications(emailed);

-- ================================================================
-- TABLE 11: CV_ANALYSES
-- ================================================================
CREATE TABLE IF NOT EXISTS cv_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    application_id INTEGER NULL,
    cv_filename VARCHAR(255) NOT NULL,
    cv_file_path VARCHAR(500) NULL,
    job_description TEXT NOT NULL,
    ats_score INTEGER NOT NULL,
    matched_keywords TEXT NOT NULL,
    missing_keywords TEXT NOT NULL,
    suggestions TEXT NOT NULL,
    api_used VARCHAR(50) DEFAULT 'internal',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE SET NULL,
    CONSTRAINT chk_ats_score CHECK (ats_score >= 0 AND ats_score <= 100)
);

CREATE INDEX IF NOT EXISTS idx_cv_analyses_user ON cv_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_cv_analyses_application ON cv_analyses(application_id);
CREATE INDEX IF NOT EXISTS idx_cv_analyses_score ON cv_analyses(ats_score);

-- ================================================================
-- TRIGGERS FOR AUTO-UPDATE TIMESTAMPS
-- ================================================================

CREATE TRIGGER IF NOT EXISTS update_applications_timestamp 
AFTER UPDATE ON applications
FOR EACH ROW
BEGIN
    UPDATE applications SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_goals_timestamp 
AFTER UPDATE ON goals
FOR EACH ROW
BEGIN
    UPDATE goals SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ================================================================
-- TRIGGER: Auto-create streak record when user is created
-- ================================================================

CREATE TRIGGER IF NOT EXISTS create_user_streak
AFTER INSERT ON users
FOR EACH ROW
BEGIN
    INSERT INTO streaks (user_id, current_streak, longest_streak, total_points)
    VALUES (NEW.id, 0, 0, 0);
END;

-- ================================================================
-- VIEWS FOR COMMON QUERIES
-- ================================================================

-- View: Application with company details
CREATE VIEW IF NOT EXISTS v_applications_detailed AS
SELECT 
    a.id,
    a.user_id,
    a.job_title,
    a.status,
    a.applied_date,
    a.created_at,
    c.name as company_name,
    c.website as company_website,
    c.location as company_location,
    c.industry as company_industry
FROM applications a
JOIN companies c ON a.company_id = c.id;

-- View: Contacts with company details
CREATE VIEW IF NOT EXISTS v_contacts_detailed AS
SELECT 
    ct.id,
    ct.name as contact_name,
    ct.role,
    ct.email,
    ct.linkedin_url,
    c.id as company_id,
    c.name as company_name,
    c.user_id
FROM contacts ct
JOIN companies c ON ct.company_id = c.id;

-- ================================================================
-- SCHEMA VALIDATION QUERIES
-- ================================================================

-- Check table count (should be 11)
-- SELECT COUNT(*) as table_count FROM sqlite_master WHERE type='table';

-- Check foreign key enforcement
-- PRAGMA foreign_keys;

-- Verify all indexes exist
-- SELECT name FROM sqlite_master WHERE type='index' ORDER BY name;