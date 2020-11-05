import os
from os import environ
import shutil
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from transform import transform_xml
from zipfile import ZipFile
from debug import debug

UPLOAD_FOLDER = 'uploads'
OUTPUT_FILES_FOLDER = 'output_files'
OUTPUT_ZIP_FOLDER = 'output_zip'
ALLOWED_EXTENSIONS = {'xml'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_ZIP_FOLDER'] = OUTPUT_ZIP_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.secret_key = 'debug_key' if not environ.get('SECRET_KEY') else environ['SECRET_KEY']


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

        delete_files_from_folder(UPLOAD_FOLDER)
        delete_files_from_folder(OUTPUT_FILES_FOLDER)

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

        if not allowed_file(file.filename):
            flash(f'Only {", ".join(ALLOWED_EXTENSIONS)} files allowed')
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


            try:
                app.logger.info("Transforming the file")
                transform_xml(f'{UPLOAD_FOLDER}/{filename}', OUTPUT_FILES_FOLDER)
                app.logger.info("Transforming the file ... done")
            except Exception as e:
                app.logger.error("Transforming the file failed: ", str(e))
                flash('Failed to convert file.')
                return redirect(request.url)

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

if __name__ == '__main__':
    if debug():
        app.logger.info("Running in debug mode")
    app.run(host='0.0.0.0')
