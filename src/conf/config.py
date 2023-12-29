from pydantic.v1 import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.environ.get('DB_URL')
    MAIL_USERNAME: str = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD: str = os.environ.get('MAIL_PASSWORD')
    MAIL_FROM: str = os.environ.get('MAIL_FROM')
    MAIL_PORT: int = int(os.environ.get('MAIL_PORT'))
    MAIL_SERVER: str = os.environ.get('MAIL_SERVER')
    CLD_NAME: str = os.environ.get('CLD_NAME')
    CLD_API_KEY: int = int(os.environ.get('CLD_API_KEY'))
    CLD_API_SECRET: str = os.environ.get('CLD_API_SECRET')

config = Settings()
