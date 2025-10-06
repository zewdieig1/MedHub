"""
Project - Backend
Rosa Solis
MEDHUB
Software Engineering
9/26/25
"""
from fastapi import FastAPI, Response, Cookie, HTTPException
from fastapi.responses import HTMLResponse
import html

app = FastAPI(title="MedHub Web Scraping API", version="0.1")

# --- existing endpoints like /health can stay above or below --- #
@app.get("/health")
def health():
    return {"status": "ok"}

# ----------------- simple login / logout for dev team ----------------- #
@app.get("/login")
def login(email: str, response: Response):
    """
    Dev-only login: sets a cookie so the browser can access protected pages.
    Usage: /login?email=you@example.com
    """
    if "@" not in email or "." not in email:
        raise HTTPException(status_code=400, detail="Please provide a valid email")
    # Set a basic cookie. (For real auth, use proper sessions + hashing.)
    response.set_cookie(
        key="demo_user",
        value=email,
        httponly=True,   # JS can't read it
        samesite="lax",  # OK for most simple flows
        # secure=True,   # uncomment when using HTTPS
        max_age=60*60*8  # 8 hours
    )
    return {"ok": True, "message": f"Logged in as {email}"}

@app.post("/logout")
def logout(response: Response):
    """Clear the cookie."""
    response.delete_cookie("demo_user")
    return {"ok": True, "message": "Logged out"}

# --------------------- auth helper (dev) ------------------------- #
def require_user(demo_user: str | None):
    if not demo_user:
        raise HTTPException(status_code=401, detail="Please log in at /login?email=you@example.com")
    return demo_user

# ---------------------- HOME PAGE (HTML) ------------------------- #
@app.get("/", response_class=HTMLResponse)
def home(demo_user: str | None = Cookie(default=None)):
    if not demo_user:
        raise HTTPException(status_code=401, detail="Please log in first at /login?email=you@example.com")

    safe_user = html.escape(demo_user)
    return f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>MedHub</title>
      <style>
        body {{
          margin: 0; font-family: Arial, sans-serif; background: #f7fafc;
        }}
        header {{
          background: #2b6cb0; color: white; padding: 1rem;
          font-size: 2.5rem; font-weight: bold; text-align: center;
        }}
        main {{
          max-width: 700px; margin: 2rem auto; padding: 1rem;
          background: white; border-radius: 10px;
          box-shadow: 0 2px 8px rgba(0,0,0,.1);
          text-align: center;
        }}
        a.button {{
          display: inline-block; margin: .5rem; padding: .6rem 1rem;
          background: #2b6cb0; color: white; border-radius: 6px;
          text-decoration: none;
        }}
      </style>
    </head>
    <body>
      <header>MedHub</header>
      <main>
        <h2>Welcome, {safe_user}!</h2>
        <p>Select a tool:</p>
        <a class="button" href="/docs" target="_blank">API Docs</a>
        <a class="button" href="/plans">View Plans</a>
        <form action="/logout" method="post" style="margin-top:1rem;">
          <button type="submit">Log out</button>
        </form>
      </main>
    </body>
    </html>
    """


