"""
PhishGuard - FastAPI Application
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils.analyzer import analyze_message

app = FastAPI(title="PhishGuard", description="AI-Powered Email & Message Quality Analyzer")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "An internal server error occurred.", "details": str(exc)}
    )

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/analyzer", response_class=HTMLResponse)
async def analyzer_page(request: Request):
    return templates.TemplateResponse("analyzer.html", {"request": request})


@app.post("/api/analyze")
async def analyze(request: Request):
    body = await request.json()
    text = body.get("text", "").strip()

    if not text:
        return JSONResponse(
            status_code=422,
            content={"error": "Please provide some text to analyze."}
        )

    if len(text) > 10000:
        return JSONResponse(
            status_code=422,
            content={"error": "Text is too long. Please limit to 10,000 characters."}
        )

    result = analyze_message(text)
    return JSONResponse(content=result)
