from config import config_dict
from services import create_app

try:
    config_mode = config_dict['Debug']
except KeyError:
    exit('Error: Invalid CONFIG_MODE environment variable entry.')

app = create_app(config_mode)


if __name__ == '__main__':
   app.run('0.0.0.0', '5003')