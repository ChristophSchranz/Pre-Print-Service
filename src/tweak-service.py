#!/usr/bin/env python3
import os
from flask import Flask, flash, request, redirect, url_for, Response, render_template
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort, RequestEntityTooLarge

import tempfile
import logging
import time
import argparse

app = Flask(__name__)

# If the file size is over 100MB, tweaking would lack due to performance issues.
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
ALLOWED_EXTENSIONS = {'stl', '3mf'}
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/tweak", methods=['GET', 'POST'])
def tweak_slice_file():
    try:
        if request.method == 'POST':
            app.logger.debug("request: %s", request)
            # check if the post request has a file
            if 'file' not in request.files:
                flash('No file in request')
                return redirect(request.url)

            # set current path or use /src/, as docker use that path but doesn't know __file__
            curpath = os.path.dirname(os.path.abspath(__file__)) + os.sep
            if len(curpath) <= 2:
                app.logger.error("__file__ too short, setting curpath hard.")
                curpath = "/src/"

            # Find out if the file is to convert or to tweak
            command = request.form["command"]
            output_format = request.form["output"]
            app.logger.debug("command: {}, output_format: {}".format(command, output_format))

            cmd_map = dict({"Tweak": "",
                            "extendedTweak": "-x",
                            "extendedTweakVol": "-x -vol",
                            "Convert": "-c",
                            "ascii STL": "-t asciistl",
                            "binary STL": "-t binarystl"})

            # manage the file
            uploaded_file = request.files['file']
            app.logger.debug("file: {}".format(uploaded_file))
            # if no file was selected, submit an empty one
            if uploaded_file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if not (uploaded_file and allowed_file(uploaded_file.filename)):
                flash('Invalid file')
                return redirect(request.url)

            filename = secure_filename(uploaded_file.filename)
            app.logger.info("secure filename: {}".format(filename))
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            app.logger.info("saved file {}/{}".format(app.config['UPLOAD_FOLDER'], filename))

            cmd = "python3 {curpath}Tweaker-3{sep}Tweaker.py -i {curpath}{upload_folder}{sep}{input} {cmd} " \
                  "{output} -o {curpath}{upload_folder}{sep}tweaked_{input}"\
                .format(curpath=curpath, sep=os.sep, upload_folder=app.config['UPLOAD_FOLDER'], input=filename,
                        cmd=cmd_map[command], output=cmd_map[output_format])

            app.logger.info("command: {}".format(cmd))
            ret = os.popen(cmd)

            if ret.read() == "":
                app.logger.info("Tweaking was successful")
            else:
                app.logger.error("Tweaking was executed with the warning: {}.".format(ret.read()))

            outfile = open("{curpath}{upload_folder}{sep}tweaked_{input}"
                           .format(curpath=curpath, sep=os.sep, upload_folder=app.config['UPLOAD_FOLDER'],
                                   input=filename), "rb")
            output_content = outfile.read()
            #
            # try:
            #     print("tweaked length: %s", len(output_content))
            # except ValueError:
            #     print("tweaked length: ValueError: View function did not return a response")
            # handling the download of the binary data
            if request.headers.get('Accept') == "text/plain":
                response = Response(output_content)
            else:
                response = Response(output_content, mimetype='application/octet-stream')
                response.headers['Content-Disposition'] = "inline; filename=tweaked_" + filename
            response.headers['Access-Control-Allow-Origin'] = "*"

            return response

        else:
            return render_template('tweak.html')
    except RequestEntityTooLarge:
        abort(413)


@app.route('/upload', methods=['GET', 'POST'])
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
            return redirect(url_for('upload_file', file=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='STL Tweaking Service.')
    parser.add_argument("-p", dest="port", help="port to listen on default: 2304", default="2304")
    parser.add_argument("-l", dest="logfile", help="logfile, default: None", default=None)
    args = parser.parse_args()

    if args.logfile:
        fmt = "%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s"
        level = logging.DEBUG
        logging.basicConfig(format=fmt, filename=args.logfile, level=level)

    app.run(host="0.0.0.0", port=int(args.port), debug=True)
