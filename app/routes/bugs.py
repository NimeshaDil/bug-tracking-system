from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, Bug, Comment, Attachment, User
from app.utils import role_required, allowed_file
from datetime import datetime
from werkzeug.utils import secure_filename
import os

bugs_bp = Blueprint('bugs', __name__)

@bugs_bp.route('/', methods=['GET'])
@login_required
def list_bugs():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    status = request.args.get('status', '', type=str)
    assignee_id = request.args.get('assignee_id', '', type=str)
    priority = request.args.get('priority', '', type=str)
    sort_by = request.args.get('sort', 'created_at', type=str)
    sort_order = request.args.get('order', 'desc', type=str)
    
    query = Bug.query
    
    if search:
        query = query.filter(db.or_(Bug.title.ilike(f'%{search}%'), Bug.description.ilike(f'%{search}%')))
    
    if status:
        query = query.filter_by(status=status)
    
    if assignee_id:
        query = query.filter_by(assignee_id=int(assignee_id))
    
    if priority:
        query = query.filter_by(priority=priority)
    
    if sort_by == 'priority':
        priority_order = {'critical': 1, 'high': 2, 'medium': 3, 'low': 4}
        query = query.order_by(db.case(priority_order, value=Bug.priority))
    elif sort_by == 'status':
        query = query.order_by(Bug.status)
    else:
        order_col = Bug.created_at if sort_by == 'created_at' else Bug.updated_at
        query = query.order_by(order_col.desc() if sort_order == 'desc' else order_col.asc())
    
    bugs = query.paginate(page=page, per_page=20)
    users = User.query.all()
    
    return render_template('bugs/list.html', bugs=bugs, search=search, status=status, assignee_id=assignee_id, priority=priority, users=users)

@bugs_bp.route('/<int:bug_id>', methods=['GET'])
@login_required
def detail_bug(bug_id):
    bug = Bug.query.get_or_404(bug_id)
    comments = Comment.query.filter_by(bug_id=bug_id).all()
    attachments = Attachment.query.filter_by(bug_id=bug_id).all()
    users = User.query.all()
    
    return render_template('bugs/detail.html', bug=bug, comments=comments, attachments=attachments, users=users)

@bugs_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('developer', 'tester', 'admin')
def create_bug():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')
        
        if not title:
            flash('Title is required.', 'error')
            return redirect(url_for('bugs.create_bug'))
        
        bug = Bug(title=title, description=description, priority=priority, reporter_id=current_user.id, status='open')
        db.session.add(bug)
        db.session.commit()
        
        flash(f'Bug "{title}" created successfully.', 'success')
        return redirect(url_for('bugs.detail_bug', bug_id=bug.id))
    
    return render_template('bugs/form.html', bug=None)

@bugs_bp.route('/<int:bug_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_bug(bug_id):
    bug = Bug.query.get_or_404(bug_id)
    
    if bug.reporter_id != current_user.id and current_user.role != 'admin':
        flash('You can only edit bugs you reported.', 'error')
        return redirect(url_for('bugs.detail_bug', bug_id=bug_id))
    
    if request.method == 'POST':
        bug.title = request.form.get('title', '').strip()
        bug.description = request.form.get('description', '').strip()
        bug.priority = request.form.get('priority', bug.priority)
        bug.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Bug updated successfully.', 'success')
        return redirect(url_for('bugs.detail_bug', bug_id=bug_id))
    
    return render_template('bugs/form.html', bug=bug)

@bugs_bp.route('/<int:bug_id>/delete', methods=['POST'])
@login_required
def delete_bug(bug_id):
    bug = Bug.query.get_or_404(bug_id)
    
    if bug.reporter_id != current_user.id and current_user.role != 'admin':
        flash('You can only delete bugs you reported.', 'error')
        return redirect(url_for('bugs.list_bugs'))
    
    db.session.delete(bug)
    db.session.commit()
    flash('Bug deleted successfully.', 'success')
    return redirect(url_for('bugs.list_bugs'))

@bugs_bp.route('/<int:bug_id>/assign', methods=['POST'])
@login_required
@role_required('developer', 'admin')
def assign_bug(bug_id):
    bug = Bug.query.get_or_404(bug_id)
    assignee_id = request.form.get('assignee_id')
    
    if assignee_id:
        bug.assignee_id = int(assignee_id)
    else:
        bug.assignee_id = None
    
    bug.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('Bug assigned successfully.', 'success')
    return redirect(url_for('bugs.detail_bug', bug_id=bug_id))

@bugs_bp.route('/<int:bug_id>/status', methods=['POST'])
@login_required
@role_required('developer', 'admin')
def change_status(bug_id):
    bug = Bug.query.get_or_404(bug_id)
    new_status = request.form.get('status')
    
    if new_status in ['open', 'in_progress', 'closed']:
        bug.status = new_status
        if new_status == 'closed':
            bug.closed_at = datetime.utcnow()
        else:
            bug.closed_at = None
        bug.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'Status changed to {new_status}.', 'success')
    else:
        flash('Invalid status.', 'error')
    
    return redirect(url_for('bugs.detail_bug', bug_id=bug_id))

