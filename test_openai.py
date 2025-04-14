#!/usr/bin/env python
"""
Test script for OpenAI integration in the healthcare system.
This script tests the OpenAI API connection and generates a sample response.
"""

import os
import sys
import logging
import django

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("OpenAI-Test")

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare_system.settings')
try:
    django.setup()
except Exception as e:
    logger.error(f"Error setting up Django: {str(e)}")
    sys.exit(1)

# Import settings and services
from django.conf import settings
from chat.services import llm_service

def test_openai_connection():
    """Test the OpenAI API connection."""
    logger.info("Testing OpenAI API connection...")
    
    # Check if OpenAI is properly configured
    if not settings.LLM_USE_API:
        logger.error("❌ LLM_USE_API is set to False. Please set it to True in settings.py.")
        return False
        
    if settings.LLM_API_PROVIDER != 'openai':
        logger.error(f"❌ LLM_API_PROVIDER is set to '{settings.LLM_API_PROVIDER}'. Please set it to 'openai' in settings.py.")
        return False
        
    if not settings.LLM_API_KEY:
        logger.error("❌ LLM_API_KEY is not set. Please add your OpenAI API key in settings.py.")
        return False
    
    # Test the OpenAI client
    if not llm_service.openai_client:
        logger.error("❌ OpenAI client not initialized. Check your configuration.")
        return False
    
    logger.info("✅ OpenAI client initialized successfully.")
    return True

def test_openai_response():
    """Test generating a response using OpenAI."""
    logger.info("Testing OpenAI response generation...")
    
    # Sample health question
    test_question = "What are the symptoms of the common cold?"
    
    try:
        # Generate response
        logger.info(f"Generating response for: '{test_question}'")
        response = llm_service.generate_health_response(test_question)
        
        # Display response
        logger.info("Response received:")
        logger.info("-" * 50)
        logger.info(response)
        logger.info("-" * 50)
        
        return True
    except Exception as e:
        logger.error(f"❌ Error generating response: {str(e)}")
        return False

def main():
    """Main function to test OpenAI integration."""
    logger.info("Starting OpenAI integration test...")
    
    # Test connection
    if not test_openai_connection():
        logger.error("❌ OpenAI connection test failed.")
        return 1
    
    # Test response generation
    if not test_openai_response():
        logger.error("❌ OpenAI response generation test failed.")
        return 1
    
    logger.info("✅ OpenAI integration test completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
