"""
Services for the chat application, including LLM integration.
"""
import os
import time
import logging
import requests
from django.conf import settings

# Set up logging
logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with LLM models."""

    def __init__(self):
        # Default to using a local model, but can be configured to use an API
        self.use_api = getattr(settings, 'LLM_USE_API', False)
        self.api_key = getattr(settings, 'LLM_API_KEY', None)
        self.api_url = getattr(settings, 'LLM_API_URL', 'http://localhost:8000/v1/completions')
        self.model_name = getattr(settings, 'LLM_MODEL_NAME', 'llama2-7b-chat')
        self.max_tokens = getattr(settings, 'LLM_MAX_TOKENS', 256)
        self.temperature = getattr(settings, 'LLM_TEMPERATURE', 0.7)

        # For local model (using transformers library)
        self.model = None
        self.tokenizer = None

    def _load_local_model(self):
        """Load the model locally using transformers library."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer

            if self.model is None or self.tokenizer is None:
                logger.info(f"Loading model {self.model_name}...")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    device_map="auto",
                    load_in_8bit=True  # Use 8-bit quantization for efficiency
                )
                logger.info("Model loaded successfully")
        except ImportError:
            logger.error("Transformers library not installed. Please install it with: pip install transformers")
            return False
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
        return True

    def _generate_local(self, prompt):
        """Generate a response using a local model."""
        if not self._load_local_model():
            return "Sorry, I'm having trouble accessing my knowledge. Please try again later."

        try:
            # Prepare the prompt with appropriate formatting
            formatted_prompt = f"<s>[INST] {prompt} [/INST]"

            # Tokenize the input
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.model.device)

            # Generate response
            outputs = self.model.generate(
                inputs.input_ids,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                do_sample=True,
                top_p=0.95,
            )

            # Decode the response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract just the model's response (after the prompt)
            response = response.split("[/INST]")[-1].strip()

            return response
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble processing your question right now."

    def _generate_api(self, prompt):
        """Generate a response using an API."""
        if not self.api_key:
            logger.error("API key not configured")
            return "Sorry, I'm not properly configured to answer questions right now."

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model_name,
                "prompt": f"<s>[INST] {prompt} [/INST]",
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
            }

            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result.get("choices", [{}])[0].get("text", "").strip()
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return "I'm having trouble connecting to my knowledge base. Please try again later."

        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return "I'm having trouble connecting to my knowledge base. Please try again later."

    def generate_health_response(self, prompt):
        """
        Generate a health-related response to the given prompt.

        Args:
            prompt (str): The user's health-related question

        Returns:
            str: The generated response
        """
        # Check if we're configured to always use rule-based responses
        rule_threshold = getattr(settings, 'LLM_RULE_THRESHOLD', 0.7)
        if rule_threshold >= 1.0:
            return "I'm currently operating in rule-based mode only. For more complex questions, please consult with a healthcare professional."

        # Add healthcare context to the prompt
        healthcare_prompt = (
            f"You are an AI health assistant in a healthcare system. "
            f"Provide a helpful, accurate, and concise response to this health-related question: {prompt}\n\n"
            f"Keep your answer brief and focused on providing general health information. "
            f"Always remind the user to consult healthcare professionals for personalized advice."
        )

        start_time = time.time()

        try:
            if self.use_api:
                response = self._generate_api(healthcare_prompt)
            else:
                response = self._generate_local(healthcare_prompt)

            # Log the response time
            elapsed_time = time.time() - start_time
            logger.info(f"LLM response generated in {elapsed_time:.2f} seconds")

            return response
        except Exception as e:
            logger.error(f"Error in generate_health_response: {str(e)}")
            return "I apologize, but I'm having trouble answering your question right now. Please try again later or consult with a healthcare professional."

# Initialize the LLM service
llm_service = LLMService()
