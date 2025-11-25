from flask import Blueprint, request, jsonify
from backend.utils.decorators import require_auth
import json
import os
import random

coaches_bp = Blueprint('coaches', __name__)

# Default fallback image if coach has no image
DEFAULT_IMAGE = "https://placeholder.coach-images.com/default.jpg"


def load_coaches():
    """Load coaches from JSON file."""
    coaches_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'coaches.json')
    with open(coaches_path, 'r') as f:
        return json.load(f)['coaches']


@coaches_bp.route('', methods=['GET'])
@require_auth
def get_coaches():
    """
    GET /api/v1/coaches
    Returns list of ALL coaches.
    """
    try:
        coaches = load_coaches()

        # Add fallback image if missing
        for c in coaches:
            if not c.get("image_url"):
                c["image_url"] = DEFAULT_IMAGE

        return jsonify(coaches), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@coaches_bp.route('/<coach_id>', methods=['GET'])
@require_auth
def get_coach(coach_id):
    """
    GET /api/v1/coaches/<coach_id>
    Returns a single coach’s full profile.
    """
    try:
        coaches = load_coaches()

        coach = next((c for c in coaches if c['id'] == coach_id), None)

        if not coach:
            return jsonify({"error": "Coach not found"}), 404

        # Add fallback for missing image
        if not coach.get("image_url"):
            coach["image_url"] = DEFAULT_IMAGE

        return jsonify(coach), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@coaches_bp.route('/tip-of-the-day', methods=['GET'])
@require_auth
def get_tip_of_the_day():
    """
    GET /api/v1/coaches/tip-of-the-day
    Returns a random TIP based on coach’s specialization.
    """
    try:
        coaches = load_coaches()

        if not coaches:
            return jsonify({"error": "No coaches available"}), 404

        # Pick a random coach
        coach = random.choice(coaches)

        # Add fallback image for tip-of-the-day
        if not coach.get("image_url"):
            coach["image_url"] = DEFAULT_IMAGE

        # Auto-generated specialization-based tips
        specialization_tips = {
            "Tech & Engineering Careers": [
                "Keep your GitHub active with recent projects.",
                "Master data structures—FAANG loves them."
            ],
            "ATS Optimization & Personal Branding": [
                "Use keywords from the job description in your resume.",
                "Strong LinkedIn headlines increase recruiter visibility."
            ],
            "Behavioral & Technical Interviews": [
                "Use the STAR method in your interview answers.",
                "Mock interviews significantly improve performance."
            ],
            "Career Changes & Pivots": [
                "Transferable skills are more powerful than job titles.",
                "Network before applying—referrals always win."
            ],
            "Leadership & C-Suite Positions": [
                "Highlight measurable impact in leadership roles.",
                "Executive presence starts with clarity and confidence."
            ],
            "Professional Networking & LinkedIn": [
                "Send personalized connection requests to boost acceptance.",
                "Engage on LinkedIn 10 minutes daily for visibility."
            ]
        }

        specialization = coach.get("specialization", "")
        tips = specialization_tips.get(specialization, [
            "Stay consistent—opportunities follow persistence.",
            "Small daily progress leads to big career wins."
        ])

        tip = random.choice(tips)

        # Return a clean summary for the tip of the day
        return jsonify({
            "coach": {
                "id": coach["id"],
                "name": coach["name"],
                "title": coach.get("title", ""),
                "specialization": coach.get("specialization", ""),
                "image_url": coach.get("image_url", DEFAULT_IMAGE)
            },
            "tip": tip
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
