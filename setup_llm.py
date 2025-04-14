#!/usr/bin/env python
"""
Setup script for the LLM integration in the healthcare system.
This script helps users download and configure the LLM model.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("LLM-Setup")

def check_dependencies():
    """Check if required dependencies are installed."""
    # Check for OpenAI package first
    try:
        import openai
        logger.info("✅ OpenAI package is installed.")
        openai_available = True
    except ImportError:
        logger.warning("⚠️ OpenAI package is not installed. You won't be able to use OpenAI models.")
        logger.warning("   Install it with: pip install openai")
        openai_available = False

    # Check for local model dependencies
    try:
        import torch
        import transformers
        import accelerate
        import bitsandbytes
        import sentencepiece

        logger.info("✅ All local model dependencies are installed.")

        # Check CUDA availability
        if torch.cuda.is_available():
            logger.info(f"✅ CUDA is available. Found {torch.cuda.device_count()} device(s).")
            logger.info(f"   Device: {torch.cuda.get_device_name(0)}")
        else:
            logger.warning("⚠️ CUDA is not available. Local models will run on CPU, which may be slow.")

        local_deps_available = True
    except ImportError as e:
        logger.warning(f"⚠️ Missing local model dependency: {str(e)}")
        logger.warning("   Local models won't be available unless you install all dependencies.")
        logger.warning("   Install them with: pip install -r requirements.txt")
        local_deps_available = False

    # Return True if at least one option is available
    if openai_available or local_deps_available:
        return True
    else:
        logger.error("❌ Neither OpenAI nor local model dependencies are available.")
        logger.error("   Please install at least one of them to use the LLM integration.")
        return False

def download_model(model_name):
    """Download the specified model."""
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM

        logger.info(f"Downloading model: {model_name}")
        logger.info("This may take some time depending on your internet connection...")

        # Download tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        logger.info("✅ Tokenizer downloaded successfully.")

        # Download model
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            load_in_8bit=True
        )
        logger.info("✅ Model downloaded successfully.")

        # Test the model with a simple prompt
        logger.info("Testing the model with a simple prompt...")
        inputs = tokenizer("Hello, I have a question about healthcare.", return_tensors="pt").to(model.device)
        outputs = model.generate(inputs.input_ids, max_new_tokens=50)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        logger.info(f"Model test response: {response}")
        logger.info("✅ Model is working correctly.")

        return True
    except Exception as e:
        logger.error(f"❌ Error downloading model: {str(e)}")
        return False

def update_settings(model_name, use_api=False, api_key="", api_url="", api_provider="openai"):
    """Update the Django settings file with LLM configuration."""
    try:
        settings_path = Path("healthcare_system") / "settings.py"

        if not settings_path.exists():
            settings_path = Path(".") / "healthcare_system" / "settings.py"

        if not settings_path.exists():
            logger.error(f"❌ Could not find settings.py file at {settings_path}")
            return False

        with open(settings_path, 'r') as f:
            settings_content = f.read()

        # Check if LLM settings already exist
        if "LLM_MODEL_NAME" in settings_content:
            # Update existing settings
            lines = settings_content.split('\n')
            updated_lines = []

            for line in lines:
                if line.startswith("LLM_USE_API"):
                    line = f"LLM_USE_API = {str(use_api)}"
                elif line.startswith("LLM_API_PROVIDER"):
                    line = f"LLM_API_PROVIDER = '{api_provider}'"
                elif line.startswith("LLM_API_KEY") and api_key:
                    line = f"LLM_API_KEY = '{api_key}'"
                elif line.startswith("LLM_API_URL") and api_url:
                    line = f"LLM_API_URL = '{api_url}'"
                elif line.startswith("LLM_MODEL_NAME"):
                    line = f"LLM_MODEL_NAME = '{model_name}'"
                elif line.startswith("LLM_RULE_THRESHOLD") and use_api and api_provider == 'openai':
                    line = f"LLM_RULE_THRESHOLD = 0.0  # Always use LLM responses with OpenAI"

                updated_lines.append(line)

            updated_settings = '\n'.join(updated_lines)
        else:
            # Add new LLM settings
            llm_settings = f"""
# LLM Settings
# Set to True to use API, False to use local model
LLM_USE_API = {str(use_api)}
# API provider ('openai', 'generic')
LLM_API_PROVIDER = '{api_provider}'
# API key for external LLM service (if using API)
LLM_API_KEY = '{api_key}'
# API URL for external LLM service (if using generic API)
LLM_API_URL = '{api_url or "http://localhost:8000/v1/completions"}'
# Model name (used for both API and local model)
LLM_MODEL_NAME = '{model_name}'
# Maximum tokens to generate
LLM_MAX_TOKENS = 256
# Temperature for generation (higher = more creative, lower = more deterministic)
LLM_TEMPERATURE = 0.7
# Probability threshold for rule-based vs LLM responses (0.0-1.0)
# Higher values will use rule-based responses more often
LLM_RULE_THRESHOLD = {'0.0' if use_api and api_provider == 'openai' else '0.7'}
"""
            # Add settings before the last line
            updated_settings = settings_content.rstrip() + llm_settings

        # Write updated settings
        with open(settings_path, 'w') as f:
            f.write(updated_settings)

        logger.info("✅ Settings updated successfully.")
        return True
    except Exception as e:
        logger.error(f"❌ Error updating settings: {str(e)}")
        return False

def main():
    """Main function to set up the LLM integration."""
    parser = argparse.ArgumentParser(description="Setup LLM integration for healthcare system")
    parser.add_argument("--model", default="gpt-3.5-turbo",
                        help="Model name to use (default: gpt-3.5-turbo for OpenAI, TinyLlama/TinyLlama-1.1B-Chat-v1.0 for local)")
    parser.add_argument("--use-api", action="store_true", help="Use API instead of local model")
    parser.add_argument("--api-provider", default="openai", choices=["openai", "generic"],
                        help="API provider to use (default: openai)")
    parser.add_argument("--api-key", default=os.environ.get('OPENAI_API_KEY', ''),
                        help="API key for external LLM service (default: from OPENAI_API_KEY environment variable)")
    parser.add_argument("--api-url", default="", help="API URL for external LLM service (only for generic API)")
    parser.add_argument("--skip-download", action="store_true", help="Skip model download for local models")

    args = parser.parse_args()

    logger.info("Starting LLM setup for healthcare system...")

    # Check dependencies
    if not check_dependencies():
        return 1

    # Set default model based on API provider if not specified
    if args.model == "gpt-3.5-turbo" and not args.use_api:
        args.model = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        logger.info(f"Using default local model: {args.model}")

    # Download model if not using API and not skipping download
    if not args.use_api and not args.skip_download:
        if not download_model(args.model):
            return 1

    # Update settings
    if not update_settings(args.model, args.use_api, args.api_key, args.api_url, args.api_provider):
        return 1

    logger.info("✅ LLM setup completed successfully!")
    logger.info(f"Model: {args.model}")
    logger.info(f"Mode: {'API (' + args.api_provider + ')' if args.use_api else 'Local'}")

    if args.use_api:
        if args.api_provider == 'openai':
            logger.info(f"API Provider: OpenAI")
            logger.info(f"API Key: {'Configured' if args.api_key else 'Not configured'}")
        else:
            logger.info(f"API URL: {args.api_url or 'http://localhost:8000/v1/completions'}")

    logger.info("\nTo learn more about the LLM integration, see LLM_INTEGRATION.md")

    return 0

if __name__ == "__main__":
    sys.exit(main())
