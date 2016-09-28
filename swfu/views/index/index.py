#coding = "utf-8"

from flask import render_template
from swfu import app
import sys

import swfu.views.apiTest.bugAnalyse


reload(sys)
sys.setdefaultencoding("utf-8")

@app.route('/')
def index():
    return render_template('index.html',pageTitle = "API Testing")