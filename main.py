import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rapidfuzz import process, fuzz
from fastapi.middleware.cors import CORSMiddleware

# Remove annoying errors
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# FastAPI app setup
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Service is up and running!"}

# Allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify your frontend's origin here
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Define Pydantic model for request body
class UserInput(BaseModel):
    user_input: str

# Keyword-response mapping
keyword_responses = {
    "projects": (
        "I've had the privilege of working on some fascinating projects that reflect my technical skills and interests. "
        "For example, I developed a 2D dungeon crawler in Pygame, writing over 4,000 lines of Python code to create engaging gameplay mechanics. "
        "I then used this project as a baseline to teach younger students at my school how to make games in the Games Creators Club. "
        "Another highlight was my hackathon project, an educational space exploration website built using Three.js, where I contributed to interactive 3D visualizations "
        "and user-friendly interfaces, making the learning experience immersive and enjoyable. "
        "If you are seeing this, I am currently working on implementing links to my projects directly into my website however, I haven't quite finished yet. "
        "If you want to see my projects first hand, please visit my github: https://github.com/CharlieGEdmunds."
    ),
    # Add other keyword_responses here...
}

synonyms = {
    "projects": ["projects", "games", "work", "projects I've worked on", "creation", "developments", "undertakings", "contributions", "builds", "designs", "ventures"],
    # Add other synonyms here...
}

# Introduction message
intro_message = "Hello! Welcome to my chatbot portfolio website. I'm here to assist you with any questions you have. Try asking about topics like 'projects', 'education', 'experience', 'personal details', 'tools', or 'experience'!"

@app.get("/chatbot/intro")
async def chatbot_intro():
    return {"response": intro_message}

def find_response(user_input):
    user_input = user_input.lower()

    for keyword, keyword_synonyms in synonyms.items():
        for synonym in keyword_synonyms:
            if synonym in user_input:
                return keyword_responses[keyword]

    keywords = list(keyword_responses.keys())
    matches = process.extract(user_input, keywords, scorer=fuzz.partial_ratio, limit=2)

    if len(matches) > 1 and matches[0][1] - matches[1][1] < 10:
        top_matches = ", ".join([f"'{match[0]}' ({match[1]}%)" for match in matches])
        return f"I found multiple topics you might be asking about: {top_matches}. Could you clarify?"
    if matches[0][1] > 60:
        return keyword_responses[matches[0][0]]
    return None

def generate_response(user_input):
    keyword_response = find_response(user_input)
    if keyword_response:
        return keyword_response

    return "Please re-enter your question."

# FastAPI route for chatbot
@app.post("/chatbot/")
async def chatbot(user_input: UserInput):
    response = generate_response(user_input.user_input)
    return {"response": response}

# Run the app with: uvicorn <filename>:app --reload
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Use the port environment variable
    uvicorn.run(app, host="0.0.0.0", port=port)