
#Import Dependencies
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import re
from transformers import pipeline
from collections import Counter
from googletrans import Translator
from gtts import gTTS
from IPython.display import Audio
import json
import spacy
import yake

# Load NLP Models
nlp = spacy.load("en_core_web_sm")  # Named Entity Recognition
kw_extractor = yake.KeywordExtractor(lan="en", n=2, top=5)  # Extract top 5 keywords

#Function to Extract Real Topics
def extract_topics(text):
    doc = nlp(text)
    topics = [chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) > 1]  # Extract only meaningful phrases
    return list(set(topics))[:5]  # Limit to top 5

#Function to Scrape 10+ News Articles
def get_news_articles(company_name):
    search_url = f"https://www.bing.com/news/search?q={company_name}+business&FORM=HDRSC6"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    links = set()
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "http" in href and "bing" not in href and "MSN" not in href:  #Exclude spam links
            match = re.search(r'(https?://\S+)', href)
            if match:
                clean_url = match.group(1).split("&")[0]
                links.add(clean_url)
        if len(links) >= 10:
            break

    return list(links)

#Function to Extract Article Data
def extract_article_data(url):
    try:
        article = Article(url)
        article.download()
        article.parse()

        if not article.text.strip():  #Exclude empty articles
            return None

        return {
            "title": article.title or "No Title",
            "summary": article.text[:500] or "No Summary",
            "content": article.text,
            "topics": extract_topics(article.text)  # Extract real topics
        }
    except Exception as e:
        return None

# Load Sentiment Analysis Model
sentiment_pipeline = pipeline("sentiment-analysis")

#Function to Perform Sentiment Analysis
def analyze_sentiment(text):
    result = sentiment_pipeline(text[:512])  # Limit text size for efficiency
    return result[0]["label"]  # Output: 'POSITIVE' or 'NEGATIVE'

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

    unique_topics = {}
    for i, topics in enumerate(all_topics):
        unique_topics[f"Unique Topics in Article {i+1}"] = list(topics - common_topics)

    topic_overlap = {
        "Common Topics": list(common_topics),
        **unique_topics
    }

    return {
        "Sentiment Distribution": sentiment_distribution,
        "Coverage Differences": coverage_differences,
        "Topic Overlap": topic_overlap
    }

#Function to Translate Text to Hindi
def translate_to_hindi(text):
    translator = Translator()
    return translator.translate(text, dest="hi").text

#Function to Generate Hindi TTS
def generate_hindi_tts(text, filename="sentiment_summary.mp3"):
    tts = gTTS(text=text, lang="hi")
    tts.save(filename)
    return filename

#Main Function: Execute Full Pipeline
def generate_news_report():
    company_name = input("Enter the company name: ")  # User Input

    # Step 1: Get News Articles
    news_links = get_news_articles(company_name)

    if not news_links:
        print("No news articles found. Try another company name.")
        return

    # Step 2: Extract Data from Articles
    news_data = []
    for url in news_links:
        article = extract_article_data(url)
        if article:
            article["sentiment"] = analyze_sentiment(article["content"])
            news_data.append(article)

    if not news_data:
        print("No valid articles found! Try another company name.")
        return

    # Step 3: Generate Comparative Sentiment Analysis
    sentiment_analysis = comparative_sentiment_analysis(news_data)

    # Step 4: Generate Final Sentiment Summary
    final_summary = f"{company_name} latest news coverage is mostly {max(sentiment_analysis['Sentiment Distribution'], key=sentiment_analysis['Sentiment Distribution'].get)}."

    # Step 5: Convert Final Sentiment Summary to Hindi and Generate TTS
    hindi_summary = translate_to_hindi(final_summary)
    audio_file = generate_hindi_tts(hindi_summary)

    # Step 6: Create Final JSON Output
    report = {
        "Company": company_name,
        "Articles": [
            {
                "Title": article["title"],
                "Summary": article["summary"],
                "Sentiment": article["sentiment"],
                "Topics": article["topics"]
            }
            for article in news_data
        ],
        "Comparative Sentiment Score": sentiment_analysis,
        "Final Sentiment Analysis": final_summary,
        "Audio": "[Play Hindi Speech]"
    }

    # Print Final JSON Output
    print(json.dumps(report, indent=4, ensure_ascii=False))

    # Play Hindi Speech
    return Audio(audio_file)

#Run the function
generate_news_report()