@bugs_bp.route('/<int:bug_id>/comment', methods=['POST'])
@login_required
def add_comment(bug_id):
    bug = Bug.query.get_or_404(bug_id)
    body = request.form.get('body', '').strip()
    
    if not body:
        flash('Comment cannot be empty.', 'error')
        return redirect(url_for('bugs.detail_bug', bug_id=bug_id))
    
    comment = Comment(bug_id=bug_id, user_id=current_user.id, body=body)
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added successfully.', 'success')
    return redirect(url_for('bugs.detail_bug', bug_id=bug_id))

@bugs_bp.route('/<int:bug_id>/upload', methods=['POST'])
@login_required
def upload_attachment(bug_id):
    bug = Bug.query.get_or_404(bug_id)
    
    if 'file' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('bugs.detail_bug', bug_id=bug_id))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('bugs.detail_bug', bug_id=bug_id))
    
    if not allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif', 'txt', 'log', 'pdf', 'docx'}):
        flash('File type not allowed.', 'error')
        return redirect(url_for('bugs.detail_bug', bug_id=bug_id))
    
    if file.content_length > 25 * 1024 * 1024:
        flash('File size exceeds 25MB limit.', 'error')
        return redirect(url_for('bugs.detail_bug', bug_id=bug_id))
    
    filename = secure_filename(file.filename)
    stored_filename = f"{bug_id}_{datetime.utcnow().timestamp()}_{filename}"
    upload_folder = 'app/uploads'
    
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    file.save(os.path.join(upload_folder, stored_filename))
    
    attachment = Attachment(
        bug_id=bug_id,
        filename=filename,
        stored_filename=stored_filename,
        file_type=file.filename.rsplit('.', 1)[1].lower(),
        file_size=file.content_length,
        uploaded_by=current_user.id
    )
    db.session.add(attachment)
    db.session.commit()
    
    flash('File uploaded successfully.', 'success')
    return redirect(url_for('bugs.detail_bug', bug_id=bug_id))

@bugs_bp.route('/attachment/<int:attachment_id>/delete', methods=['POST'])
@login_required
def delete_attachment(attachment_id):
    attachment = Attachment.query.get_or_404(attachment_id)
    bug_id = attachment.bug_id
    
    if attachment.uploaded_by != current_user.id and current_user.role != 'admin':
        flash('You can only delete your own attachments.', 'error')
        return redirect(url_for('bugs.detail_bug', bug_id=bug_id))
    
    try:
        filepath = os.path.join('app/uploads', attachment.stored_filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        flash(f'Error deleting file: {str(e)}', 'error')
    
    db.session.delete(attachment)
    db.session.commit()
    
    flash('Attachment deleted successfully.', 'success')
    return redirect(url_for('bugs.detail_bug', bug_id=bug_id))
