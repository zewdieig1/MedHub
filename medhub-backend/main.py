
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend (React) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary user database
users_db = {
    "test@example.com": "password123",
    "admin@medhub.com": "adminpass"
}

# Login request body
class LoginRequest(BaseModel):
    email: str
    password: str

@app.get("/")
def home():
    return {"message": "MedHub backend is running 🚀"}

@app.post("/login")
def login_user(data: LoginRequest):
    email = data.email
    password = data.password

    if email not in users_db or users_db[email] != password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"message": "Login successful!"}
