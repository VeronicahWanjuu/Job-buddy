from flask import Blueprint, request, jsonify
from backend.utils.decorators import require_auth
import json
import os

resources_bp = Blueprint('resources', __name__)

@resources_bp.route('', methods=['GET'])
@require_auth
def get_resources():
    """
    GET /api/v1/resources
    
    Get all learning resources (protected)
    
    Query params:
        - category: Filter by category (optional)
        - type: Filter by type (optional)
    
    Returns:
        [
            {
                "id": "res-1",
                "title": "Resume Writing Guide",
                "description": "...",
                "category": "resume",
                "type": "article",
                "url": "...",
                "difficulty": "beginner"
            },
            ...
        ]
    """
    try:
        # Load resources from JSON
        resources_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'resources.json')
        with open(resources_path, 'r') as f:
            resources_data = json.load(f)
        
        resources = resources_data['resources']
        
        # Apply filters
        category = request.args.get('category')
        resource_type = request.args.get('type')
        
        if category:
            resources = [r for r in resources if r.get('category') == category]
        
        if resource_type:
            resources = [r for r in resources if r.get('type') == resource_type]
        
        return jsonify(resources), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@resources_bp.route('/categories', methods=['GET'])
@require_auth
def get_resource_categories():
    """
    GET /api/v1/resources/categories
    
    Get all resource categories (protected)
    
    Returns:
        {
            "categories": ["resume", "interview_prep", "networking", ...],
            "types": ["article", "tool", "template", ...]
        }
    """
    try:
        # Load resources
        resources_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'resources.json')
        with open(resources_path, 'r') as f:
            resources_data = json.load(f)
        
        resources = resources_data['resources']
        
        # Extract unique categories and types
        categories = list(set(r.get('category') for r in resources if r.get('category')))
        types = list(set(r.get('type') for r in resources if r.get('type')))
        
        return jsonify({
            "categories": sorted(categories),
            "types": sorted(types)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500