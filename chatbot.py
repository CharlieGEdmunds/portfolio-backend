from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rapidfuzz import process, fuzz
import os
from fastapi.middleware.cors import CORSMiddleware

# Remove annoying errors
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

# FastAPI app setup
app = FastAPI()

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
    "education": (
        "I'm currently pursuing a BSc (Hons) in Computer Science at The University of Manchester, where I earned a First Class result (77%) in my first year. "
        "During my studies, I've led the frontend development of an award-winning AI-powered timetabling website and delved into a variety of subjects, "
        "including Machine Learning, Algorithms, Software Engineering, and Knowledge-Based AI."
    ),
    "experience": (
        "My experience has been diverse and impactful. As a tutor, I've designed and led personalized lessons to help underrepresented students succeed in mathematics. "
        "In addition, I co-organize and facilitate game development workshops at UniCS, mentoring over 100 society members and nurturing their skills in game design and programming. "
        "These roles have honed my ability to collaborate, teach, and lead effectively."
    ),
    "personal": (
        "Outside academics, I'm passionate about badminton, where I've competed at the county level and won several club tournaments. "
        "I also enjoy exploring creative challenges in game development, such as building unique mechanics and immersive worlds that merge technical and artistic skills. "
        "These hobbies balance my academic pursuits and keep me motivated."
    ),
    "tools": (
        "I'm skilled in a range of tools and languages, including Python (for machine learning, NLP, and data visualization), JavaScript (Three.js for interactive 3D content), "
        "C# (for Unity game development), and C++ (for general programming problems). While not my first choice of language, "
        "I am also very familiar with the following from university: Java, C, HTML, CSS, PHP, Assembly."
    ),
    "achievements": (
        "Some of my proudest achievements include earning the Microsoft Azure AI Fundamentals certification with a 95% score and winning first place in my university's design and implementation award. "
        "Additionally, my leadership in a high school Games Creation Club helped foster a love for programming among younger students, demonstrating my commitment to mentorship and innovation."
    ),
}

synonyms = {
    "projects": ["projects", "games", "work", "projects I've worked on", "creation", "developments", "undertakings", "contributions", "builds", "designs", "ventures"],
    "education": ["education", "studies", "learning", "school", "academic", "training", "schooling", "curriculum", "degree", "qualifications", "knowledge acquisition"],
    "experience": ["experience", "background", "expertise", "knowledge", "history", "skills", "track record", "professional experience", "work experience", "know-how", "competency", "proficiency"],
    "personal": ["tell me about yourself", "about you", "your background", "who are you", "your story", "about yourself", "personal details", "yourself"],
    "tools": ["tools", "technologies", "software", "languages", "platforms", "frameworks", "technological stack", "programming languages", "development tools", "skillset"],
    "achievements": ["achievements", "accomplishments", "milestones", "awards", "recognitions", "successes", "honors", "certifications", "notable achievements", "victories", "distinctions", "certifications"],
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