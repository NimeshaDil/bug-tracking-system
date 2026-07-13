from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in first.', 'error')
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'error')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in first.', 'error')
            return redirect(url_for('auth.login'))
        if current_user.role != 'admin':
            flash('Administrator access required.', 'error')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
