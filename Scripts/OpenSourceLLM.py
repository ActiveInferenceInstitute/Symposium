import aiohttp
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import os

class CustomLLMClient:
    """Client for interacting with custom LLM endpoint."""
    
    def __init__(self, endpoint_url: Optional[str] = None):
        """
        Initialize the custom LLM client.
        
        Args:
            endpoint_url: Optional custom endpoint URL. If not provided, will try to read from environment.
        """
        self.output_dir = Path("Outputs")
        self.output_dir.mkdir(exist_ok=True)
        
        # Use the exact endpoint URL
        self.endpoint_url = (
            endpoint_url or 
            os.getenv('LLM_ENDPOINT_URL') or 
            "https://lil-stability-smoke-consultancy.trycloudflare.com/v1/chat/completions"
        )

    async def check_endpoint(self) -> bool:
        """Test if the endpoint is accessible."""
        async with aiohttp.ClientSession() as session:
            try:
                # For OpenAI-compatible endpoints, we should use GET request instead of HEAD
                async with session.get(
                    self.endpoint_url.replace("/v1/chat/completions", ""),  # Check base URL
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status in (200, 404)  # 404 is ok for base endpoint
            except:
                return False

    async def generate_response(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The input prompt for the LLM
            
        Returns:
            Response dictionary or None if request fails
        """
        # First check if endpoint is accessible
        if not await self.check_endpoint():
            print(f"Endpoint {self.endpoint_url} is not accessible")
            return None

        async with aiohttp.ClientSession() as session:
            try:
                payload = {
                    "model": "mistralai/Mistral-Nemo-Instruct-2407",  # Specific model
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
                
                headers = {
                    "Content-Type": "application/json",
                }
                
                async with session.post(
                    self.endpoint_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        print(f"Error status: {response.status}")
                        print(f"Error details: {await response.text()}")
                        return None
                    
                    return await response.json()
                    
            except Exception as e:
                print(f"Error: {str(e)}")
                return None

    def save_response(self, prompt: str, response: dict) -> None:
        """Save the prompt and response to a JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"llm_response_{timestamp}.json"
        
        output_data = {
            "timestamp": timestamp,
            "prompt": prompt,
            "response": response
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)
            print(f"Response saved to: {output_file}")

async def test_endpoint():
    """Test the endpoint with various prompts."""
    # Allow endpoint override from environment variable
    endpoint_url = os.getenv('LLM_ENDPOINT_URL')
    client = CustomLLMClient(endpoint_url)
    
    print(f"Testing endpoint availability: {client.endpoint_url}")
    if not await client.check_endpoint():
        print("Endpoint is not accessible. Please check the URL and try again.")
        return

    test_prompts = [
        "Hello"  # Simple test prompt to verify connection
    ]
    
    for prompt in test_prompts:
        print(f"\nTesting prompt: {prompt}")
        response = await client.generate_response(prompt)
        
        if response:
            print("Response received!")
            client.save_response(prompt, response)
            if 'choices' in response and len(response['choices']) > 0:
                print("Response content:", response['choices'][0]['message']['content'])
            else:
                print("Raw response:", response)
        else:
            print("No response received.")
        
        print("-" * 50)

if __name__ == "__main__":
    import asyncio
    print("Starting LLM endpoint test...")
    asyncio.run(test_endpoint())