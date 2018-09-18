from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('config.py')

import api_v1.user
import api_v1.datasets
import api_v1.resources
