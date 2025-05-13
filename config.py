import os
import json
import logging

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for the X reply automation tool"""
    
    def __init__(self):
        self.config_file = "config.json"
        
        # Default configuration values
        self.x_username = ""
        self.x_password = ""
        self.ai_provider = "chatgpt"  # "chatgpt" or "xai"
        self.chatgpt_username = ""
        self.chatgpt_password = ""
        self.comments_per_session = 20
        self.delay_between_comments = 15  # seconds
        
        # Load configuration from file if it exists
        self.load()
    
    def load(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                # Update configuration values
                for key, value in data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                
                logger.info("Configuration loaded from file")
                return True
            else:
                logger.info("Configuration file not found, using defaults")
                return False
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return False
    
    def save(self):
        """Save configuration to file"""
        try:
            # Create a dictionary of configuration values
            data = {
                "x_username": self.x_username,
                "x_password": self.x_password,
                "ai_provider": self.ai_provider,
                "chatgpt_username": self.chatgpt_username,
                "chatgpt_password": self.chatgpt_password,
                "comments_per_session": self.comments_per_session,
                "delay_between_comments": self.delay_between_comments
            }
            
            # Write to file
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=4)
            
            logger.info("Configuration saved to file")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
