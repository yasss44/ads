from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import json
from datetime import datetime, date, time
from functools import wraps
import bcrypt
from dotenv import load_dotenv
import logging
import uuid

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'webm'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# MySQL/Aiven specific configuration
if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI']:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': {
            'ssl': {'ssl': True},
            'charset': 'utf8mb4'
        }
    }

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Authentication decorators
def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in to access this page.', 'error')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin():
            flash('You need admin privileges to access this page.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

# API Endpoints for Settings Sections
@app.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    """Get user profile"""
    try:
        user = User.query.get(session['user_id'])
        return jsonify(user.to_dict())
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
        return jsonify({'error': 'Failed to fetch profile'}), 500

@app.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        user = User.query.get(session['user_id'])
        data = request.get_json()
        
        # Validate required fields
        if not data.get('username'):
            return jsonify({'error': 'Username is required'}), 400
        
        # Check if username is already taken (excluding current user)
        existing_user = User.query.filter(User.username == data['username'], User.id != user.id).first()
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 400
        
        # Update allowed fields
        user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'full_name' in data:
            user.full_name = data.get('full_name', '')
        
        db.session.commit()
        log_activity('profile_updated', f"Profile updated for user {user.username}")
        return jsonify({'success': True, 'user': user.to_dict()})
        
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile'}), 500

@app.route('/api/preferences', methods=['PUT'])
@login_required
def update_preferences():
    """Update user preferences"""
    try:
        user = User.query.get(session['user_id'])
        data = request.get_json()
        
        preferences = {
            'language': data.get('language', 'en'),
            'timezone': data.get('timezone', 'UTC'),
            'date_format': data.get('date_format', 'MM/DD/YYYY'),
            'dark_mode': data.get('dark_mode', False),
            'auto_refresh': data.get('auto_refresh', True)
        }
        
        user.preferences = json.dumps(preferences)
        db.session.commit()
        
        log_activity('preferences_updated', f"Preferences updated for user {user.username}")
        return jsonify({'success': True, 'preferences': preferences})
        
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update preferences'}), 500

@app.route('/api/notifications/settings', methods=['PUT'])
@login_required
def update_notification_settings():
    """Update notification settings"""
    try:
        user = User.query.get(session['user_id'])
        data = request.get_json()
        
        settings = {
            'email': data.get('email', True),
            'push': data.get('push', False),
            'system_alerts': data.get('system_alerts', True),
            'marketing': data.get('marketing', False)
        }
        
        user.notification_settings = json.dumps(settings)
        db.session.commit()
        
        log_activity('notification_settings_updated', f"Notification settings updated for user {user.username}")
        return jsonify({'success': True, 'settings': settings})
        
    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update notification settings'}), 500

@app.route('/api/settings/security', methods=['PUT'])
@login_required
def update_security_settings():
    """Update security settings (change password)"""
    try:
        user = User.query.get(session['user_id'])
        data = request.get_json()
        
        # Validate current password
        if not data.get('current_password'):
            return jsonify({'error': 'Current password is required'}), 400
        
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Validate new password
        new_password = data.get('new_password')
        if not new_password or len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        
        if new_password != data.get('confirm_password'):
            return jsonify({'error': 'New passwords do not match'}), 400
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        log_activity('password_changed', f"Password changed for user {user.username}")
        return jsonify({'success': True, 'message': 'Password updated successfully'})
        
    except Exception as e:
        logger.error(f"Error updating security settings: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update security settings'}), 500


@app.route('/api/settings/system', methods=['PUT'])
@login_required
@admin_required
def update_system_settings():
    """Update system settings (admin only)"""
    try:
        data = request.get_json()
        
        # In a real application, you would store these in a SystemSettings table
        # For this demo, we'll just simulate successful update
        settings = {
            'maintenance_mode': data.get('maintenance_mode', False),
            'max_upload_size': data.get('max_upload_size', 10),
            'session_timeout': data.get('session_timeout', 30),
            'backup_frequency': data.get('backup_frequency', 'daily'),
            'log_retention': data.get('log_retention', 90)
        }
        
        # Log the system settings update
        log_activity('system_settings_updated', f"System settings updated by admin")
        
        return jsonify({
            'success': True, 
            'settings': settings,
            'message': 'System settings updated successfully'
        })
        
    except Exception as e:
            logger.error(f"Error updating system settings: {e}")
            return jsonify({'error': 'Failed to update system settings'}), 500

@app.route('/api/notifications/settings', methods=['GET'])
@login_required
def get_notification_settings():
    """Get notification settings"""
    try:
        user = User.query.get(session['user_id'])
        # Mock settings to match JavaScript expectations
        settings = {
            'email': True,
            'push': False,
            'system_alerts': True,
            'marketing': False
        }
        return jsonify(settings)
    except Exception as e:
        logger.error(f"Error fetching notification settings: {e}")
        return jsonify({'error': 'Failed to fetch notification settings'}), 500

@app.route('/api/security/settings', methods=['GET'])
@login_required
def get_security_settings():
    """Get security settings like 2FA & active sessions"""
    try:
        user = User.query.get(session['user_id'])
        # Mock security settings data to match JavaScript expectations
        settings = {
            'two_factor_enabled': False,
            'login_alerts': True,
            'active_sessions': 1
        }
        return jsonify(settings)
    except Exception as e:
        logger.error(f"Error fetching security settings: {e}")
        return jsonify({'error': 'Failed to fetch security settings'}), 500

@app.route('/api/preferences', methods=['GET'])
@login_required
def get_preferences():
    """Get user preferences"""
    try:
        user = User.query.get(session['user_id'])
        # Mock preferences to match JavaScript expectations
        preferences = {
            'language': 'en',
            'timezone': 'UTC',
            'date_format': 'MM/dd/yyyy',
            'dark_mode': False,
            'auto_refresh': True
        }
        return jsonify(preferences)
    except Exception as e:
        logger.error(f"Error fetching preferences: {e}")
        return jsonify({'error': 'Failed to fetch preferences'}), 500

@app.route('/api/system/settings', methods=['GET'])
@login_required
@admin_required
def get_system_settings():
    """Get system settings (admin only)"""
    try:
        # Mock system settings - in a real app, these would be stored in database
        settings = {
            'system_name': 'GeoScope Dashboard',
            'system_email': 'admin@geoscope.com',
            'max_locations': 1000,
            'session_timeout': 30,
            'allow_registration': True,
            'require_email_verification': False,
            'enable_api_access': True,
            'maintenance_mode': False
        }
        return jsonify(settings)
    except Exception as e:
        logger.error(f"Error fetching system settings: {e}")
        return jsonify({'error': 'Failed to fetch system settings'}), 500

# Additional Settings API Endpoints
@app.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        user = User.query.get(session['user_id'])
        data = request.get_json()
        
        # Validate current password
        if not user.check_password(data.get('current_password', '')):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        new_password = data.get('new_password')
        if not new_password or len(new_password) < 8:
            return jsonify({'error': 'New password must be at least 8 characters'}), 400
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        log_activity('password_changed', f"Password changed for user {user.username}")
        return jsonify({'success': True, 'message': 'Password changed successfully'})
        
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to change password'}), 500



@app.route('/api/security/2fa/toggle', methods=['POST'])
@login_required
def toggle_2fa():
    """Toggle 2FA for user"""
    try:
        user = User.query.get(session['user_id'])
        
        # For demo purposes, just toggle the status
        # In a real app, you would handle 2FA setup with QR codes, etc.
        current_status = getattr(user, 'two_factor_enabled', False)
        new_status = not current_status
        
        # Store 2FA status (you might need to add this field to User model)
        # For now, we'll simulate it
        
        log_activity('2fa_toggled', f"2FA {'enabled' if new_status else 'disabled'} for user {user.username}")
        
        return jsonify({
            'success': True,
            'enabled': new_status,
            'qr_code': 'data:image/png;base64,mock_qr_code' if new_status else None,
            'secret': 'MOCK_SECRET_KEY' if new_status else None
        })
        
    except Exception as e:
        logger.error(f"Error toggling 2FA: {e}")
        return jsonify({'error': 'Failed to toggle 2FA'}), 500

@app.route('/api/security/sessions', methods=['GET'])
@login_required
def get_active_sessions():
    """Get active user sessions"""
    try:
        # Mock session data - in a real app, you'd track sessions properly
        sessions = [
            {
                'id': '1',
                'user_agent': request.headers.get('User-Agent', 'Unknown'),
                'ip_address': request.remote_addr or '127.0.0.1',
                'location': 'Unknown location',
                'last_active': datetime.utcnow().isoformat(),
                'is_current': True
            }
        ]
        
        return jsonify(sessions)
        
    except Exception as e:
        logger.error(f"Error fetching active sessions: {e}")
        return jsonify({'error': 'Failed to fetch sessions'}), 500

@app.route('/api/security/sessions/<session_id>', methods=['DELETE'])
@login_required
def terminate_session(session_id):
    """Terminate a user session"""
    try:
        # In a real app, you would terminate the actual session
        # For demo purposes, just return success
        
        log_activity('session_terminated', f"Session {session_id} terminated")
        return jsonify({'success': True, 'message': 'Session terminated'})
        
    except Exception as e:
        logger.error(f"Error terminating session: {e}")
        return jsonify({'error': 'Failed to terminate session'}), 500

@app.route('/api/security/login-history', methods=['GET'])
@login_required
def get_login_history():
    """Get user login history"""
    try:
        # Mock login history - in a real app, you'd track this in database
        history = [
            {
                'timestamp': datetime.utcnow().isoformat(),
                'ip_address': request.remote_addr or '127.0.0.1',
                'location': 'Unknown location',
                'user_agent': request.headers.get('User-Agent', 'Unknown'),
                'success': True
            }
        ]
        
        return jsonify(history)
        
    except Exception as e:
        logger.error(f"Error fetching login history: {e}")
        return jsonify({'error': 'Failed to fetch login history'}), 500

@app.route('/api/account/export', methods=['POST'])
@login_required
def export_account_data():
    """Export user account data"""
    try:
        user = User.query.get(session['user_id'])
        
        # In a real app, you would generate a comprehensive data export
        export_data = {
            'user_profile': user.to_dict(),
            'locations': [loc.to_dict() for loc in Location.query.filter_by(created_by=user.id).all()],
            'campaigns': [camp.to_dict() for camp in Campaign.query.filter_by(created_by=user.id).all()],
            'export_date': datetime.utcnow().isoformat()
        }
        
        log_activity('data_exported', f"Account data exported for user {user.username}")
        
        return jsonify({
            'success': True,
            'message': 'Account data export completed',
            'download_url': '/api/download/export'  # Mock URL
        })
        
    except Exception as e:
        logger.error(f"Error exporting account data: {e}")
        return jsonify({'error': 'Failed to export account data'}), 500

@app.route('/api/account/delete', methods=['DELETE'])
@login_required
def delete_account():
    """Delete user account"""
    try:
        user = User.query.get(session['user_id'])
        data = request.get_json()
        
        # Verify password
        if not user.check_password(data.get('password', '')):
            return jsonify({'error': 'Password verification failed'}), 400
        
        # In a real app, you would:
        # 1. Delete all user data
        # 2. Handle data retention requirements
        # 3. Send confirmation email
        
        log_activity('account_deleted', f"Account deletion initiated for user {user.username}")
        
        # For demo, just deactivate the user
        user.is_active = False
        db.session.commit()
        
        # Clear session
        session.clear()
        
        return jsonify({'success': True, 'message': 'Account deletion initiated'})
        
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete account'}), 500

@app.route('/api/system/backup', methods=['POST'])
@login_required
@admin_required
def backup_database():
    """Create database backup (admin only)"""
    try:
        # In a real app, you would create an actual database backup
        backup_filename = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.sql"
        
        log_activity('database_backup', f"Database backup created: {backup_filename}")
        
        return jsonify({
            'success': True,
            'message': 'Database backup created successfully',
            'filename': backup_filename,
            'download_url': f'/api/download/backup/{backup_filename}'
        })
        
    except Exception as e:
        logger.error(f"Error creating database backup: {e}")
        return jsonify({'error': 'Failed to create database backup'}), 500

@app.route('/api/system/logs', methods=['GET'])
@login_required
@admin_required
def get_system_logs():
    """Get system logs (admin only)"""
    try:
        # Mock log data - in a real app, you'd read from log files
        logs = [
            {
                'timestamp': datetime.utcnow().isoformat(),
                'level': 'INFO',
                'message': 'System started successfully',
                'source': 'system'
            },
            {
                'timestamp': datetime.utcnow().isoformat(),
                'level': 'WARNING',
                'message': 'High memory usage detected',
                'source': 'monitor'
            }
        ]
        
        return jsonify(logs)
        
    except Exception as e:
        logger.error(f"Error fetching system logs: {e}")
        return jsonify({'error': 'Failed to fetch system logs'}), 500

@app.route('/api/system/logs/download', methods=['POST'])
@login_required
@admin_required
def download_system_logs():
    """Download system logs (admin only)"""
    try:
        log_filename = f"system_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.log"
        
        log_activity('logs_downloaded', f"System logs downloaded: {log_filename}")
        
        return jsonify({
            'success': True,
            'message': 'System logs prepared for download',
            'download_url': f'/api/download/logs/{log_filename}'
        })
        
    except Exception as e:
        logger.error(f"Error preparing log download: {e}")
        return jsonify({'error': 'Failed to prepare log download'}), 500

@app.route('/api/system/database/reset', methods=['POST'])
@login_required
@admin_required
def reset_database():
    """Reset database (admin only)"""
    try:
        # In a real app, this would be extremely dangerous!
        # You would want multiple confirmations, backups, etc.
        
        log_activity('database_reset', "Database reset initiated - DANGER!")
        
        # For demo purposes, don't actually reset anything
        return jsonify({
            'success': True,
            'message': 'Database reset initiated (simulated)'
        })
        
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        return jsonify({'error': 'Failed to reset database'}), 500

# User model for authentication
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='viewer', nullable=False)  # admin, client, viewer
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Additional fields for MySQL compatibility
    full_name = db.Column(db.String(200))
    preferences = db.Column(db.Text)  # JSON string for user preferences
    notification_settings = db.Column(db.Text)  # JSON string for notification settings
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            # Additional fields for profile display
            'first_name': '',
            'last_name': '',
            'bio': '',
            'avatar_url': None
        }

