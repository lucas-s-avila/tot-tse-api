import json
from flaskr import create_app

with open('./config.json') as config_file:
    config = json.load(config_file)
app = create_app(config)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
