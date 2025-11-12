<<<<<<< HEAD
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GMAIL_USER = os.getenv('GMAIL_USER', 'consular.services.infos@gmail.com')
    GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', 'Adam23031979*')
=======
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GMAIL_USER = os.getenv('GMAIL_USER', 'consular.services.infos@gmail.com')
    GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', 'Adam23031979*')
>>>>>>> ba3058378dee71b1a95fe6c4ef390310c261661d
    SECRET_KEY = os.getenv('SECRET_KEY', 'votre_cle_secrete_api_2024')