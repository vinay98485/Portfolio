import uvicorn

if __name__ == "__main__":
    # Start the FastAPI application using uvicorn
    # host 0.0.0.0 makes it accessible over the local network
    # reload=True automatically restarts the server when code changes
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
