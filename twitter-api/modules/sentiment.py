from textblob import TextBlob


class Sentiment_analysis:

    def analize_sentiment(self,text):

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