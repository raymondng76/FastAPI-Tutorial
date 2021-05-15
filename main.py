from fastapi import FastAPI

# FastAPI object instance
app = FastAPI()

# Root end point
@app.get("/")
async def root():
    return {"message": "Hello World"}

