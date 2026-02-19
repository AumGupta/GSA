# Main application file for the Green Spaces Accessibility API
# This file initializes the FastAPI application and includes the spatial router.

# Importing necessary libraries
from fastapi import FastAPI
from API.routers import accessibility, routing, spatial
from fastapi.middleware.cors import CORSMiddleware


# Creating the FastAPI app
app = FastAPI(title="Green Spaces Accessibility API")

origins = ["*"]   # allow everyone for now

# Adding CORS middleware to allow cross-origin requests 
# REMEMBER TO CHANGE THIS IN PRODUCTION!!!!!!!!
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def root():
    return {"message": "API is running"}

# Conetion with the spatial router
app.include_router(spatial.router, prefix="/api/v1")
app.include_router(accessibility.router, prefix="/api/v1")
app.include_router(routing.router, prefix="/api/v1/routing")