# Enhanced models for enterprise features
class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    latitude = db.Column(db.DECIMAL(10, 8))  # More precise for MySQL
    longitude = db.Column(db.DECIMAL(11, 8))  # More precise for MySQL
    address = db.Column(db.String(255))
    status = db.Column(db.String(20), default='active', nullable=False)  # active, inactive, maintenance
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref='created_locations')
    devices = db.relationship('Device', backref='location', cascade='all, delete-orphan')
    
    def to_dict(self):
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'address': self.address,
            'status': self.status,
            'created_by': self.creator.username if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'device_count': len(self.devices)
        }
        
        # Include coordinates if available
        if self.latitude is not None and self.longitude is not None:
            result['latitude'] = self.latitude
            result['longitude'] = self.longitude
            
        return result

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft', nullable=False)  # draft, active, paused, completed
    budget = db.Column(db.DECIMAL(12, 2), default=0.0)  # More precise for currency
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    target_audience = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))  # assigned client
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_campaigns')
    client = db.relationship('User', foreign_keys=[client_id], backref='assigned_campaigns')
    media_files = db.relationship('CampaignMedia', backref='campaign', cascade='all, delete-orphan')
    schedules = db.relationship('CampaignSchedule', backref='campaign', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_by': self.creator.username if self.creator else None,
            'client': self.client.username if self.client else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'media_count': len(self.media_files),
            'schedule_count': len(self.schedules)
        }

