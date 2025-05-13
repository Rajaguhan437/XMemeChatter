import logging
import time
import random

logger = logging.getLogger(__name__)

class AIGenerator:
    """Class to handle AI assistant interactions for generating replies
    
    Note: This is a mock version for demo purposes without requiring a real browser.
    The actual implementation would use Selenium with a real browser.
    """
    
    def __init__(self, config):
        self.config = config
        self.driver = None
        self.ai_provider = config.ai_provider  # "chatgpt" or "xai"
        self.ai_urls = {
            "chatgpt": "https://chat.openai.com/",
            "xai": "https://x.ai/"
        }
        
        # Sample witty responses for simulation
        self.sample_responses = [
            "That's a fascinating hill to die on. Did you pack a lunch for the climb?",
            "Your opinion is so unique, they're saving it in a museum of terrible ideas.",
            "I'd agree with you, but then we'd both be wrong.",
            "I'm not saying you're wrong, but Google just automatically started a fact-check.",
            "Wow, you really woke up and chose chaos today.",
            "That's the kind of hot take that makes thermometers explode.",
            "If that opinion were any more half-baked, it would still be raw dough.",
            "Congratulations! Your comment just won first place in the bad take Olympics.",
            "Not sure if that's your opinion or if your keyboard just fell down the stairs.",
            "On a scale from 1 to 10, that take is a solid yikes.",
            "That's not just a bad take, that's a catastrophic nuclear take.",
            "Your logic is so circular it should apply for a job at NASA.",
            "I've seen more convincing arguments from my toaster.",
            "Did your brain take a vacation, or is this its normal operating mode?",
            "If wrong answers made a sound, yours would be a foghorn."
        ]
    
    def open_browser(self):
        """Open a browser window for AI assistant (Mock)"""
        logger.info(f"Mock: Opening browser for {self.ai_provider}")
        time.sleep(1)  # Simulate browser startup time
        self.driver = "mock_browser"
        logger.info(f"Mock: {self.ai_provider} browser opened successfully")
        return True
    
    def close_browser(self):
        """Close the browser window (Mock)"""
        logger.info(f"Mock: {self.ai_provider} browser closed")
        self.driver = None
    
    def _handle_login(self):
        """Handle logging into the AI service if needed (Mock)"""
        logger.info(f"Mock: {self.ai_provider} logged in automatically")
        return True
    
    def generate_reply(self, prompt):
        """Generate a reply using the AI assistant (Mock)
        
        In this mock version, we select a random witty response from our samples
        and customize it to match the prompt context if possible.
        """
        logger.info(f"Mock: Generating reply with {self.ai_provider} for prompt: {prompt[:30]}...")
        
        if not self.driver:
            logger.error("Mock: AI browser not opened")
            return "Sorry, I couldn't generate a reply. AI service not available."
        
        # Extract the original tweet text from the prompt
        original_text = ""
        if "to this X comment:" in prompt:
            parts = prompt.split("to this X comment:", 1)
            if len(parts) > 1:
                original_text = parts[1].strip().strip("'")
        
        # Simulate AI thinking time
        time.sleep(2)
        
        # Pick a random response from our samples
        response = random.choice(self.sample_responses)
        
        # For some responses, try to customize based on the original text
        if original_text and random.random() > 0.5:
            # Look for keywords in the original text to customize the response
            keywords = ["movie", "team", "earth", "politics", "pizza", "AI", "book"]
            
            for keyword in keywords:
                if keyword.lower() in original_text.lower():
                    # Generate a more specific response based on the keyword
                    if keyword == "movie":
                        custom_responses = [
                            f"Your movie taste is so bad, Netflix just created a 'Please Don't Watch' category for you.",
                            f"That's the kind of movie opinion that makes film critics consider a career change."
                        ]
                        response = random.choice(custom_responses)
                        break
                    elif keyword == "team":
                        response = f"Your team is so bad, they'd lose a game of solitaire."
                        break
                    elif keyword == "earth":
                        response = f"Your flat earth theory holds less water than a pasta strainer."
                        break
                    elif keyword == "politics":
                        response = f"Your political take is so hot, it just melted my screen."
                        break
                    elif keyword == "pizza":
                        response = f"Defending pineapple on pizza? I've seen better arguments from a toddler explaining why bedtime is 'unfair'."
                        break
                    elif keyword == "AI":
                        response = f"'AI will never replace human creativity' is exactly what my code predicted you'd say."
                        break
                    elif keyword == "book":
                        response = f"Saying the book was better is just a fancy way of admitting you can read. Congratulations!"
                        break
        
        logger.info(f"Mock: Generated reply: {response}")
        return response
