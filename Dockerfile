FROM python:3.11-slim

# create app dir
WORKDIR /app

# install build deps and pip dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy app
COPY app /app

# set environment defaults (override in hosting env)
ENV PYTHONUNBUFFERED=1

# run the bot
CMD ["python", "discord_bot.py"]
