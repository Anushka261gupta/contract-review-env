# server/main.py
import uvicorn

def serve():
    """Entry point for OpenEnv multi-mode deployment."""
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=7860,
        reload=False,
    )

if __name__ == "__main__":
    serve()
