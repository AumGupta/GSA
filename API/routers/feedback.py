# This file defines the API endpoints for handling user feedback on park accessibility and quality.
# It allows users to submit feedback on their experience with green spaces, including their location,
# whether they liked the park, and their scores for various accessibility factors.

# importing necessary libraries
from fastapi import APIRouter
from API.db import get_connection
from pydantic import BaseModel
from datetime import datetime

# Creating the router for feedback endpoints
router = APIRouter(prefix="/feedback", tags=["Feedback"])

# Defining the data model for feedback submission   
class FeedbackRequest(BaseModel):
    lat: float
    lon: float
    liked: bool
    accessibility_score: float 
    proximity_score: float 
    quantity_score: float 
    area_score: float 
    diversity_score: float
    timestamp: datetime

# Endpoint to submit feedback on park accessibility and quality
@router.post("/")
def post_feedback(feedback: FeedbackRequest):

    conn = get_connection()
    cursor = conn.cursor()
    query = """
            INSERT INTO feedback ( 
                lat, 
                lon, 
                liked, 
                accessibility_score, 
                proximity_score, 
                quantity_score, 
                area_score, 
                diversity_score,
                timestamp) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
                RETURNING id;
        """
    cursor.execute(query, (
        feedback.lat, 
        feedback.lon, 
        feedback.liked, 
        feedback.accessibility_score, 
        feedback.proximity_score,
        feedback.quantity_score,
        feedback.area_score,
        feedback.diversity_score,
        feedback.timestamp
    ))

    new_id = cursor.fetchone()[0]
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Feedback submitted successfully", "id": new_id}

