import requests

class SentimentService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = 'https://api.meaningcloud.com/sentiment-2.1'

    def analyze(self, text, lang='en', model='general'):
        params = {
            'key': self.api_key,
            'txt': text,
            'lang': lang,
            'model': model
        }
        response = requests.get(self.url, params=params)
        response_data = response.json()
        return self.extract_sentiment_data(response_data)

    @staticmethod
    def extract_sentiment_data(response_data):
        keys = ['score_tag', 'agreement', 'subjectivity', 'confidence']
        return {key: response_data.get(key) for key in keys}
