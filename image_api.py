import openai
import requests
import streamlit as st

# Set your API keys
OPENAI_API_KEY = "your_openai_api_key"
UNSPLASH_API_KEY = "your_unsplash_api_key"

openai.api_key = OPENAI_API_KEY

def generate_ai_image(prompt: str, size="512x512"):
    """Generate an AI image using OpenAI's DALL·E."""
    if not prompt:
        return None, "Please enter a prompt."
    
    try:
        response = openai.Image.create(prompt=prompt, n=1, size=size)
        image_url = response["data"][0]["url"]
        return image_url, None
    except Exception as e:
        return None, str(e)


def fetch_unsplash_image(query: str):
    """Fetch a random image from Unsplash based on a query."""
    if not query:
        return None, "Please enter a search term."
    
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_API_KEY}"
    
    try:
        response = requests.get(url).json()
        if "urls" in response:
            return response["urls"]["regular"], None
        else:
            return None, "No image found."
    except Exception as e:
        return None, str(e)


def generate_chart():
    """Generate a sample bar chart using QuickChart API."""
    chart_url = "https://quickchart.io/chart?c={type:'bar',data:{labels:['A','B','C'],datasets:[{label:'Data',data:[10,20,30]}]}}"
    return chart_url