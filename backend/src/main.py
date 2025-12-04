from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api.endpoints import router
from .api.tree_routes import router as tree_router
from .cores.config import settings
from pathlib import Path
import time

# Clear all logs on server startup
def clear_all_logs():
    """Clear all log files when server starts"""
    backend_dir = Path(__file__).parent.parent
    
    # Clear component-testing logs
    component_log_dir = backend_dir / "logs" / "component-testing"
    if component_log_dir.exists():
        for log_file in component_log_dir.glob("*.log"):
            with open(log_file, 'w') as f:
                f.write(f"{'='*80}\n")
                f.write(f"{log_file.stem} LOG\n")
                f.write(f"Server Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n\n")
    
    # Clear component-testing-full logs
    component_full_log_dir = backend_dir / "logs" / "component-testing-full"
    if component_full_log_dir.exists():
        for log_file in component_full_log_dir.glob("*.log"):
            with open(log_file, 'w') as f:
                f.write(f"{'='*80}\n")
                f.write(f"{log_file.stem} LOG\n")
                f.write(f"Server Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n\n")
    
    print("✅ All logs cleared on server startup")

# Clear logs before app initialization
clear_all_logs()

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")
app.include_router(tree_router, prefix="/api")  # Tree visualization routes

# Mount static files for tree visualization
backend_dir = Path(__file__).parent.parent
logs_dir = backend_dir / "logs"
app.mount("/logs", StaticFiles(directory=str(logs_dir)), name="logs")

# Mount dataset logs for metrics visualization
dataset_logs_dir = backend_dir / "dataset" / "logs"
app.mount("/dataset-logs", StaticFiles(directory=str(dataset_logs_dir)), name="dataset-logs")

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.app_name} v{settings.version}"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.version}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host=settings.host, port=settings.port, reload=True)  