class CampaignMedia(db.Model):
    __tablename__ = 'campaign_media'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    file_type = db.Column(db.String(50))  # image, video
    mime_type = db.Column(db.String(100))
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    uploader = db.relationship('User', backref='uploaded_media')
    
    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'mime_type': self.mime_type,
            'uploaded_by': self.uploader.username if self.uploader else None,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }

class CampaignSchedule(db.Model):
    __tablename__ = 'campaign_schedules'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'day_of_week': self.day_of_week,
            'day_name': days[self.day_of_week] if 0 <= self.day_of_week <= 6 else 'Unknown',
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Device(db.Model):
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    device_type = db.Column(db.String(50), nullable=False)  # display, sensor, kiosk, etc.
    serial_number = db.Column(db.String(100), unique=True, index=True)
    status = db.Column(db.String(20), default='offline', nullable=False)  # online, offline, maintenance, error
    last_seen = db.Column(db.DateTime)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id', ondelete='SET NULL'))
    firmware_version = db.Column(db.String(20))
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'device_type': self.device_type,
            'serial_number': self.serial_number,
            'status': self.status,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'location_id': self.location_id,
            'location_name': self.location.name if self.location else None,
            'firmware_version': self.firmware_version,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    action = db.Column(db.String(100), nullable=False, index=True)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='activity_logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.username if self.user else None,
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Helper functions
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    """Determine file type based on extension"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext in {'png', 'jpg', 'jpeg', 'gif'}:
        return 'image'
    elif ext in {'mp4', 'avi', 'mov', 'webm'}:
        return 'video'
    return 'unknown'

def create_user_upload_folder(user_id, upload_date=None):
    """Create folder structure: uploads/user_id/date"""
    if upload_date is None:
        upload_date = datetime.now().strftime('%Y-%m-%d')
    
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id), upload_date)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def log_activity(action, details=None):
    """Log user activity"""
    if 'user_id' in session:
        activity = ActivityLog(
            user_id=session['user_id'],
            action=action,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(activity)
        try:
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
            db.session.rollback()


# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            flash(f'Welcome back, {user.username}!', 'success')
            logger.info(f"User {user.username} logged in successfully")
            log_activity('user_login', f'User logged in from {request.remote_addr}')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            logger.warning(f"Failed login attempt for username: {username}")
    
    # Get demo users for display (without passwords)
    demo_users = User.query.filter(User.username.in_(['admin', 'client1', 'viewer1'])).all()
    demo_accounts = [{'username': user.username, 'role': user.role} for user in demo_users]
    
    return render_template('login.html', demo_accounts=demo_accounts)

@app.route('/demo-login/<username>', methods=['POST'])
def demo_login(username):
    """Demo login endpoint - only works for predefined demo accounts"""
    # Only allow specific demo usernames
    allowed_demo_users = ['admin', 'client1', 'viewer1']
    
    if username not in allowed_demo_users:
        flash('Invalid demo account.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=username, is_active=True).first()
    
    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        
        flash(f'Demo login successful! Welcome, {user.username}!', 'success')
        logger.info(f"Demo login successful for user: {user.username}")
        
        return redirect(url_for('dashboard'))
    else:
        flash('Demo account not found. Please run the demo setup script.', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """User logout"""
    username = session.get('username', 'Unknown')
    log_activity('user_logout', f'User logged out')
    session.clear()
    flash('You have been logged out successfully.', 'info')
    logger.info(f"User {username} logged out")
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        
        # Create new user
        try:
            user = User(
                username=username,
                email=email,
                role='viewer'  # Default role
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! You can now log in.', 'success')
            logger.info(f"New user registered: {username}")
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during registration: {e}")
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard for logged-in users"""
    user = User.query.get(session['user_id'])
    log_activity('dashboard_accessed')
    
    # Get comprehensive stats based on user role
    if user.role == 'admin':
        stats = {
            'total_locations': Location.query.count(),
            'total_users': User.query.count(),
            'total_campaigns': Campaign.query.count(),
            'total_devices': Device.query.count(),
            'active_campaigns': Campaign.query.filter_by(status='active').count(),
            'online_devices': Device.query.filter_by(status='online').count(),
            'offline_devices': Device.query.filter_by(status='offline').count(),
            'recent_activities': ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all(),
            'user_role': user.role,
            'username': user.username
        }
    elif user.role == 'client':
        # Client sees only their assigned campaigns and related data
        user_campaigns = Campaign.query.filter_by(client_id=user.id).all()
        stats = {
            'total_campaigns': len(user_campaigns),
            'active_campaigns': len([c for c in user_campaigns if c.status == 'active']),
            'total_budget': sum([c.budget for c in user_campaigns]),
            'total_locations': Location.query.count(),  # Can view all locations
            'total_devices': Device.query.count(),  # Can view all devices
            'online_devices': Device.query.filter_by(status='online').count(),
            'user_campaigns': user_campaigns,
            'user_role': user.role,
            'username': user.username
        }
    else:  # viewer
        stats = {
            'total_locations': Location.query.count(),
            'total_devices': Device.query.count(),
            'online_devices': Device.query.filter_by(status='online').count(),
            'offline_devices': Device.query.filter_by(status='offline').count(),
            'user_role': user.role,
            'username': user.username
        }
    
    return render_template('dashboard.html', stats=stats, user=user)

