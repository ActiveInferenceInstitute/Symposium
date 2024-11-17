import os
from openai import OpenAI
import logging
import json
from pathlib import Path
import time
from typing import Optional
import backoff  # you'll need to: pip install backoff

def setup_logging(name=__name__):
    """Set up logging configuration."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(name)
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)
    return logger

def get_openrouter_client():
    """Initialize OpenRouter client"""
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")

    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

# Exponential backoff decorator for handling rate limits
@backoff.on_exception(
    backoff.expo,
    (Exception),  # You might want to specify exact exceptions
    max_tries=5,  # Maximum number of retries
    max_time=300,  # Maximum total time to try in seconds
    giveup=lambda e: not (isinstance(e, Exception) and
        ('rate' in str(e).lower() or 'timeout' in str(e).lower())),
)
def get_openrouter_response_with_retry(client, prompt: str,
                                     max_retries: int = 10,
                                     retry_delay: int = 10) -> Optional[str]:
    """
    Get response from OpenRouter API with retry logic

    Args:
        client: OpenRouter client
        prompt: Input prompt
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        Response content or None if all retries failed
    """
    retries = 0
    while retries < max_retries:
        try:
            response = client.chat.completions.create(
                model="google/gemini-pro-1.5-exp",
                messages=[{"role": "user", "content": prompt}]
            )

            # Check if response is valid
            if response and response.choices and response.choices[0].message.content:
                return response.choices[0].message.content

            logging.warning(f"Empty or invalid response received, attempt {retries + 1}/{max_retries}")

        except Exception as e:
            logging.error(f"Error getting OpenRouter response (attempt {retries + 1}/{max_retries}): {e}")

            # Check if it's a rate limit error
            if 'rate' in str(e).lower():
                logging.info(f"Rate limit hit. Waiting {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logging.error(f"Unexpected error: {e}")
                if '400' in str(e):
                    logging.error("Request details for debugging:")
                    logging.error(f"Prompt length: {len(prompt)}")
                    logging.error(f"First 100 chars of prompt: {prompt[:100]}...")

        retries += 1
        time.sleep(retry_delay)

    logging.error("All retry attempts failed")
    return None

def get_openrouter_response(client, prompt: str) -> str:
    """
    Main response function that handles retries and validates output
    """
    response = get_openrouter_response_with_retry(client, prompt)

    if response is None:
        raise Exception("Failed to get valid response after all retries")

    return response

def save_markdown_report(content: str, filepath: Path, title: str):
    """Save report in markdown format"""
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(content)

    except Exception as e:
        logging.error(f"Error saving markdown report: {e}")
        raise

def save_json_report(content: str, filepath: Path, metadata: dict):
    """Save report in JSON format"""
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "metadata": metadata,
            "content": content
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    except Exception as e:
        logging.error(f"Error saving JSON report: {e}")
        raise

