import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import threading
import time

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database (SQLite for simplicity)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///x_replies.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database with app
db.init_app(app)

# Import automation modules
from x_automation import XAutomation
from screen_manager import ScreenManager
from ai_generator import AIGenerator
from config import Config

# Import models
from models import Comment, Session

# Initialize automation components
config = Config()
screen_manager = ScreenManager()
x_automation = XAutomation(config)
ai_generator = AIGenerator(config)

# Global state variables
active_session = None
automation_thread = None
is_running = False

def automation_job():
    """Background thread function to run the automation process"""
    global is_running, active_session
    
    # Initialize comments_processed for all code paths
    comments_processed = 0
    
    try:
        logger.info("Starting automation job")
        # Step 1: Setup screens
        screen_manager.setup_dual_screen()
        
        # Step 2: Open X on primary screen
        x_automation.open_browser()
        screen_manager.position_window("x", 0)  # Position on first screen
        
        # Step 3: Login to X if needed
        if not x_automation.is_logged_in():
            # Always attempt login for our mock version
            login_success = x_automation.login()
            if not login_success:
                logger.error("Failed to login to X. Please check your credentials.")
                raise Exception("X login failed")
        
        # Step 4: Open AI assistant on secondary screen
        ai_generator.open_browser()
        screen_manager.position_window("ai", 1)  # Position on second screen
        
        # Step 5: Navigate to target X feed
        feed_success = x_automation.navigate_to_feed()
        if not feed_success:
            logger.error("Failed to navigate to X feed")
            raise Exception("X feed navigation failed")
        
        # Step 6: Process comments
        comments_to_process = config.comments_per_session
        
        while comments_processed < comments_to_process and is_running:
            # Find comments to reply to
            comment_elements = x_automation.find_comments_to_reply()
            
            if not comment_elements:
                logger.info("No comments found to reply to. Waiting...")
                time.sleep(5)
                continue
            
            for comment in comment_elements:
                if not is_running or comments_processed >= comments_to_process:
                    break
                
                try:
                    # Extract comment text and metadata
                    comment_data = x_automation.extract_comment_data(comment)
                    
                    # Generate AI reply
                    prompt = f"Generate a savage/meme-style reply to this X comment: '{comment_data['text']}'"
                    reply_text = ai_generator.generate_reply(prompt)
                    
                    # Post the reply
                    x_automation.post_reply(comment, reply_text)
                    
                    # Store the session_id in a local variable to avoid detached instance issues
                    session_id = None
                    if active_session and hasattr(active_session, 'id'):
                        session_id = active_session.id
                        
                    # Record in database if we have a valid session_id
                    if session_id:
                        with app.app_context():
                            try:
                                # Create a new Comment object directly using constructor params
                                new_comment = Comment()
                                new_comment.original_text = comment_data['text']
                                new_comment.author = comment_data['author']
                                new_comment.reply_text = reply_text
                                new_comment.session_id = session_id
                                
                                # Add and commit in a fresh session
                                db.session.add(new_comment)
                                db.session.commit()
                                
                                # Update the session as well
                                session_obj = Session.query.get(session_id)
                                if session_obj:
                                    session_obj.comments_processed = comments_processed + 1
                                    db.session.commit()
                            except Exception as e:
                                logger.error(f"Database error adding comment: {str(e)}")
                                db.session.rollback()
                    else:
                        logger.error("Cannot add comment: no active session ID")
                    
                    comments_processed += 1
                    logger.info(f"Processed comment {comments_processed}/{comments_to_process}")
                    
                    # Small delay between comments to appear natural
                    time.sleep(config.delay_between_comments)
                    
                except Exception as e:
                    logger.error(f"Error processing comment: {str(e)}")
                    continue
        
        logger.info(f"Completed processing {comments_processed} comments")
        
    except Exception as e:
        logger.error(f"Automation job failed: {str(e)}")
    
    finally:
        # Clean up
        x_automation.close_browser()
        ai_generator.close_browser()
        is_running = False
        
        # Store the session_id for final update
        session_id = None
        if active_session and hasattr(active_session, 'id'):
            session_id = active_session.id
            
        # Update session in database if we have a valid session_id
        if session_id:
            with app.app_context():
                try:
                    # Get a fresh session object
                    active_session_from_db = Session.query.get(session_id)
                    if active_session_from_db:
                        active_session_from_db.is_completed = True
                        active_session_from_db.comments_processed = comments_processed
                        db.session.commit()
                        logger.info(f"Successfully marked session {session_id} as completed")
                    else:
                        logger.error(f"Could not find session {session_id} in database")
                except Exception as e:
                    logger.error(f"Error updating session status: {str(e)}")
                    db.session.rollback()

