from fastapi import FastAPI
from news_summarization import generate_news_report

app = FastAPI()

#API Endpoint for News Summarization
@app.get("/analyze")
def analyze(company: str):
    return generate_news_report(company)
