import sys, os

from swfu import app
from flask import Flask, request, render_template, url_for, abort, redirect, send_from_directory
reload(sys)
sys.setdefaultencoding("utf-8")

@app.route('/i/<fileName>')
def imageDownload(fileName = ""):
    if fileName != "":
        downloadDocumentPath = os.path.join(app.static_folder, "image")
        return send_from_directory(downloadDocumentPath, fileName)
    else:
        return abort(404)

@app.route('/v/<fileName>')
def videoDownload(fileName = ""):
    if fileName != "":
        downloadDocumentPath = os.path.join(app.static_folder, "video")
        return send_from_directory(downloadDocumentPath, fileName)
    else:
        return abort(404)
    
@app.route('/f/<fileName>')
def fileDownload(fileName = ""):
    if fileName != "":
        downloadDocumentPath = os.path.join(app.static_folder, "anal")
        return send_from_directory(downloadDocumentPath, fileName, as_attachment=True)
    else:
        return abort(404)