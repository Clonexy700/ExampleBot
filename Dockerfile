FROM python:3

WORKDIR /app

COPY . .

RUN python3 -m pip install -U nextcord.py python-dotenv

CMD python -u ./client.py