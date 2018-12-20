#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, request, redirect, url_for, send_from_directory, render_template, make_response
from werkzeug.utils import secure_filename
import re
import os
import xml.sax
import base64
import pickle

UPLOAD_FOLDER = '.'
ALLOWED_EXTENSIONS = set(['xml'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class VulnParse(xml.sax.handler.ContentHandler):
  def __init__(self, object):
    self.obj = object
    self.curpath = []
  
  def startElement(self, name, attrs):
    self.chars = ""
    print name,attrs
  
  def endElement(self, name):
    if name in set(['To','Subject','Content']):
      self.obj[name] = self.chars

  def characters(self, content):
    self.chars += content

def process_xml(filename):
  parser = xml.sax.make_parser()
  object = {}
  handler = VulnParse(object)
  parser.setContentHandler(handler)
  parser.parse(open(filename))
#  print object
  return " SENT EMAIL: \r\n " + \
         " To: " + object["To"] + "\r\n" + \
         " Subject: " + object["Subject"] + "\r\n" + \
         " Content: " + object["Content"] + "\r\n" + \
         " URL for later reference: " + url_for('uploaded_file',filename=filename)

def template(fname):
  name=request.args.get('name','')
  with open(fname, 'r') as myfile:
    data=myfile.read().replace('\n', '')
  content=re.sub('\$name', name, data)
  return content


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
  if request.method == 'POST':
     # check if the post request has the file part
     if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
     file = request.files['file']
     # if user does not select file, browser also
     # submit a empty part without filename
     if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
     if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return process_xml(filename)
        # return redirect(url_for('uploaded_file',filename=filename))
  return template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route("/")
def xss():
    return template('index.html')

# Notice: this may be extremely dangerous if you are running this on your own computer.
@app.route("/bonus")
def bonus():
  fname = request.args.get('name')
  fname = re.sub('[\/*?]','',fname)
  with open(fname, 'r') as myfile:
    data=myfile.read().replace('\n', '')
  return data


@app.route("/xss5")
def xss5():
  return template('xss5.html')

@app.route("/myson")
def myson():
  jsonni = request.args.get('name')
  jsonni = re.sub('[":{},]','',jsonni)
  return '{"name": "' + jsonni + '"}'


@app.route("/xss1")
def xss1():
  f = '<html><body>Mighty ' + request.args.get('name') + ', compose your email now:'
  g = """
           <form>To: <input type='text'></input><br>
           Subject: <input type='text'></input><br>
           Content: <textarea></textarea><br>
           <input type="button" value="Send!"/>
           </form></body></html>
         """
  return f + g

@app.route("/xss2")
def xss2():
  return template('xss2.html')

@app.route("/xss3")
def xss3():
  return template('xss3.html')

@app.route("/xss4")
def xss4():
  return template('xss4.html')

@app.route("/deepest-secret")
def innermystery():
  return template('innermystery.txt')


@app.route("/mystery")
def mystery():
  return redirect(request.args.get('name'), code=302)

@app.route("/sessioncookie", methods = ['GET'])
def sessioncookie():
  class SessionClass:
    authenticated = False

  COOKIENAME = 'sessioncookie'
  BASEDATA = SessionClass()
  session_cookie = request.cookies.get(COOKIENAME)
  if session_cookie:
    try:
      session_data = pickle.loads(base64.b64decode(session_cookie))
    except (AttributeError, TypeError) as e:
      session_data = BASEDATA
  else:
    session_data = BASEDATA
  resp = make_response(render_template("sessioncookie.html", session_data=session_data))
  resp.set_cookie(COOKIENAME, base64.b64encode(pickle.dumps(session_data)))
  return resp

if __name__ == "__main__":
      app.run(host='0.0.0.0')
