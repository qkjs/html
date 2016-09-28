from flask import Flask, request, render_template
from testAPI import app

@app.errorhandler(400)
def page_not_found(error):
    return ("400")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('err/404.html')

@app.errorhandler(500)
def page_not_found(error):
    return ("500")