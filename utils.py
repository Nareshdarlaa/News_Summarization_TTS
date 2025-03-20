import spacy
import yake
from transformers import pipeline
from collections import Counter
from googletrans import Translator
from gtts import gTTS
from IPython.display import Audio

#Load NLP Models
nlp = spacy.load("en_core_web_sm")
kw_extractor = yake.KeywordExtractor(lan="en", n=2, top=5)

#Function to Extract Topics
def extract_topics(text):
    doc = nlp(text)
    topics = [chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) > 1]
    return list(set(topics))[:5]

# Load Sentiment Analysis Model
sentiment_pipeline = pipeline("sentiment-analysis")

# Function to Perform Sentiment Analysis
def analyze_sentiment(text):
    result = sentiment_pipeline(text[:512])
    return result[0]["label"]

#Function to Perform Comparative Sentiment Analysis
def comparative_sentiment_analysis(news_data):
    sentiments = [article["sentiment"] for article in news_data]
    sentiment_counts = Counter(sentiments)

    sentiment_distribution = {
        "Positive": sentiment_counts.get("POSITIVE", 0),
        "Negative": sentiment_counts.get("NEGATIVE", 0),
        "Neutral": sentiment_counts.get("NEUTRAL", 0)
    }

    coverage_differences = []
    for i in range(len(news_data) - 1):
        coverage_differences.append({
            "Comparison": f"Article {i+1} discusses '{news_data[i]['title']}', while Article {i+2} discusses '{news_data[i+1]['title']}'.",
            "Impact": f"The first article focuses on {news_data[i]['topics']}, whereas the second article focuses on {news_data[i+1]['topics']}."
        })

    all_topics = [set(article["topics"]) for article in news_data]
    common_topics = set.intersection(*all_topics) if all_topics else set()

    unique_topics = {f"Unique Topics in Article {i+1}": list(topics - common_topics) for i, topics in enumerate(all_topics)}

    topic_overlap = {"Common Topics": list(common_topics), **unique_topics}

    return {
        "Sentiment Distribution": sentiment_distribution,
        "Coverage Differences": coverage_differences,
        "Topic Overlap": topic_overlap
    }

#Function to Translate Text to Hindi
def translate_to_hindi(text):
    translator = Translator()
    return translator.translate(text, dest="hi").text

# Function to Generate Hindi TTS
def generate_hindi_tts(text, filename="sentiment_summary.mp3"):
    tts = gTTS(text=text, lang="hi")
    tts.save(filename)
    return filename
