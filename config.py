"""
MAX PAY Payment Integration - Configuration
Load environment variables for Max Pay API credentials
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for Max Pay integration"""
    
    # Max Pay API Credentials
    MAX_API_KEY = os.environ.get('MAX_API_KEY', '')
    MAX_MERCHANT_ID = os.environ.get('MAX_MERCHANT_ID', '')
    MAX_API_URL = os.environ.get('MAX_API_URL', 'https://api.maxpay.example.com/v1/payments')
    MAX_WEBHOOK_SECRET = os.environ.get('MAX_WEBHOOK_SECRET', '')
    
    # Application URLs (customize these for your domain)
    SUCCESS_URL = os.environ.get('SUCCESS_URL', 'https://mydomain.com/success')
    CANCEL_URL = os.environ.get('CANCEL_URL', 'https://mydomain.com/cancel')
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    @staticmethod
    def validate():
        """Validate that required environment variables are set"""
        required_vars = [
            'MAX_API_KEY',
            'MAX_MERCHANT_ID',
            'MAX_WEBHOOK_SECRET'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
