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

keyword_responses = {
    "projects": (
        "I've worked on some really exciting projects that showcase my skills and interests. "
        "One of my favorites was creating a 2D dungeon crawler in Pygame. It involved writing over 4,000 lines of Python code to make an impressive game using nothing but pygame. "
        "I then used this project as a baseline to teach younger students at my school how to make games in the Games Creators Club and documented it for my A-level programming project. "
        "Another highlight was my hackathon project, an educational space exploration website built using Three.js, where I contributed to the interactive 3D space environment "
        "and user-friendly interfaces for the planet cards, making the learning experience immersive and enjoyable. "
        "I'm currently working on adding links to my projects directly on my website, but in the meantime, you can check them out on my GitHub: github.com/CharlieGEdmunds."
    ),
    "education": (
        "I'm currently pursuing a BSc (Hons) in Computer Science at The University of Manchester, where I earned a First Class result (77%) in my first year. "
        "As part of my studies, I led the frontend development for an AI-powered timetabling website which won my university's best design and implementation award. "
        "In my first year, I earned top marks in key modules such as:"
        "Intro To Programming - 78%; Fundamentals of Computer Architecture - 89%; Fundamentals of Computation - 78%; Data Science - 78% and more... "
        "This year, I'm diving into modules like Database Systems, Intro to AI, Software Engineering, Machine Learning, Algorithms and Data Structures, and more!"
    ),
    "experience": (
        "My experience has been both diverse and rewarding, giving me opportunities to grow as a mentor, leader, and collaborator. "
        "As a mathematics tutor, I created and delivered personalized lesson plans to support underrepresented students, helping them build confidence and excel in their studies. This role strengthened my communication skills and taught me how to adapt my teaching style to meet the unique needs of each student. "
        "At university, I co-organize and lead game development workshops for UniCS, our Game Development Society. Through these workshops, I've mentored over 100 society members, guiding them in a wide range of game design principles, programming techniques, and collaborative projects. "
    ),
    "personal": (
        "Outside of academics, I have a real passion for badminton. It's been a big part of my life, from competing at the county level to winning several club tournaments. I've loved this sport form a young age as it's always been a great way to stay active and challenge myself. "
        "In addition, I have recently started enjoying long distance running and am currently working towards my goal of running a marathon in 2025."
        "I also enjoy game development in my free time. Working towards building a fun and interactive environment in games has always felt fun for me and this is a hobby I intend to continue alongside my studies. "
        "These hobbies help me to balance my academic pursuits and keep me motivated."
    ),
    "tools": (
        "I'm skilled in a range of tools and languages, including Python (for machine learning, NLP, and data visualization), JavaScript (Three.js for interactive 3D content), "
        "C# (for Unity game development), and C++ (for complex programming challenges). "
        "Additionally, my university coursework has made me well-versed in Java, C, HTML, CSS, PHP, and Assembly, even if they aren't my go-to choices for personal projects."
    ),
    "achievements": (
        "Some of my proudest achievements include earning the Microsoft Azure AI Fundamentals certification with a 95% score and winning first place in my university's design and implementation award for my first year group project. "
        "Additionally, my leadership in a high school Games Creation Club helped foster a love for programming among younger students, demonstrating my commitment to mentorship and innovation in others."
    ),
}

detailed_responses = {
    "projects": (
        "Here's more about my projects: I also have other projects such as my dungeons and dragons machine learning race classifier which is able to group races of DNDWiki by type using machine learning. "
        "Finally, there is my texas holdem networked unity game where you can play poker using netcode for game objects with your friends."
    ),
    "education": (
        "I studied my A-levels at Kenilworth School and Sixth Form where I Achieved: Computer Science - A*; Mathematics - A*; Further Mathematics - A*; Physics - A."
        "This is also where I volunteered at the games creators club for almost 4 years."
    ),
    "experience": (
        "I have also worked in summer 2022 for a company called hilotherm where I was paid to assist in the office regarding the maintenance and distribution of medical equiptment. "
        "I gained many valuable skills here such as communicating with clients over the phone and the distribution and packaging of important goods."
    ),
    "personal": (
        "Here's more about me: I'm a 19 year old student who is currently eager to land an internship role in data science or software engineering. "
        "Other hobbies of mine include dodgeball, camping/hiking, Dungeons & Dragons and skiing."
    ),
    "tools": (
        "Here's more about my technical skills: I've used Python as my primary language for many years now but am slowly transitioning towards C++ for some complex problems. "
        "I also have experience with arduino having made some projects with an arduino uno years ago."
    ),
    "achievements": (
        "Here's more about my achievements: In secondary school I achieved the gold certificate in the UKMT maths challenge many times and went on to compete in the kangaroo a few. "
        "I also got the highest mark in my entire school the one year we did the BEBRAS computer science challenge where I also competed in the following round."
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
intro_message = "Hello! Welcome to my chatbot portfolio website. I'm here to assist you with any questions you have. Try asking about topics like 'projects', 'education', 'experience', 'personal details', 'tools', or 'achievements'!"

@app.get("/chatbot/intro")
async def chatbot_intro():
    return {"response": intro_message}

def find_response(user_input):
    user_input = user_input.lower()

    if "more details" in user_input:
        for keyword in detailed_responses.keys():
            if keyword in user_input:
                return (detailed_responses[keyword], "detailed")

    for keyword, keyword_synonyms in synonyms.items():
        for synonym in keyword_synonyms:
            if synonym in user_input:
                return (keyword_responses[keyword], "normal")

    keywords = list(keyword_responses.keys())
    matches = process.extract(user_input, keywords, scorer=fuzz.partial_ratio, limit=2)

    if len(matches) > 1 and matches[0][1] - matches[1][1] < 10:
        top_matches = ", ".join([f"'{match[0]}' ({match[1]}%)" for match in matches])
        return f"I found multiple topics you might be asking about: {top_matches}. Could you clarify?"
    if matches[0][1] > 60:
        return (keyword_responses[matches[0][0]], "normal")
    return (None, None)

def generate_response(user_input):
    followup_message = "                                              If you want more info about this topic please type 'More details about [topic]'"
    keyword_response, response_type = find_response(user_input)
    if keyword_response:
        if response_type == "normal":
            return keyword_response + followup_message
        else:
            return keyword_response

    return "Please re-enter your question."

# FastAPI route for chatbot (changed back to POST)
@app.post("/chatbot/")
async def chatbot(user_input: UserInput):
    response = generate_response(user_input.user_input)
    return {"response": response}

# Run the app with: uvicorn <filename>:app --reload
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Use the port environment variable
    uvicorn.run(app, host="0.0.0.0", port=port)