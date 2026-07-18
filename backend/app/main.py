from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI-Powered Code Review Assistant API",
    description="API for ingesting repositories, managing vector search, and generating code reviews using Gemini.",
    version="1.0.0",
)

# Configure CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Default Vite port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 
@app.get("/health")
async def health_check():
    return {"status": "ok"}
