"""
Cynergy Studio Server
"""
from cynergy.studio.api.workflow_api import create_app
import uvicorn


def main():
    app = create_app()
    print("🚀 Starting Cynergy Studio Server...")
    print("Access the API at: http://localhost:8000")
    print("Studio UI will be available at: http://localhost:3000 (when frontend is served)")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()