# Routes
@app.route('/')
def index():
    """Serve the main dashboard page"""
    # Redirect to login if not authenticated
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # If authenticated, redirect to dashboard
    return redirect(url_for('dashboard'))

@app.route('/api')
def api_info():
    """API information endpoint"""
    return jsonify({
        'message': 'Flask Application (MySQL 8 Version)',
        'status': 'running',
        'version': '1.0.0',
        'database': 'MySQL 8'
    })

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'type': 'MySQL 8'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'disconnected',
            'error': str(e)
        }), 500

@app.route('/api/locations', methods=['GET'])
@login_required
def get_locations():
    """Get all locations (all users can view)"""
    try:
        locations = Location.query.all()
        log_activity('locations_viewed')
        return jsonify([location.to_dict() for location in locations])
    except Exception as e:
        logger.error(f"Error fetching locations: {e}")
        return jsonify({'error': 'Failed to fetch locations'}), 500

@app.route('/api/locations', methods=['POST'])
@login_required
@admin_required
def create_location():
    """Create a new location (admin only)"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400
        
        user = User.query.get(session['user_id'])
        location = Location(
            name=data['name'],
            description=data.get('description'),
            address=data.get('address'),
            status=data.get('status', 'active'),
            created_by=user.id
        )
        
        # Add coordinates if provided
        if 'longitude' in data and 'latitude' in data:
            location.latitude = float(data['latitude'])
            location.longitude = float(data['longitude'])
        
        db.session.add(location)
        db.session.commit()
        
        log_activity('location_created', f'Created location: {location.name}')
        logger.info(f"Created location: {location.name}")
        return jsonify(location.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating location: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create location'}), 500

@app.route('/api/locations/<int:location_id>', methods=['GET'])
@login_required
def get_location(location_id):
    """Get a specific location (all users can view)"""
    try:
        location = Location.query.get_or_404(location_id)
        log_activity('location_viewed', f'Viewed location: {location.name}')
        return jsonify(location.to_dict())
    except Exception as e:
        logger.error(f"Error fetching location {location_id}: {e}")
        return jsonify({'error': 'Location not found'}), 404

@app.route('/api/locations/<int:location_id>', methods=['PUT'])
@login_required
@admin_required
def update_location(location_id):
    """Update a location (admin only)"""
    try:
        location = Location.query.get_or_404(location_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            location.name = data['name']
        if 'description' in data:
            location.description = data['description']
        if 'address' in data:
            location.address = data['address']
        if 'status' in data:
            location.status = data['status']
        if 'latitude' in data and 'longitude' in data:
            location.latitude = float(data['latitude']) if data['latitude'] else None
            location.longitude = float(data['longitude']) if data['longitude'] else None
        
        location.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity('location_updated', f'Updated location: {location.name}')
        logger.info(f"Updated location: {location.name}")
        return jsonify(location.to_dict())
        
    except Exception as e:
        logger.error(f"Error updating location {location_id}: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update location'}), 500

@app.route('/api/locations/<int:location_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_location(location_id):
    """Delete a location (admin only)"""
    try:
        location = Location.query.get_or_404(location_id)
        location_name = location.name
        
        db.session.delete(location)
        db.session.commit()
        
        log_activity('location_deleted', f'Deleted location: {location_name}')
        logger.info(f"Deleted location: {location_name}")
        return jsonify({'message': f'Location "{location_name}" deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting location {location_id}: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete location'}), 500

# Campaign Management APIs
@app.route('/api/campaigns', methods=['GET'])
@login_required
def get_campaigns():
    """Get campaigns (admin sees all, client sees assigned)"""
    try:
        user = User.query.get(session['user_id'])
        if user.role == 'admin':
            campaigns = Campaign.query.all()
        elif user.role == 'client':
            campaigns = Campaign.query.filter_by(client_id=user.id).all()
        else:
            campaigns = Campaign.query.filter_by(status='active').all()  # viewers see active only
        
        log_activity('campaigns_viewed')
        return jsonify([campaign.to_dict() for campaign in campaigns])
    except Exception as e:
        logger.error(f"Error fetching campaigns: {e}")
        return jsonify({'error': 'Failed to fetch campaigns'}), 500

@app.route('/api/campaigns', methods=['POST'])
@login_required
def create_campaign():
    """Create a new campaign (authenticated users)"""
    try:
        # Handle both JSON and form data (for file uploads)
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form.to_dict()
            files = request.files
        else:
            data = request.get_json()
            files = {}
        
        user = User.query.get(session['user_id'])
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Campaign name is required'}), 400
        
        # Automatically set client_id for client users
        client_id = data.get('client_id')
        if user.role == 'client' and not client_id:
            client_id = user.id
            
        campaign = Campaign(
            name=data['name'],
            description=data.get('description'),
            status=data.get('status', 'draft'),
            created_by=user.id,
            client_id=client_id
        )
        
        # Handle dates
        if data.get('start_date'):
            campaign.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        if data.get('end_date'):
            campaign.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        
        db.session.add(campaign)
        db.session.flush()  # Get campaign ID without committing
        
        # Handle schedule data
        schedule_data = data.get('schedules')
        if schedule_data and isinstance(schedule_data, list):
            for schedule_item in schedule_data:
                try:
                    # Parse time strings
                    start_time_obj = datetime.strptime(schedule_item['start_time'], '%H:%M').time()
                    end_time_obj = datetime.strptime(schedule_item['end_time'], '%H:%M').time()
                    
                    # Validate day_of_week
                    day_of_week_int = int(schedule_item['day_of_week'])
                    if not (0 <= day_of_week_int <= 6):
                        logger.warning(f"Invalid day_of_week for schedule item: {schedule_item.get('day_of_week')}. Skipping.")
                        continue # Skip this schedule item if day_of_week is invalid

                    schedule = CampaignSchedule(
                        campaign_id=campaign.id,
                        day_of_week=day_of_week_int,
                        start_time=start_time_obj,
                        end_time=end_time_obj,
                        is_active=schedule_item.get('is_active', True)
                    )
                    db.session.add(schedule)
                except KeyError as ke:
                    logger.error(f"Missing key in schedule data for campaign {campaign.id}: {ke}. Schedule item: {schedule_item}")
                    # Continue to next schedule item
                except ValueError as ve:
                    logger.error(f"Invalid time or day_of_week format for campaign {campaign.id}: {ve}. Schedule item: {schedule_item}")
                    # Continue to next schedule item
                except Exception as se:
                    logger.error(f"Error processing schedule item for campaign {campaign.id}: {se}. Schedule item: {schedule_item}")

        # Handle file uploads
        if files:
            upload_folder = create_user_upload_folder(user.id)
            
            for file_key, file in files.items():
                if file and file.filename and allowed_file(file.filename):
                    # Generate unique filename
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    file_path = os.path.join(upload_folder, unique_filename)
                    
                    # Save file
                    file.save(file_path)
                    
                    # Create media record
                    media = CampaignMedia(
                        campaign_id=campaign.id,
                        filename=unique_filename,
                        original_filename=filename,
                        file_path=file_path,
                        file_size=os.path.getsize(file_path),
                        file_type=get_file_type(filename),
                        mime_type=file.content_type,
                        uploaded_by=user.id
                    )
                    db.session.add(media)
        
        db.session.commit()
        
        log_activity('campaign_created', f"Created campaign: {campaign.name}")
        logger.info(f"Created campaign: {campaign.name}")
        return jsonify(campaign.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create campaign'}), 500

@app.route('/api/campaigns/<int:campaign_id>', methods=['PUT'])
@login_required
def update_campaign(campaign_id):
    """Update a campaign (campaign owner or admin)"""
    try:
        campaign = Campaign.query.get_or_404(campaign_id)
        user = User.query.get(session['user_id'])
        
        # Check if user is admin or campaign owner
        if not user.is_admin() and campaign.created_by != user.id and campaign.client_id != user.id:
            return jsonify({'error': 'Permission denied'}), 403
            
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            campaign.name = data['name']
        if 'description' in data:
            campaign.description = data['description']
        if 'status' in data:
            campaign.status = data['status']
        if 'client_id' in data:
            campaign.client_id = data['client_id']
        
        # Handle dates
        if 'start_date' in data:
            campaign.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')) if data['start_date'] else None
        if 'end_date' in data:
            campaign.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')) if data['end_date'] else None
        
        campaign.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity('campaign_updated', f'Updated campaign: {campaign.name}')
        logger.info(f"Updated campaign: {campaign.name}")
        return jsonify(campaign.to_dict())
        
    except Exception as e:
        logger.error(f"Error updating campaign {campaign_id}: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update campaign'}), 500

@app.route('/api/campaigns/<int:campaign_id>', methods=['DELETE'])
@login_required
def delete_campaign(campaign_id):
    """Delete a campaign (campaign owner or admin)"""
    try:
        campaign = Campaign.query.get_or_404(campaign_id)
        user = User.query.get(session['user_id'])
        
        # Check if user is admin or campaign owner
        if not user.is_admin() and campaign.created_by != user.id and campaign.client_id != user.id:
            return jsonify({'error': 'Permission denied'}), 403
            
        campaign_name = campaign.name
        
        db.session.delete(campaign)
        db.session.commit()
        
        log_activity('campaign_deleted', f'Deleted campaign: {campaign_name}')
        logger.info(f"Deleted campaign: {campaign_name}")
        return jsonify({'message': f'Campaign "{campaign_name}" deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting campaign {campaign_id}: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete campaign'}), 500

# Schedule Management APIs
@app.route('/api/schedule', methods=['GET'])
@login_required
def get_schedules():
    """Get campaign schedules, optionally filtered by date"""
    try:
        user = User.query.get(session['user_id'])
        date_str = request.args.get('date')
        
        query = CampaignSchedule.query

        if date_str:
            try:
                # Parse date string (e.g., 'YYYY-MM-DD')
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                # Filter schedules that are active on the target_date
                # This logic assumes schedules are recurring weekly based on day_of_week
                # and that start_date/end_date on Campaign model define overall campaign validity.
                # For simplicity, we'll just check day_of_week for now.
                query = query.filter(CampaignSchedule.day_of_week == target_date.weekday())
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

        # If user is a client, only show schedules for their campaigns
        if user.role == 'client':
            query = query.join(Campaign).filter(Campaign.client_id == user.id)
        
        schedules = query.all()
        
        # Prepare response, including campaign details
        result = []
        for schedule in schedules:
            schedule_dict = schedule.to_dict()
            if schedule.campaign:
                schedule_dict['campaign_name'] = schedule.campaign.name
                schedule_dict['campaign_name'] = schedule.campaign.name
                schedule_dict['campaign_description'] = schedule.campaign.description
                schedule_dict['campaign_status'] = schedule.campaign.status
                schedule_dict['campaign_start_date'] = schedule.campaign.start_date.isoformat() if schedule.campaign.start_date else None
                schedule_dict['campaign_end_date'] = schedule.campaign.end_date.isoformat() if schedule.campaign.end_date else None
            result.append(schedule_dict)

        log_activity('schedules_viewed', f"Viewed schedules for date: {date_str or 'all'}")
        return jsonify({'schedule': result, 'isAdmin': user.is_admin()})

    except Exception as e:
        logger.error(f"Error fetching schedules: {e}")
        return jsonify({'error': 'Failed to fetch schedules'}), 500

@app.route('/api/schedule', methods=['POST'])
@login_required
def create_schedule():
    """Create a new campaign schedule"""
    try:
        data = request.get_json()
        
        if not data or 'campaign_id' not in data or 'day_of_week' not in data or 'start_time' not in data or 'end_time' not in data:
            return jsonify({'error': 'Campaign ID, day of week, start time and end time are required'}), 400
            
        campaign = Campaign.query.get(data['campaign_id'])
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Parse time strings
        try:
            start_time_obj = datetime.strptime(data['start_time'], '%H:%M').time()
            end_time_obj = datetime.strptime(data['end_time'], '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Invalid time format. Use HH:MM.'}), 400

        # Validate day_of_week
        day_of_week_int = int(data['day_of_week'])
        if not (0 <= day_of_week_int <= 6):
            return jsonify({'error': 'day_of_week must be an integer between 0 (Monday) and 6 (Sunday)'}), 400
            
        schedule = CampaignSchedule(
            campaign_id=data['campaign_id'],
            day_of_week=day_of_week_int,
            start_time=start_time_obj,
            end_time=end_time_obj,
            is_active=data.get('is_active', True)
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        log_activity('schedule_created', f"Created schedule for campaign: {campaign.name}")
        return jsonify(schedule.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating schedule: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create schedule'}), 500

# Device Management APIs
@app.route('/api/devices', methods=['GET'])

@login_required
def get_devices():
    """Get all devices"""
    try:
        devices = Device.query.all()
        log_activity('devices_viewed')
        return jsonify([device.to_dict() for device in devices])
    except Exception as e:
        logger.error(f"Error fetching devices: {e}")
        return jsonify({'error': 'Failed to fetch devices'}), 500

@app.route('/api/devices', methods=['POST'])
@login_required
@admin_required
def create_device():
    """Create a new device (admin only)"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'device_type' not in data:
            return jsonify({'error': 'Device name and type are required'}), 400
        
        device = Device(
            name=data['name'],
            device_type=data['device_type'],
            serial_number=data.get('serial_number'),
            status=data.get('status', 'offline'),
            location_id=data.get('location_id'),
            firmware_version=data.get('firmware_version'),
            ip_address=data.get('ip_address')
        )
        
        db.session.add(device)
        db.session.commit()
        
        log_activity('device_created', f"Created device: {device.name}")
        logger.info(f"Created device: {device.name}")
        return jsonify(device.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating device: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create device'}), 500

@app.route('/api/devices/<int:device_id>/status', methods=['PUT'])
@login_required
@admin_required
def update_device_status(device_id):
    """Update device status (admin only)"""
    try:
        device = Device.query.get_or_404(device_id)
        data = request.get_json()
        
        if 'status' in data:
            old_status = device.status
            device.status = data['status']
            device.last_seen = datetime.utcnow()
            db.session.commit()
            
            log_activity('device_status_updated', f"Device {device.name} status: {old_status} -> {device.status}")
            return jsonify(device.to_dict())
        
        return jsonify({'error': 'Status is required'}), 400
        
    except Exception as e:
        logger.error(f"Error updating device status: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update device status'}), 500

@app.route('/api/devices/<int:device_id>', methods=['PUT'])
@login_required
@admin_required
def update_device(device_id):
    """Update a device (admin only)"""
    try:
        device = Device.query.get_or_404(device_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            device.name = data['name']
        if 'device_type' in data:
            device.device_type = data['device_type']
        if 'serial_number' in data:
            device.serial_number = data['serial_number']
        if 'status' in data:
            device.status = data['status']
        if 'location_id' in data:
            device.location_id = data['location_id']
        if 'firmware_version' in data:
            device.firmware_version = data['firmware_version']
        if 'ip_address' in data:
            device.ip_address = data['ip_address']
        
        device.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity('device_updated', f'Updated device: {device.name}')
        logger.info(f"Updated device: {device.name}")
        return jsonify(device.to_dict())
        
    except Exception as e:
        logger.error(f"Error updating device {device_id}: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update device'}), 500

@app.route('/api/devices/<int:device_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_device(device_id):
    """Delete a device (admin only)"""
    try:
        device = Device.query.get_or_404(device_id)
        device_name = device.name
        
        db.session.delete(device)
        db.session.commit()
        
        log_activity('device_deleted', f'Deleted device: {device_name}')
        logger.info(f"Deleted device: {device_name}")
        return jsonify({'message': f'Device "{device_name}" deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting device {device_id}: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete device'}), 500

# User Management APIs (Admin only)
@app.route('/api/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """Get all users (admin only)"""
    try:
        users = User.query.all()
        log_activity('users_viewed')
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return jsonify({'error': 'Failed to fetch users'}), 500

@app.route('/api/users/<int:user_id>/role', methods=['PUT'])
@login_required
@admin_required
def update_user_role(user_id):
    """Update user role (admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if 'role' in data and data['role'] in ['admin', 'client', 'viewer']:
            old_role = user.role
            user.role = data['role']
            db.session.commit()
            
            log_activity('user_role_updated', f"User {user.username} role: {old_role} -> {user.role}")
            return jsonify({'success': True, 'user': user.to_dict()})
        
        return jsonify({'error': 'Valid role is required'}), 400
        
    except Exception as e:
        logger.error(f"Error updating user role: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update user role'}), 500

@app.route('/api/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status (admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent deactivating the current admin
        if user.id == session['user_id']:
            return jsonify({'error': 'Cannot deactivate your own account'}), 400
        
        user.is_active = not user.is_active
        db.session.commit()
        
        action = 'activated' if user.is_active else 'deactivated'
        log_activity('user_status_updated', f"User {user.username} {action}")
        return jsonify({'success': True, 'user': user.to_dict(), 'action': action})
        
    except Exception as e:
        logger.error(f"Error toggling user status: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update user status'}), 500

# Activity Log API (Admin only)
@app.route('/api/activity', methods=['GET'])
@login_required
@admin_required
def get_activity_logs():
    """Get activity logs (admin only)"""
    try:
        limit = request.args.get('limit', 50, type=int)
        activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
        return jsonify([activity.to_dict() for activity in activities])
    except Exception as e:
        logger.error(f"Error fetching activity logs: {e}")
        return jsonify({'error': 'Failed to fetch activity logs'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# Initialize database
def create_tables():
    """Create database tables"""
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")


if __name__ == '__main__':
    # Create tables when running directly
    create_tables()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
