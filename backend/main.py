from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from configuration.config import settings
from database import models
from database.db_config import engine, SessionLocal
from routers import auth, admin, users

# Ensure database tables are created
models.Base.metadata.create_all(bind=engine)

# Lifespan Event (Manages DB Connections)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI application starting...")
    yield
    print("FastAPI application shutting down...")
    # Ensure DB session cleanup
    SessionLocal().close()

# Create FastAPI App
app = FastAPI(lifespan=lifespan)

# CORS
cors_origins = settings.CORS_ORIGINS
if isinstance(cors_origins, str):
    cors_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
# Fallback to allow all in dev if not provided
allow_all = not cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=[] if allow_all else cors_origins,
    allow_origin_regex=".*" if allow_all else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Root Route
@app.get("/")
def root():
    return {"message": "Welcome to our Blockchain application!"}

# Register API Routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


