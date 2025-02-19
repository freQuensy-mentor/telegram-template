import os
from dotenv import load_dotenv

load_dotenv()

PGPASSWORD = os.environ["PGPASSWORD"]  # Обязательное поле
PGUSER = os.environ["PGUSER"]
PGDATABASE = os.environ["PGDATABASE"]
PGHOST = os.environ["PGHOST"]

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]

# Так задаются не обязательные, будут None если значение не найдется
MIXPANEL_TOKEN = os.getenv("MIXPANEL_TOKEN")
