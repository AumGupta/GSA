# Main application file for the Green Spaces Accessibility API
# This file initializes the FastAPI application and includes the spatial router.

# Importing necessary libraries
from fastapi import FastAPI
from API.routers import accessibility, spatial

# Creating the FastAPI app
app = FastAPI(title="Green Spaces Accessibility API")

# Root endpoint
@app.get("/")
def root():
    return {"message": "API is running"}

# Conetion with the spatial router
app.include_router(spatial.router, prefix="/api/v1")
app.include_router(accessibility.router, prefix="/api/v1")