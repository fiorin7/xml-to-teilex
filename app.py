import os
import shutil
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from transform import transform_xml
from zipfile import ZipFile

UPLOAD_FOLDER = 'uploads'
OUTPUT_FILES_FOLDER = 'output_files'
OUTPUT_ZIP_FOLDER = 'output_zip'
ALLOWED_EXTENSIONS = {'xml'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_ZIP_FOLDER'] = OUTPUT_ZIP_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def delete_files_from_folder(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            os.unlink(os.path.join(root, f))


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            transform_xml(f'{UPLOAD_FOLDER}/{filename}')

            with ZipFile(f'{OUTPUT_ZIP_FOLDER}/transformed_files.zip', 'w') as myzip:
                for root, dirs, files in os.walk(OUTPUT_FILES_FOLDER):
                    for f in files:
                        myzip.write(os.path.join(root, f))
            
            filename_output = secure_filename('transformed_files.zip')
            
            delete_files_from_folder(UPLOAD_FOLDER)
            delete_files_from_folder(OUTPUT_FILES_FOLDER)


            return redirect(url_for('output_file',
                                    filename=filename_output))
    return render_template("index.html")



@app.route('/<filename>')
def output_file(filename):
    return send_from_directory(app.config['OUTPUT_ZIP_FOLDER'],
                               filename)