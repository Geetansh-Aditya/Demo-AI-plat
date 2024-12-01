from fastapi import FastAPI, HTTPException, Request
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from dotenv import load_dotenv
import logging
import uvicorn
import os
from langchain_groq import ChatGroq
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

# Load environment variables
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
# api_key = os.getenv("GROQ_API_KEY")  # Load API key securely

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Coding Question and Solution API",
    version="1.0",
    description="An API for generating coding questions, solutions, and test cases."
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Groq model
llm = ChatGroq(model="llama-3.1-70b-versatile", api_key="Your API KEY")

# Define prompts
prompts = {
    "question": ChatPromptTemplate.from_messages([
    ("system", "Generate exactly 1 coding question inspired by real-life scenarios on the topic: arrays and difficulty level: {difficulty}. Each question should start on a new line without any introductory or concluding text. Just the questions. Also generate the title for the generated question. Return the content in the JSON format like this: '{{\"title\": \"question_title\", \"question\": \"question\"}}'. No extras needed, only give the JSON output.")
    ]),

    "solution": ChatPromptTemplate.from_messages([
        ("system", "Generate the solution for the coding question in C language. Question: {question}. Difficulty level: {difficulty} and also explain the code by taking small code snippets and code examples and real-life examples.")
    ]),
    "convo": ChatPromptTemplate.from_messages([
        ("system", "You are a computer science assistant professor. Reply to all the student education-related queries {query}.")
    ]),
    "code_check": ChatPromptTemplate.from_messages([
        ("system", "You are a computer science assistant professor. Check the code {code} given to you by the user is correct or not.")
    ]),
    "test_case": ChatPromptTemplate.from_messages([
        ("system", "Create exactly 10 unique test cases for this coding question: {question}. Each test case should be formatted as follows:\n\n"
                   "Input: <array of integers>, Target: <target integer> | Output: <indices or values that satisfy the condition>\n\n"
                   "Return only the 10 test cases without extra text.")
    ]),
    "ques_gen" : ChatPromptTemplate.from_messages([
        ("system", "Generate a topic to generate question for coding questions. Reply in one word and not more than one.")
    ])
}

# Request models
class QuestionRequest(BaseModel):
    topic: str
    difficulty: str


class SolutionRequest(BaseModel):
    question: str
    difficulty: str


class QueryRequest(BaseModel):
    query: str


class CodeCheckRequest(BaseModel):
    code: str


class TestCaseRequest(BaseModel):
    question: str


# Endpoint to generate coding questions
@app.post("/generate_questions")
async def generate_questions(request: QuestionRequest):
    try:
        formatted_prompt = prompts["question"].format_prompt(topic=request.topic, difficulty=request.difficulty)
        response = llm.invoke(formatted_prompt.to_messages())
        return {"questions": response}
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")


# Endpoint to generate solution and explanation
@app.post("/generate_solution")
async def generate_solution(request: SolutionRequest):
    try:
        formatted_prompt = prompts["solution"].format_prompt(question=request.question, difficulty=request.difficulty)
        response = llm.invoke(formatted_prompt.to_messages())
        return {"solution": response}
    except Exception as e:
        logger.error(f"Error generating solution: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating solution: {str(e)}")


# Endpoint for educational query conversation
@app.post("/generate_convo")
async def generate_convo(request: QueryRequest):
    try:
        formatted_prompt = prompts["convo"].format_prompt(query=request.query)
        response = llm.invoke(formatted_prompt.to_messages())
        return {"response": response}
    except Exception as e:
        logger.error(f"Error generating conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating conversation: {str(e)}")


# Endpoint to check if the code is correct
@app.post("/check_code")
async def check_code(request: CodeCheckRequest):
    try:
        formatted_prompt = prompts["code_check"].format_prompt(code=request.code)
        response = llm.invoke(formatted_prompt.to_messages())
        return {"code_check": response}
    except Exception as e:
        logger.error(f"Error checking code: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking code: {str(e)}")


# Endpoint to generate test cases
# @app.post("/generate_test_cases")
# async def generate_test_cases(request: TestCaseRequest):
#     try:
#         formatted_prompt = prompts["test_case"].format_prompt(question=request.question)
#         response = llm.invoke(formatted_prompt.to_messages())
#         return {"test_cases": response}
#     except Exception as e:
#         logger.error(f"Error generating test cases: {e}")
#         raise HTTPException(status_code=500, detail=f"Error generating test cases: {str(e)}")
@app.post("/generate_test_cases")
async def generate_test_cases(request: TestCaseRequest):
    try:
        formatted_prompt = prompts["test_case"].format_prompt(question=request.question)
        response = llm.invoke(formatted_prompt.to_messages())

        # Parse response into structured test cases
        raw_test_cases = response.split("\n")  # Assuming each test case is on a new line
        test_cases = []
        for raw_case in raw_test_cases:
            try:
                # Extract input and output using a known format
                parts = raw_case.split("|")
                input_part = parts[0].strip().replace("Input:", "").strip()
                expected_output = parts[1].strip().replace("Output:", "").strip()
                test_cases.append({
                    "input": json.loads(input_part),
                    "expected_output": json.loads(expected_output)
                })
            except (IndexError, json.JSONDecodeError):
                logger.warning(f"Skipping malformed test case: {raw_case}")

        return {"test_cases": test_cases}
    except Exception as e:
        logger.error(f"Error generating test cases: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating test cases: {str(e)}")


# Endpoint to generate a topic for coding questions
@app.post("/gues_gen")
async def generate_topic():
    try:
        formatted_prompt = prompts["ques_gen"].format_prompt()
        response = llm.invoke(formatted_prompt.to_messages())
        return {"topic": response}
    except Exception as e:
        logger.error(f"Error generating topic: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating topic: {str(e)}")


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request URL: {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


# Run the FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
