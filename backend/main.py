from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import traceback

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Smart Tutor API",
    description="An AI-powered learning platform for all subjects",
    version="1.0.0"
)

# Get allowed origins from environment or use defaults
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = allowed_origins_env.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Securely load and validate API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Get model configuration from environment variables
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.7"))

try:
    client = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=DEFAULT_MODEL,
        temperature=MODEL_TEMPERATURE,
    )
except Exception as e:
    print(f"Error initializing OpenAI client: {str(e)}")
    raise ValueError(f"Failed to initialize OpenAI client: {str(e)}")

# Subject-specific prompts
subject_prompts = {
    "technology": "technology and computer science",
    "science": "science and scientific concepts",
    "mathematics": "mathematics and mathematical concepts",
    "languages": "languages and linguistics",
    "arts": "arts and literature",
    "history": "history and historical events",
    "business": "business and economics",
    "health": "health and medicine",
    "other": "general knowledge",
}

# Prompt Template
prompt = PromptTemplate(
    input_variables=["user_input", "subject"],
    template="""
    You are a knowledgeable and engaging tutor specializing in {subject}. Your goal is to help students learn and understand concepts effectively.
    
    When teaching:
    1. Use clear, concise explanations
    2. Provide relevant examples
    3. Break down complex topics into manageable parts
    4. Encourage critical thinking
    5. Adapt your teaching style to the student's needs
    
    Current question:
    {user_input}
    
    Please provide a helpful and informative response:
    """
)

# Initialize the tutor chain
tutor = LLMChain(
    llm=client, 
    prompt=prompt,
    verbose=True
)

# Learning style prompts
prompts = {
    "explanation": lambda topic, subject: f"""
        Provide a detailed explanation of '{topic}' in the context of {subject_prompts[subject]}.
        Include:
        - Clear definitions
        - Key concepts
        - Real-world applications
        - Common misconceptions
        Use analogies and examples to make the explanation more relatable.
    """,
    
    "study_notes": lambda topic, subject: f"""
        Create comprehensive study notes for '{topic}' in {subject_prompts[subject]}.
        Include:
        - Main concepts and definitions
        - Key points in bullet form
        - Important relationships and connections
        - Summary diagrams or flowcharts (described in text)
        - Review questions
    """,
    
    "quiz": lambda topic, subject: f"""
        Generate an engaging 5-question multiple-choice quiz about '{topic}' in {subject_prompts[subject]}.
        For each question:
        - Make it challenging but fair
        - Provide 4 options (A, B, C, D)
        - Include one correct answer
        - Explain why each answer is correct or incorrect
        Format: Number each question and mark correct answers with **Correct Answer: X**
    """,
    
    "examples": lambda topic, subject: f"""
        Provide practical examples and exercises related to '{topic}' in {subject_prompts[subject]}.
        Include:
        - 3-4 detailed examples with explanations
        - Practice problems with solutions
        - Real-world applications
        - Tips for understanding similar problems
    """,
    
    "hands_on": lambda topic, subject: f"""
        Create an interactive exercise about '{topic}' in {subject_prompts[subject]}.
        Include:
        - Step-by-step instructions
        - Materials or tools needed
        - Expected outcomes
        - Common mistakes to avoid
        - Tips for success
    """,
    
    "learning_path": lambda topic, subject: f"""
        Design a structured learning path for mastering '{topic}' in {subject_prompts[subject]}.
        Include:
        - Prerequisites
        - Learning objectives
        - Step-by-step progression
        - Recommended resources
        - Milestones and checkpoints
        - Estimated time commitments
    """,
    
    "visualization": lambda topic, subject: f"""
        Create a detailed text description of visual aids to understand '{topic}' in {subject_prompts[subject]}.
        Include:
        - Diagrams (described in text)
        - Charts or graphs (described in text)
        - Visual analogies
        - Step-by-step visual breakdowns
        - Color and spatial relationships
    """,
    
    "custom": lambda question, subject: f"""
        Answer this specific question about {subject_prompts[subject]}:
        '{question}'
        Provide:
        - Direct answer
        - Supporting explanation
        - Examples if relevant
        - Additional context
    """
}

class RequestData(BaseModel):
    topic: str = "(Optional)"
    subject: str = "technology"
    query_type: str = "(Optional)"
    custom_question: str = ""

def process_query(topic: str, subject: str, query_type: str, custom_question: str) -> str:
    # Input validation and sanitization
    topic_val = topic if topic != "(Optional)" else None
    query_val = query_type if query_type != "(Optional)" else None
    subject_val = subject if subject in subject_prompts else "other"
    user_input = custom_question.strip()

    # Validate required inputs
    if not user_input and not (topic_val and query_val):
        raise HTTPException(
            status_code=400,
            detail="Please provide either a custom question or select both a topic and a query type."
        )

    try:
        # Input validation for query type
        if query_val and query_val not in prompts:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid query type. Available types: {list(prompts.keys())}"
            )
            
        # Construct appropriate prompt based on inputs
        if user_input and query_val and topic_val:
            system_prompt = prompts[query_val](topic_val, subject_val)
            full_prompt = f"{system_prompt}\n\nAlso consider this specific question: '{user_input}'"
        elif query_val and topic_val:
            full_prompt = prompts[query_val](topic_val, subject_val)
        else:
            full_prompt = prompts["custom"](user_input, subject_val)

        # Add a timeout to prevent hanging requests
        try:
            # Use the tutor chain with timeout handling
            response = tutor.invoke({
                "user_input": full_prompt,
                "subject": subject_prompts[subject_val]
            }, timeout=30)  # 30 second timeout
            
            return response["text"]
        except TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="Request timed out. Please try again with a simpler query."
            )
    except Exception as e:
        print(f"Error in process_query: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/api/query")
async def handle_query(request_data: RequestData):
    try:
        # Rate limiting can be added here
        
        # Process the query
        result = process_query(
            topic=request_data.topic,
            subject=request_data.subject,
            query_type=request_data.query_type,
            custom_question=request_data.custom_question
        )
        
        # Return successful response
        return JSONResponse(
            content={"result": result, "status": "success"},
            status_code=200
        )
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        # Log the full error for debugging
        print(f"Error in handle_query: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail="Unexpected error occurred. Please try again later."
        )

@app.get("/api/test")
async def test_api():
    return {"status": "ok", "message": "API is reachable"}

@app.get("/")
async def read_root():
    environment = os.getenv("ENVIRONMENT", "development")
    return {
        "status": "online",
        "version": "1.0.0",
        "message": "Smart Tutor API is running",
        "docs": "/docs",
        "endpoints": {
            "query": "/api/query",
            "test": "/api/test"
        },
        "environment": environment,
        "health": "OK",
        "model": DEFAULT_MODEL
    }