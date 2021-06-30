from textblob import TextBlob
'''
TextBlob is a Python (2 and 3) library for processing textual data. It provides a simple API 
for diving into common natural language processing (NLP) tasks such as part-of-speech tagging,
noun phrase extraction, sentiment analysis, classification, translation, and more.
'''


class SentimentAnalysis:

    def analize_sentiment(self, text):

        # print(text)

        analysis = TextBlob(text)
        # print(analysis.sentiment.polarity)
        if analysis.sentiment.polarity > 0:
            # sentiment = print("positive : 1")
            # return sentiment
            return 1

        elif analysis.sentiment.polarity == 0:
            # sentiment = print("neutral : 0")
            # return sentiment
            return 0
        else:
            # sentiment = print("negative : -1")
            # return sentiment
            return -1
