Installation & Setup

1. Clone the Repository
2. Install Dependencies
Run the following command to install all required libraries:
3. Run the Project in Google Colab
   
Open Google Colab

Upload news_summarization_tts.ipynb
Run all cells
Usage Instructions
Run the Script
You will be prompted to enter a company name.
The system will extract relevant news, analyze sentiment, and generate Hindi speech.
Example Output (JSON Format)

Model Details

1. News Scraping
Tool: BeautifulSoup
Source: Bing News
Filter: Extracts 10+ business-related articles, removes irrelevant news (e.g., celebrity content).
2. Sentiment Analysis
Model: distilbert-base-uncased-finetuned-sst-2-english
Library: transformers (Hugging Face)
Output: POSITIVE, NEGATIVE, NEUTRAL
3. Topic Extraction
Tool: spaCy + yake
Method: Extracts noun phrases and key phrases from article content.
4. Text-to-Speech (TTS) in Hindi
Tool: gTTS (Google Text-to-Speech)
Output: Hindi MP3 file

API Usage

The project does not currently expose an API but can be extended using FastAPI or Flask.
To integrate with an API, structure the generate_news_report() function as an endpoint.
