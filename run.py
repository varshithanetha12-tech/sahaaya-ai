import uvicorn

if __name__ == "__main__":
    print("==================================================================")
    print(" Starting Sahaaya AI: Real-Time Stress & Trauma Assessment Platform")
    print(" Triage & Decision-Support System | Public Service Technology")
    print(" Access URL: http://127.0.0.1:8000")
    print("==================================================================")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
