from fastapi import FastAPI
from API.routers import spatial

app = FastAPI(title="Green Areas API")

@app.get("/")
def root():
    return {"message": "API is running"}

# aquí conectamos el router
app.include_router(spatial.router, prefix="/api/v1")