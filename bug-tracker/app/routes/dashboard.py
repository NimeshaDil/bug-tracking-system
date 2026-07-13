from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.models import Bug, User
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@dashboard_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    total_open = Bug.query.filter_by(status='open').count()
    total_in_progress = Bug.query.filter_by(status='in_progress').count()
    total_closed = Bug.query.filter_by(status='closed').count()
    
    status_data = {
        'open': total_open,
        'in_progress': total_in_progress,
        'closed': total_closed
    }
    
    priority_counts = Bug.query.with_entities(Bug.priority, func.count(Bug.id)).group_by(Bug.priority).all()
    priority_data = {priority: count for priority, count in priority_counts}
    
    assignee_counts = Bug.query.filter(Bug.assignee_id != None).with_entities(
        User.username, func.count(Bug.id)
    ).join(User, Bug.assignee_id == User.id).group_by(User.username).all()
    assignee_data = {username: count for username, count in assignee_counts}
    
    recent_bugs = Bug.query.order_by(Bug.created_at.desc()).limit(5).all()
    recent_data = [{
        'id': bug.id,
        'title': bug.title,
        'status': bug.status,
        'priority': bug.priority,
        'created_at': bug.created_at.strftime('%Y-%m-%d %H:%M')
    } for bug in recent_bugs]
    
    return jsonify({
        'status': status_data,
        'priority': priority_data,
        'assignee': assignee_data,
        'recent': recent_data,
        'total_open': total_open,
        'total_closed': total_closed
    })
