from fastapi import FastAPI
from api import api_router
import os
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=os.getenv("HOST"), port=5555)
