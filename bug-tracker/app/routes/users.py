from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import db, User
from app.utils import admin_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
@login_required
@admin_required
def list_users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=20)
    return render_template('users/list.html', users=users)

@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'tester')
        
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return redirect(url_for('users.create_user'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('users.create_user'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return redirect(url_for('users.create_user'))
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return redirect(url_for('users.create_user'))
        
        user = User(username=username, email=email, role=role, is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash(f'User "{username}" created successfully.', 'success')
        return redirect(url_for('users.list_users'))
    
    return render_template('users/form.html', user=None)

@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role', user.role)
        is_active = request.form.get('is_active') == 'on'
        
        if User.query.filter(User.username == username, User.id != user_id).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('users.edit_user', user_id=user_id))
        
        if User.query.filter(User.email == email, User.id != user_id).first():
            flash('Email already exists.', 'error')
            return redirect(url_for('users.edit_user', user_id=user_id))
        
        user.username = username
        user.email = email
        user.role = role
        user.is_active = is_active
        db.session.commit()
        
        flash('User updated successfully.', 'success')
        return redirect(url_for('users.list_users'))
    
    return render_template('users/form.html', user=user)

@users_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('users.list_users'))
