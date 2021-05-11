FROM python:3.8.7-slim-buster

COPY config.py /bot/
COPY games.py /bot/
COPY tweepy_nba_bot.py /bot/
COPY games_today.csv /bot/
COPY requirements.txt /tmp
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt

WORKDIR /bot
CMD ["python", "tweepy_nba_bot.py"]