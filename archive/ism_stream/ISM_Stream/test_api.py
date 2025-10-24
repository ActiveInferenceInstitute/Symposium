from Perplexity_Methods import get_perplexity_client, get_perplexity_response
import logging

def test_api():
    logging.basicConfig(level=logging.INFO)
    try:
        client = get_perplexity_client()
        response = get_perplexity_response(
            client, 
            "Please respond with 'API connection successful' if you receive this message."
        )
        print("\nAPI Test Results:")
        print("================")
        print(f"Response: {response}")
        print("================\n")
    except Exception as e:
        print("\nAPI Test Failed:")
        print("================")
        print(f"Error: {str(e)}")
        print("================\n")

if __name__ == "__main__":
    test_api() 