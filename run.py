import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    env = os.environ.get("ENV", "development").lower()
    is_dev = env == "development"

    print("==================================================================")
    print(" Starting Sahaaya AI: Real-Time Stress & Trauma Assessment Platform")
    print(f" Environment: {env.upper()} | Listening on: http://{host}:{port}")
    print(" Triage & Decision-Support System | Public Service Technology")
    print("==================================================================")

    uvicorn.run("app.main:app", host=host, port=port, reload=is_dev)
