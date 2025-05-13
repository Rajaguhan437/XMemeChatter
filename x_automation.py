import time
import logging
import random

logger = logging.getLogger(__name__)

class XAutomation:
    """Class to handle X (Twitter) website automation
    
    Note: This is a mock version for demo purposes without requiring a real browser.
    The actual implementation would use Selenium with a real browser.
    """
    
    def __init__(self, config):
        self.config = config
        self.driver = None
        self.x_base_url = "https://twitter.com/"
        self.logged_in = False
        
        # Mock data for simulation
        self.mock_tweets = [
            {"id": 1, "author": "user1", "text": "This movie was terrible! Waste of money."},
            {"id": 2, "author": "user2", "text": "I can't believe people still think the earth is round."},
            {"id": 3, "author": "user3", "text": "My team is the best team in the entire league!"},
            {"id": 4, "author": "user4", "text": "Politics these days is so divisive."},
            {"id": 5, "author": "user5", "text": "Pineapple absolutely belongs on pizza."},
            {"id": 6, "author": "user6", "text": "I waited 3 hours for this movie and it was a complete disaster."},
            {"id": 7, "author": "user7", "text": "AI will never replace human creativity."},
            {"id": 8, "author": "user8", "text": "I don't understand why people like that show so much."},
            {"id": 9, "author": "user9", "text": "The book was so much better than the movie adaptation."},
            {"id": 10, "author": "user10", "text": "This is the worst customer service I've ever experienced!"}
        ]
    
    def open_browser(self):
        """Open a browser window for X (Mock)"""
        logger.info("Mock: Opening browser for X")
        time.sleep(1)  # Simulate browser startup time
        self.driver = "mock_browser"
        logger.info("Mock: X browser opened successfully")
        return True
    
    def close_browser(self):
        """Close the browser window (Mock)"""
        logger.info("Mock: X browser closed")
        self.driver = None
        self.logged_in = False
    
    def is_logged_in(self):
        """Check if user is logged in to X (Mock)"""
        return self.logged_in
    
    def login(self):
        """Login to X using credentials from config (Mock)"""
        logger.info("Mock: Attempting to login to X")
        
        if not self.driver:
            logger.error("Mock: Browser not opened")
            return False
        
        # Check if credentials are provided
        if self.config.x_username and self.config.x_password:
            time.sleep(2)  # Simulate login time
            self.logged_in = True
            logger.info(f"Mock: Successfully logged into X as {self.config.x_username}")
            return True
        else:
            logger.error("Mock: Missing X credentials")
            return False
    
    def navigate_to_feed(self):
        """Navigate to the target feed (Mock)"""
        logger.info("Mock: Navigating to target feed")
        
        if not self.logged_in:
            logger.error("Mock: Not logged in")
            return False
        
        time.sleep(1)  # Simulate page load
        logger.info("Mock: Successfully navigated to feed")
        return True
    
    def find_comments_to_reply(self, count=5):
        """Find comments/tweets that can be replied to (Mock)"""
        logger.info(f"Mock: Looking for {count} comments to reply to")
        
        if not self.logged_in:
            logger.error("Mock: Not logged in")
            return []
        
        # Randomly select tweets to simulate finding new comments
        sample_size = min(count, len(self.mock_tweets))
        selected_tweets = random.sample(self.mock_tweets, sample_size)
        
        logger.info(f"Mock: Found {len(selected_tweets)} valid comments to reply to")
        return selected_tweets
    
    def extract_comment_data(self, comment_element):
        """Extract text and metadata from a comment/tweet element (Mock)"""
        # In our mock version, the comment_element is already our data dictionary
        return {
            'author': comment_element['author'],
            'text': comment_element['text'],
            'element': comment_element  # just pass through for compatibility
        }
    
    def post_reply(self, comment_element, reply_text):
        """Post a reply to a specific comment/tweet (Mock)"""
        logger.info(f"Mock: Posting reply to {comment_element['author']}: {reply_text[:30]}...")
        
        if not self.logged_in:
            logger.error("Mock: Not logged in")
            return False
        
        # Simulate posting delay
        time.sleep(1.5)
        
        logger.info("Mock: Reply posted successfully")
        return True
