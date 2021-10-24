import asyncio
from typing import Optional
from fastapi import FastAPI
import uvicorn

from fs import mount

app = FastAPI()

@app.get("/")
async def root_check():
    return {"code": 0}

@app.get("/health")
async def health_check():
    return {"code": 0}

@app.get("/job/{job_id}")
async def get_job(job_id: int, q: Optional[str] = None):
    return {"job": job_id, "q": q}

def main():
    mount()
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    main()