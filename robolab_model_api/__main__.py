import uvicorn

if __name__ == "__main__":
    uvicorn.run("robolab_model_api.server:app", host="0.0.0.0", port=int(__import__("os").getenv("PORT", "8080")))
