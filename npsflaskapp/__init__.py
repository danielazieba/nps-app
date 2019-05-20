from flask import Flask

app = Flask(__name__)

from npsflaskapp import routes
