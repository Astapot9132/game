import os

import colorama
import dotenv

from logger import GLOG

colorama.just_fix_windows_console()

dotenv.load_dotenv()

PROD = bool(os.getenv('PROD'))

JWT_SECRET = os.getenv('JWT_SECRET', 'secret')
CSRF_SECRET = os.getenv('CSRF_SECRET', 'secret')
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv('ACCESS_TOKEN_EXPIRE_SECONDS', '10'))
REFRESH_TOKEN_EXPIRE_SECONDS = int(os.getenv('REFRESH_TOKEN_EXPIRE_SECONDS', '1440'))

if PROD:
    GLOG.warning('Запуск сервера в PRODUCTION режиме.')
    
else:
    GLOG.warning('Запуск сервера в тестовом режиме.')


