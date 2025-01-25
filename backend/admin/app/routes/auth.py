from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..models.user import User
from .. import mongo
from bson import ObjectId

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('categories.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            # Debug print
            print(f"Attempting login for username: {username}")
            
            user_data = mongo.db.users.find_one({'username': username})
            print(f"Found user data: {user_data}")
            
            if user_data:
                # Check if password needs to be rehashed
                if not user_data['password'].startswith('pbkdf2:sha256:'):
                    # Update password hash
                    new_hash = generate_password_hash(password)
                    mongo.db.users.update_one(
                        {'_id': user_data['_id']},
                        {'$set': {'password': new_hash}}
                    )
                    user_data['password'] = new_hash
                
                if check_password_hash(user_data['password'], password):
                    user = User(user_data)
                    login_user(user)
                    return redirect(url_for('categories.index'))
            
            flash('Invalid credentials', 'error')
        except Exception as e:
            print(f"Login error: {str(e)}")
            flash(f'Login error: {str(e)}', 'error')
            
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))