#To start the FastAPI server, run: uvicorn api:app --reload
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import json
import traceback
import numpy as np
from main import kickoff

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class CrewAIRequest(BaseModel):
    survey_data: List[Dict]

@app.post("/run-analysis/")
async def run_analysis(request: CrewAIRequest):
    try:
        # Ensure no NaN or Infinity values in the received data
        cleaned_data = json.loads(json.dumps(request.survey_data, allow_nan=False))

        # Call the CrewAI flow with properly formatted survey data
        result = kickoff(json.dumps(cleaned_data))  # Convert to JSON string for processing
        return {"result": result}
    except ValueError as ve:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="Invalid data: contains NaN or Infinity values.")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
