from flask import Blueprint, request, jsonify
from backend.database.db import db
from backend.utils.decorators import require_auth
from backend.services.streak_service import update_user_streak
from backend.services.notification_service import create_quest_completion_notification
from datetime import date, timedelta
import json
import os
import random

goals_bp = Blueprint('goals', __name__)

def get_streak_level(total_points: int) -> tuple:
    """
    Get streak level and next milestone based on total points
    
    Returns:
        (level_number, level_name, next_milestone)
    """
    if total_points < 100:
        return 1, "Getting Started", 100
    elif total_points < 300:
        return 2, "Momentum Builder", 300
    elif total_points < 600:
        return 3, "Consistent Achiever", 600
    else:
        return 4, "Job Hunt Pro", None


@goals_bp.route('/current', methods=['GET'])
@require_auth
def get_current_goal():
    """
    GET /api/v1/goals/current
    
    Get current week's goal (protected)
    
    Returns:
        {
            "goal": {
                "week_start": "2025-01-20",
                "applications_goal": 5,
                "applications_current": 2,
                "outreach_goal": 3,
                "outreach_current": 1,
                ...
            },
            "applications_percentage": 40.0,
            "outreach_percentage": 33.3,
            "days_remaining": 5
        }
    """
    try:
        # Determine week_start (Monday of current week)
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        # Fetch goal for current week
        goal = db.query_one(
            """
            SELECT *
            FROM goals
            WHERE user_id = ? AND week_start = ?
            """,
            (request.user_id, week_start.isoformat())
        )
        
        # If no goal exists, create one with default values
        if not goal:
            db.execute(
                """
                INSERT INTO goals
                (user_id, week_start, applications_goal, applications_current,
                 outreach_goal, outreach_current, created_at)
                VALUES (?, ?, 5, 0, 3, 0, date('now'))
                """,
                (request.user_id, week_start.isoformat())
            )
            db.commit()
            
            goal = db.query_one(
                "SELECT * FROM goals WHERE user_id = ? AND week_start = ?",
                (request.user_id, week_start.isoformat())
            )
        
        # Calculate percentages
        applications_pct = (goal['applications_current'] / goal['applications_goal'] * 100) \
                          if goal['applications_goal'] > 0 else 0
        outreach_pct = (goal['outreach_current'] / goal['outreach_goal'] * 100) \
                      if goal['outreach_goal'] > 0 else 0
        
        # Calculate days remaining in week (0-6, where 0 = Sunday)
        days_remaining = 6 - today.weekday()
        
        return jsonify({
            "goal": goal,
            "applications_percentage": round(applications_pct, 1),
            "outreach_percentage": round(outreach_pct, 1),
            "days_remaining": days_remaining
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@goals_bp.route('/update', methods=['POST'])
@require_auth
def update_goals():
    """
    POST /api/v1/goals/update
    
    Update weekly goals (protected)
    
    Can only update once per week
    
    Request body:
        {
            "applications_goal": 7,
            "outreach_goal": 5
        }
    
    Returns:
        Updated goal object
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        applications_goal = data.get('applications_goal')
        outreach_goal = data.get('outreach_goal')
        
        if applications_goal is None or outreach_goal is None:
            return jsonify({"error": "applications_goal and outreach_goal are required"}), 400
        
        # Validate goals are positive
        if applications_goal < 1 or outreach_goal < 1:
            return jsonify({"error": "Goals must be positive integers"}), 400
        
        # Get current week
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        # Fetch existing goal
        goal = db.query_one(
            "SELECT * FROM goals WHERE user_id = ? AND week_start = ?",
            (request.user_id, week_start.isoformat())
        )
        
        if not goal:
            return jsonify({"error": "No goal found for current week"}), 404
        
        # Check if already updated this week
        if goal['updated_at']:
            # Parse updated_at date
            updated_date = date.fromisoformat(goal['updated_at'])
            week_start_date = date.fromisoformat(goal['week_start'])
            
            # If updated_at is within the same week, don't allow another update
            if updated_date >= week_start_date:
                return jsonify({
                    "error": "Goals can only be updated once per week"
                }), 400
        
        # Update goals
        db.execute(
            """
            UPDATE goals
            SET applications_goal = ?, outreach_goal = ?, updated_at = date('now')
            WHERE user_id = ? AND week_start = ?
            """,
            (applications_goal, outreach_goal, request.user_id, week_start.isoformat())
        )
        db.commit()
        
        # Fetch updated goal
        updated_goal = db.query_one(
            "SELECT * FROM goals WHERE user_id = ? AND week_start = ?",
            (request.user_id, week_start.isoformat())
        )
        
        return jsonify(updated_goal), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@goals_bp.route('/streak', methods=['GET'])
@require_auth
def get_streak():
    """
    GET /api/v1/goals/streak
    
    Get current streak information (protected)
    
    Returns:
        {
            "current_streak": 5,
            "longest_streak": 12,
            "last_activity_date": "2025-01-15",
            "total_points": 450,
            "level": 3,
            "level_name": "Consistent Achiever",
            "next_milestone": 600
        }
    """
    try:
        # Fetch streak
        streak = db.query_one(
            "SELECT * FROM streaks WHERE user_id = ?",
            (request.user_id,)
        )
        
        if not streak:
            return jsonify({"error": "Streak not found"}), 404
        
        # Calculate level and next milestone
        level_number, level_name, next_milestone = get_streak_level(streak['total_points'])
        
        return jsonify({
            "current_streak": streak['current_streak'],
            "longest_streak": streak['longest_streak'],
            "last_activity_date": streak['last_activity_date'],
            "total_points": streak['total_points'],
            "level": level_number,
            "level_name": level_name,
            "next_milestone": next_milestone
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@goals_bp.route('/micro-quests', methods=['GET'])
@require_auth
def get_micro_quests():
    """
    GET /api/v1/goals/micro-quests
    
    Get available micro-quests (3 random, not completed) (protected)
    
    Returns:
        [
            {
                "id": "mq-1",
                "title": "Update Your LinkedIn Profile",
                "description": "...",
                "category": "profile_optimization",
                "points": 20
            },
            ...
        ]
    """
    try:
        # Load micro-quests from JSON
        quests_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'micro_quests.json')
        with open(quests_path, 'r') as f:
            quests_data = json.load(f)
        
        all_quests = quests_data['quests']
        
        # Fetch completed quest IDs
        completed = db.query(
            "SELECT quest_id FROM user_quests WHERE user_id = ?",
            (request.user_id,)
        )
        completed_ids = {row['quest_id'] for row in completed}
        
        # Filter out completed quests
        available_quests = [q for q in all_quests if q['id'] not in completed_ids]
        
        # Return 3 random quests if available
        if len(available_quests) > 3:
            selected_quests = random.sample(available_quests, 3)
        else:
            selected_quests = available_quests
        
        return jsonify(selected_quests), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@goals_bp.route('/micro-quests/<quest_id>/complete', methods=['POST'])
@require_auth
def complete_micro_quest(quest_id):
    """
    POST /api/v1/goals/micro-quests/<quest_id>/complete
    
    Mark micro-quest as completed (protected)
    
    Returns:
        {
            "message": "Quest completed!",
            "points_earned": 20,
            "new_total_points": 470,
            "quest": {...}
        }
    """
    try:
        # Check if already completed
        existing = db.query_one(
            "SELECT id FROM user_quests WHERE user_id = ? AND quest_id = ?",
            (request.user_id, quest_id)
        )
        
        if existing:
            return jsonify({"error": "Quest already completed"}), 400
        
        # Load quest details
        quests_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'micro_quests.json')
        with open(quests_path, 'r') as f:
            quests_data = json.load(f)
        
        # Find the quest
        quest = None
        for q in quests_data['quests']:
            if q['id'] == quest_id:
                quest = q
                break
        
        if not quest:
            return jsonify({"error": "Quest not found"}), 404
        
        # Insert completion record
        db.execute(
            """
            INSERT INTO user_quests (user_id, quest_id, completed_at)
            VALUES (?, ?, datetime('now'))
            """,
            (request.user_id, quest_id)
        )
        db.commit()
        
        # Update streak with quest points
        quest_points = quest.get('points', 10)
        streak_result = update_user_streak(request.user_id, points=quest_points)
        
        # Create completion notification
        create_quest_completion_notification(
            request.user_id, 
            quest['title'], 
            quest_points
        )
        
        return jsonify({
            "message": "Quest completed!",
            "points_earned": quest_points,
            "new_total_points": streak_result['total_points'],
            "quest": quest
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500