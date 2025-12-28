import os

import colorama
import dotenv

from logger import GLOG

colorama.just_fix_windows_console()

dotenv.load_dotenv()

PROD = bool(os.getenv('PROD'))

JWT_SECRET = os.getenv('JWT_SECRET', 'secret')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '10'))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES', '1440'))

if PROD:
    GLOG.warning('Запуск сервера в PRODUCTION режиме.')
    
else:
    GLOG.warning('Запуск сервера в тестовом режиме.')


