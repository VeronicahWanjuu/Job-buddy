"""
One-time script to create minimal Blueprint stubs
for all JobBuddy route files.

Run from project root with:
    python backend/generate_route_stubs.py
"""

import os

BASE_DIR = os.path.dirname(__file__)
ROUTES_DIR = os.path.join(BASE_DIR, "routes")

FILES = {
    "auth.py": """from flask import Blueprint

# Blueprint for authentication routes
auth_bp = Blueprint("auth", __name__)

# FR-1: Authentication routes (register, login, profile)
# will be implemented in Block 2.
""",
    "onboarding.py": """from flask import Blueprint

onboarding_bp = Blueprint("onboarding", __name__)

# FR-2: Onboarding routes
# will be implemented in Block 3.
""",
    "applications.py": """from flask import Blueprint

applications_bp = Blueprint("applications", __name__)

# FR-3: Applications CRUD routes
# will be implemented in Block 4.
""",
    "companies.py": """from flask import Blueprint

companies_bp = Blueprint("companies", __name__)

# FR-4: Companies routes
# will be implemented in Block 5.
""",
    "contacts.py": """from flask import Blueprint

contacts_bp = Blueprint("contacts", __name__)

# FR-4: Contacts routes
# will be implemented in Block 5.
""",
    "outreach.py": """from flask import Blueprint

outreach_bp = Blueprint("outreach", __name__)

# FR-4: Outreach routes
# will be implemented in Block 6.
""",
    "goals.py": """from flask import Blueprint

goals_bp = Blueprint("goals", __name__)

# FR-5: Goals, streaks, and micro-quests routes
# will be implemented in Block 7.
""",
    "cv_matcher.py": """from flask import Blueprint

# IMPORTANT: app.py imports `cv_bp` from here
cv_bp = Blueprint("cv", __name__)

# FR-6: CV matcher routes
# will be implemented in Block 8.
""",
    "resources.py": """from flask import Blueprint

resources_bp = Blueprint("resources", __name__)

# FR-7: Resources routes
# will be implemented in Block 9.
""",
    "coaches.py": """from flask import Blueprint

coaches_bp = Blueprint("coaches", __name__)

# FR-8: Coaches routes
# will be implemented in Block 9.
""",
    "notifications.py": """from flask import Blueprint

notifications_bp = Blueprint("notifications", __name__)

# FR-9: Notifications routes
# will be implemented in Block 10.
""",
    "__init__.py": """# Package for JobBuddy API route blueprints
""",
}


def main():
    os.makedirs(ROUTES_DIR, exist_ok=True)

    for filename, content in FILES.items():
        path = os.path.join(ROUTES_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f" Wrote stub for {filename}")

    print("\n All route stubs generated successfully.")


if __name__ == "__main__":
    main()
