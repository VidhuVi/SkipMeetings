# test_gemini.py
import os
from dotenv import load_dotenv # Import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Load environment variables from .env file
load_dotenv()

# Ensure your API key is set as an environment variable
if "GOOGLE_API_KEY" not in os.environ:
    print("ERROR: GOOGLE_API_KEY environment variable not set.")
    print("Please ensure you have a .env file with GOOGLE_API_KEY='YOUR_API_KEY'")
    exit()

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)

try:
    response = llm.invoke([HumanMessage(content="Hello, how are you today?")])
    print(f"Gemini says: {response.content}")
except Exception as e:
    print(f"An error occurred: {e}")
    print("Please check your API key, internet connection, and model availability.")