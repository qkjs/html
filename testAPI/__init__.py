from flask import Flask

app = Flask(__name__)

import testAPI.views
import testAPI.err
import testAPI.db



