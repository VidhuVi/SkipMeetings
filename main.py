# main.py
from fastapi import FastAPI
import gradio as gr
from gradio_ui import create_gradio_blocks_app # Import the function to create Gradio app

# Initialize FastAPI app
app = FastAPI()

# Create the Gradio app instance using the function from gradio_ui.py
gradio_app = create_gradio_blocks_app()

# Mount the Gradio app to a subpath of your FastAPI application
# This means your Gradio UI will be accessible at YOUR_RENDER_URL/gradio
app = gr.mount_gradio_app(app, gradio_app, path="/gradio")

# Optional: Add a simple root endpoint for your API (useful for health checks)
@app.get("/")
async def root():
    return {"message": "Welcome to the Meeting Summarizer API. Go to /gradio for the UI."}

# You can add other FastAPI endpoints here if you want to expand your API later
# For example:
# @app.post("/api/summarize")
# async def summarize_api(text: str):
#     summary_report = get_meeting_summary_report(text)
#     return {"summary": summary_report}