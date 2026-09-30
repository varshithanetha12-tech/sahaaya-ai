import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    env = os.environ.get("ENV", "production").lower()
    is_dev = env == "development"
    uvicorn.run("app.main:app", host=host, port=port, reload=is_dev)
