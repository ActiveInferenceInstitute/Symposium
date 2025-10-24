import os
import json
import logging
from openai import OpenAI
from pathlib import Path
from datetime import datetime

def setup_logging(name=__name__):
    """Set up logging configuration."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(name)
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)
    return logger

def load_api_key():
    """Load API key from configuration file."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        key_file_path = os.path.join(script_dir, "llm_keys.key")
        
        with open(key_file_path, 'r') as f:
            keys = json.load(f)
            if not keys.get("perplexity"):
                raise ValueError("Perplexity API key not found in config file")
            return keys["perplexity"]
    except Exception as e:
        logging.error(f"Error reading API key: {str(e)}")
        raise

def get_perplexity_client():
    """Initialize and return Perplexity client."""
    api_key = load_api_key()
    return OpenAI(
        api_key=api_key,
        base_url="https://api.perplexity.ai"
    )

def get_model_config():
    """Get model configuration."""
    return {
        "model": "llama-3.1-sonar-large-128k-online",
        "temperature": 0.7,
        "max_tokens": 2000
    }

def get_perplexity_response(client, prompt, system_prompt="You are a research analyst specializing in academic analysis."):
    """Get response from Perplexity API with standard configuration."""
    try:
        config = get_model_config()
        
        response = client.chat.completions.create(
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        
        if not response or not response.choices:
            raise ValueError("Empty response from Perplexity API")
            
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error getting Perplexity response: {e}")
        raise

def save_markdown_report(content, output_path, title):
    """Save report in markdown format."""
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(content)
            
        logging.info(f"Saved report to {output_path}")
    except Exception as e:
        logging.error(f"Error saving report to {output_path}: {e}")
        raise

def save_json_report(content, output_path, metadata=None):
    """Save report in JSON format."""
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "content": content
        }
        
        if metadata:
            data.update(metadata)
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        logging.info(f"Saved JSON report to {output_path}")
    except Exception as e:
        logging.error(f"Error saving JSON report to {output_path}: {e}")
        raise