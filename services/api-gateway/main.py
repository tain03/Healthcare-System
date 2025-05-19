from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="Healthcare API Gateway")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
CORE_SERVICE_URL = os.getenv("CORE_SERVICE_URL", "http://core-service:8000")
CHAT_SERVICE_URL = os.getenv("CHAT_SERVICE_URL", "http://chat-service:8001")

# HTTP client
http_client = httpx.AsyncClient()

@app.get("/")
def read_root():
    return {"message": "Welcome to Healthcare API Gateway"}

# User endpoints
@app.post("/users/")
async def create_user(user: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{CORE_SERVICE_URL}/users/", json=user)
        return response.json()

@app.get("/users/")
async def get_users(skip: int = 0, limit: int = 100):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CORE_SERVICE_URL}/users/?skip={skip}&limit={limit}")
        return response.json()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CORE_SERVICE_URL}/users/{user_id}")
        return response.json()

# Appointment endpoints
@app.post("/appointments/")
async def create_appointment(appointment: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{CORE_SERVICE_URL}/appointments/", json=appointment)
        return response.json()

@app.get("/appointments/")
async def get_appointments(skip: int = 0, limit: int = 100):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CORE_SERVICE_URL}/appointments/?skip={skip}&limit={limit}")
        return response.json()

@app.get("/appointments/{appointment_id}")
async def get_appointment(appointment_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CORE_SERVICE_URL}/appointments/{appointment_id}")
        return response.json()

# Chat endpoints
@app.post("/chat/")
async def create_chat_message(chat: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{CHAT_SERVICE_URL}/chat/", json=chat)
        return response.json()

@app.get("/chat/{user_id}")
async def get_chat_history(user_id: int, skip: int = 0, limit: int = 100):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CHAT_SERVICE_URL}/chat/{user_id}?skip={skip}&limit={limit}")
        return response.json()

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose() 