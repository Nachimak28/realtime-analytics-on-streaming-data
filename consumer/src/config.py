import os
import json
import socket
import datetime
import redis
from base64 import b64encode
from pathlib import Path
from logger import setup_logger



PV_ROOT = Path('./')

LOG_FILE_NAME = '%s_backend.log' % socket.gethostname()

PROJECT_ROOT_FOLDER = Path(os.getcwd()).parent
os.environ.setdefault('PROJECT_ROOT_FOLDER', str(PROJECT_ROOT_FOLDER))

os.environ['LOG_ROOT'] = str(PV_ROOT / 'logs')
os.environ['PV_PATH'] = str(PV_ROOT / 'images')

try:
    Path(os.environ['LOG_ROOT']).mkdir(exist_ok=True, parents=True)
except PermissionError as e:
    quit('''[%s]\n Unable to start. Error making following dirs:\n- %s\n'''
         % (e, os.environ['LOG_ROOT']))

# Defaults

os.environ.setdefault('LOG_FILE_NAME', LOG_FILE_NAME)

########################################################################
# Environment Variables used throughout the codebase

# format of logs
FMT = "[%(asctime)s] [%(levelname)s ] " + \
      "[%(filename)s:%(lineno)d:%(funcName)s()] - %(message)s"

# log file size limit (after which it rotates)
# 1024*1024*4
FSIZE = 4194304

_logger, log_path = setup_logger(
    log_root=os.environ['LOG_ROOT'],
    file_name=os.environ['LOG_FILE_NAME'],
    file_format=FMT,
    file_size=FSIZE,
    debug=True
)

print("Storing logs to file: %s" % log_path)

### Redis config
redis_host = os.environ['REDIS_URL']
redis_password = os.environ['REDIS_PASSWORD']
redis_conn = redis.Redis(host=redis_host, password=redis_password)
