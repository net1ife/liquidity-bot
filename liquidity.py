import requests
from textblob import TextBlob
from nltk.tokenize import word_tokenize
from nltk.classify import NaiveBayesClassifier
from nltk.probability import FreqDist

# Constants
NEWSAPI_KEY = "YOUR_NEWSAPI_KEY"
NEWSAPI_ENDPOINT = "https://newsapi.org/v2/everything"

def fetch_articles(ticker):
    """Fetches news articles for a given stock ticker."""
    query = f"{ticker} stock"
    params = {
        'q': query,
        'apiKey': NEWSAPI_KEY,
        'language': 'en',
        'sortBy': 'relevancy',
        'pageSize': 100
    }

    response = requests.get(NEWSAPI_ENDPOINT, params=params)
    response.raise_for_status()  # Raise exception for any response errors

    articles = response.json().get('articles', [])
    return [article['description'] or article['title'] for article in articles if article['description'] or article['title']]

def get_sentiment(text):
    """Returns the sentiment of a text based on its polarity."""
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0.1:
        return 'positive'
    elif analysis.sentiment.polarity < -0.1:
        return 'negative'
    else:
        return 'neutral'

def get_word_features(documents, num_features=2000):
    """Returns top n word features."""
    all_words = FreqDist(w.lower() for words, _ in documents for w in words)
    return list(all_words.keys())[:num_features]

def document_features(document, word_features):
    """Generate features for a document."""
    document_words = set(document)
    return {f'contains({word})': (word in document_words) for word in word_features}

def main():
    # Fetch articles for a ticker
    ticker = input("Enter the stock ticker for which you want to fetch news articles: ")

    try:
        articles = fetch_articles(ticker)

        # Auto-label the first N articles using TextBlob
        N = 10
        print("\nAuto-labeling the first few articles using TextBlob:")
        documents = [(word_tokenize(article), get_sentiment(article)) for article in articles[:N]]

        word_features = get_word_features(documents)
        featuresets = [(document_features(d, word_features), c) for (d, c) in documents]
        classifier = NaiveBayesClassifier.train(featuresets)

        # Analyze the remaining articles
        for article in articles[N:]:
            words = word_tokenize(article)
            sentiment = classifier.classify(document_features(words, word_features))
            print(f"\nArticle: {article}\nPredicted Sentiment: {sentiment}\n{'-' * 50}")

    except requests.RequestException as e:
        print(f"Error fetching news: {e}")

if __name__ == "__main__":
    main()
