import requests
import auth
from twilio.rest import Client

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

parameters = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": "TSLA",
    "apikey": auth.STOCK_API_KEY,
}
response = requests.get(url=STOCK_ENDPOINT, params=parameters)
response.raise_for_status()

stock_data = response.json()["Time Series (Daily)"]

keys = [day for day, info in stock_data.items()]
yesterday_price = float(stock_data[f"{keys[0]}"]["4. close"])
today_price = float(stock_data[f"{keys[1]}"]["4. close"])

five_pct_difference = False

difference_price = yesterday_price - today_price
difference_price_pct = (abs(difference_price) / ((yesterday_price + today_price) / 2)) * 100
if difference_price_pct >= 5:
    five_pct_difference = True

parameters_news = {
    "apiKey": auth.NEWS_API_KEY,
    "q": COMPANY_NAME,
    "language": "en",
}
response = requests.get(url=NEWS_ENDPOINT, params=parameters_news)
response.raise_for_status()

news_data = response.json()

if five_pct_difference:
    top_news = [article for article in news_data["articles"][:3]]
    news_article = ""
    for article in top_news:
        news_article += "".join(f"Headline: {article['title']}\n"
                                f"Brief: {article['description']}\n\n")

    client = Client(auth.account_sid, auth.auth_token)

    if difference_price > 0:
        message = client.messages \
            .create(
            body=f"{COMPANY_NAME}: UP {difference_price_pct} %\n"
                 f"{news_article}",
            from_=auth.twilio_phone,
            to=auth.receiver_phone
        )

    elif difference_price < 0:
        message = client.messages \
            .create(
            body=f"{COMPANY_NAME}: DOWN {difference_price_pct} %\n"
                 f"{news_article}",
            from_=auth.twilio_phone,
            to=auth.receiver_phone
        )
