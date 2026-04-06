# server/main.py
import uvicorn
from server.app import app   
def main():
    """Entry point for OpenEnv multi-mode deployment."""
    uvicorn.run(
        app,               
        host="0.0.0.0",
        port=7860,
        reload=False,
    )

if __name__ == "__main__":
    main()