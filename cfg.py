import os
import dotenv
import colorama

from logger import game_logger

colorama.just_fix_windows_console()

dotenv.load_dotenv()

PROD = bool(os.getenv('PROD'))
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
JWT_SECRET = os.getenv('JWT_SECRET')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES')










if PROD:
    game_logger.warning('Запуск сервера в PRODUCTION режиме.')
    
else:
    game_logger.warning('Запуск сервера в тестовом режиме.')