@app.route('/')
def index():
    """Main dashboard page"""
    # Get recent sessions
    recent_sessions = Session.query.order_by(Session.created_at.desc()).limit(5).all()
    
    # If active_session exists, refresh it from the database to avoid detached instance error
    active_session_data = None
    if is_running and active_session and hasattr(active_session, 'id'):
        # Try to get the session from the database
        try:
            active_session_data = Session.query.get(active_session.id)
        except Exception as e:
            logger.error(f"Error retrieving active session: {str(e)}")
    
    return render_template('index.html', 
                          is_running=is_running,
                          active_session=active_session_data,
                          recent_sessions=recent_sessions,
                          config=config)

@app.route('/start', methods=['POST'])
def start_automation():
    """Start the automation process"""
    global automation_thread, is_running, active_session
    
    if is_running:
        flash('Automation is already running!', 'warning')
        return redirect(url_for('index'))
    
    try:
        # Create new session
        with app.app_context():
            new_session = Session()
            new_session.comments_target = config.comments_per_session
            new_session.is_completed = False
            new_session.comments_processed = 0
            db.session.add(new_session)
            db.session.commit()
            
            # Store session ID
            session_id = new_session.id
            logger.info(f"Created new session with ID: {session_id}")
            
            # Create a new session object with just the ID to avoid detached instance issues
            class SessionInfo:
                pass
            
            session_info = SessionInfo()
            session_info.id = session_id
            active_session = session_info
        
        # Start automation thread
        is_running = True
        automation_thread = threading.Thread(target=automation_job)
        automation_thread.daemon = True
        automation_thread.start()
        
        flash('Automation started successfully!', 'success')
    except Exception as e:
        logger.error(f"Error starting automation: {str(e)}")
        flash(f'Failed to start automation: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop_automation():
    """Stop the automation process"""
    global is_running
    
    if not is_running:
        flash('Automation is not running!', 'warning')
        return redirect(url_for('index'))
    
    is_running = False
    flash('Stopping automation... This may take a moment.', 'info')
    return redirect(url_for('index'))

@app.route('/session/<int:session_id>')
def view_session(session_id):
    """View details of a specific session"""
    session_data = Session.query.get_or_404(session_id)
    comments = Comment.query.filter_by(session_id=session_id).all()
    
    return render_template('index.html', 
                          session_data=session_data,
                          comments=comments,
                          is_running=is_running,
                          config=config)

@app.route('/config', methods=['GET', 'POST'])
def update_config():
    """Update configuration settings"""
    if request.method == 'POST':
        config.x_username = request.form.get('x_username', config.x_username)
        config.x_password = request.form.get('x_password', config.x_password)
        config.comments_per_session = int(request.form.get('comments_per_session', config.comments_per_session))
        config.delay_between_comments = int(request.form.get('delay_between_comments', config.delay_between_comments))
        config.save()
        
        flash('Configuration updated successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('index.html', config=config, show_config=True)

@app.route('/api/status')
def get_status():
    """API endpoint to get current status"""
    response = {
        'is_running': is_running,
        'active_session': None
    }
    
    if active_session:
        # Get comment count
        comment_count = Comment.query.filter_by(session_id=active_session.id).count()
        
        response['active_session'] = {
            'id': active_session.id,
            'created_at': active_session.created_at.isoformat(),
            'comments_processed': comment_count,
            'comments_target': active_session.comments_target
        }
    
    return jsonify(response)

# Create all database tables
with app.app_context():
    db.create_all()
