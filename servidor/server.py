#!/usr/bin/env python3
import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.json_util import dumps
client = MongoClient("mongodb://127.0.0.1");


UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))+'/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#app.add_url_rule("/uploads/<name>", endpoint="download_file", build_only=True)

@app.route('/')
def hello():
	return 'Hello, World!'
	
@app.route('/eita')
def eita():
	return 'Aoba'
	
@app.route('/listar')
def listar():
	ret = list(client['soja']['listagem'].find({}).sort([("_id",-1)]))
	strTb = "<table>";
	for linha in ret:
		strTb += "<tr>";
		for campo in linha:
			if campo != '_id':
				strTb += "<td>"+str(linha[campo])+"</td>";
		
		strTb += "<td><img style='width:40px' src='/uploads/"+str(linha['_id'])+".png'/></td>";
		strTb += "</tr>";
	strTb += "</table>";
	return strTb;#dumps(ret)
	
@app.route('/favicon.ico')
def favicon():
	return redirect(url_for('download_file', name="soja.png"))
	
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#proteger com algum tipo de autenticação
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		# If the user does not select a file, the browser submits an
		# empty file without a filename.
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			objMongo = request.form.to_dict();
			#objMongo['img'] = filename
			#fazer verificacao da imagem
			objMongo['soja'] = False;
			resp = client['soja']['listagem'].insert_one(objMongo);
			
			filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(str(resp.inserted_id)+".png"))
			file.save(filename)
			return 'True';
			#redirect(url_for('download_file', name=filename))
	return '''
	<!doctype html>
	<title>Upload new File</title>
	<h1>Upload new File</h1>
	<form method=post enctype=multipart/form-data>
	  <input type=file name=file>
	  <input type=submit value=Upload>
	</form>
	'''

@app.route('/uploads/<name>')
def download_file(name):
	return send_from_directory(app.config["UPLOAD_FOLDER"], name)
	
	# main driver function
if __name__ == '__main__':
  
	# run() method of Flask class runs the application 
	# on the local development server.
	app.run(host='0.0.0.0', port=3000)
