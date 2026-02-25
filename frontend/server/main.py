import os

from config import config_dict
from services import create_app

# Allow CONFIG_MODE/PORT to be set from environment; fall back to Debug/5003.
config_name = os.environ.get('CONFIG_MODE', 'Debug')
config_mode = config_dict.get(config_name)
if not config_mode:
    exit('Error: Invalid CONFIG_MODE environment variable entry.')

app = create_app(config_mode)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5003)))
