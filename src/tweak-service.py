#!/usr/bin/env python3
import os, sys
import requests
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
ALLOWED_EXTENSIONS = {'stl', '3mf', 'obj'}

# set current path or use /src/, as docker use that path but doesn't know __file__
CURPATH = os.path.dirname(os.path.abspath(__file__)) + os.sep
if len(CURPATH) <= 2:
    app.logger.error("__file__ too short, setting curpath hard.")
    CURPATH = "/src/"

app.config['UPLOAD_FOLDER'] = CURPATH+"uploads"
app.config['PROFILE_FOLDER'] = CURPATH+'profiles'
app.config['SLIC3R_PATHS'] = ["/Slic3r/slic3r-dist/slic3r", "/home/chris/Documents/software/Slic3r/Slic3rPE-1.41.2+linux64-full-201811221508/slic3r"]
for path in app.config['SLIC3R_PATHS']:
    if os.path.isfile(path):
        app.config['SLIC3R_PATH'] = path
        break

OCTOPRINT_URL = "http://il043/"
OCTOPRINT_APIKEY = "?apikey=1E7A2CA92550406381A176D9C8C8B0C2"


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/tweak", methods=['GET', 'POST'])
def tweak_file():
    try:
        if request.method == 'POST':
            app.logger.debug("request: %s", request)
            # check if the post request has a file
            if 'file' not in request.files:
                flash('No file in request')
                return redirect(request.url)

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
            # if no file was selected, submit an empty one
            if uploaded_file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if not (uploaded_file and allowed_file(uploaded_file.filename)):
                flash('Invalid file')
                return redirect(request.url)

            filename = secure_filename(uploaded_file.filename)
            app.logger.info("Uploaded new file: {}".format(filename))
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            app.logger.info("saved file to {}/{}".format(app.config['UPLOAD_FOLDER'], filename))

            cmd = "python3 {curpath}Tweaker-3{sep}Tweaker.py -i {curpath}{upload_folder}{sep}{input} {cmd} " \
                  "{output} -o {curpath}{upload_folder}{sep}tweaked_{input}"\
                .format(curpath=CURPATH, sep=os.sep, upload_folder=app.config['UPLOAD_FOLDER'], input=filename,
                        cmd=cmd_map[command], output=cmd_map[output_format])

            app.logger.info("command: '{}'".format(cmd))
            ret = os.popen(cmd)

            if ret.read() == "":
                app.logger.info("Tweaking was successful")
            else:
                app.logger.error("Tweaking was executed with the warning: {}.".format(ret.read()))

            outfile = open("{curpath}{upload_folder}{sep}tweaked_{input}"
                           .format(curpath=CURPATH, sep=os.sep, upload_folder=app.config['UPLOAD_FOLDER'],
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


@app.route("/upload-octoprint", methods=['GET', 'POST'])
def tweak_slice_file():
    try:
        if request.method == 'POST':
            app.logger.debug("request: %s", request)
            # check if the post request has a file
            if 'file' not in request.files:
                flash('No file in request')
                return redirect(request.url)

            # Find out if the file is to convert or to tweak
            command = request.form["command"]
            # output_format = request.form["profile"]
            # app.logger.debug("command: {}, output_format: {}".format(command, output_format))

            cmd_map = dict({"Tweak": "",
                            "extendedTweak": "-x",
                            "extendedTweakVol": "-x -vol",
                            "Convert": "-c",
                            "ascii STL": "-t asciistl",
                            "binary STL": "-t binarystl"})

            # manage the file
            uploaded_file = request.files['file']
            # if no file was selected, submit an empty one
            if uploaded_file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if not (uploaded_file and allowed_file(uploaded_file.filename)):
                flash('Invalid file')
                return redirect(request.url)

            filename = secure_filename(uploaded_file.filename)
            app.logger.info("Uploaded new file: {}".format(filename))
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            app.logger.info("Saved file to {}/{}".format(app.config['UPLOAD_FOLDER'], filename))

            # Tweak the file
            cmd = "python3 {curpath}Tweaker-3{sep}Tweaker.py -i {upload_folder}{sep}{input} {cmd} " \
                  "{output} -o {upload_folder}{sep}tweaked_{input}"\
                .format(curpath=CURPATH, sep=os.sep, upload_folder=app.config['UPLOAD_FOLDER'], input=filename,
                        cmd=cmd_map[command], output=cmd_map["binary STL"])

            app.logger.info("command: '{}'".format(cmd))
            ret = os.popen(cmd)
            response = ret.read()
            if response == "":
                app.logger.info("Tweaking was successful")
            else:
                app.logger.error("Tweaking was executed with the warning: {}.".format(response))

            # Slice the file
            app.logger.info("Using profile: {}".format(request.form["profile"]))
            profile = app.config['PROFILE_FOLDER'] + os.sep + request.form["profile"]  # "profiles/profile_015mm_none.ini"
            gcode_path = app.config['UPLOAD_FOLDER'] + os.sep + filename
            gcode_path = gcode_path.replace(".stl", profile.split(os.sep)[-1].replace("profile_", "_").replace(".ini", ".gcode"))

            cmd = "{SLIC3R_PATH} {UPLOAD_FOLDER}{sep}tweaked_{filename} --load {profile} -o {gcode_path}".format(
                sep=os.sep, SLIC3R_PATH=app.config['SLIC3R_PATH'], UPLOAD_FOLDER=app.config['UPLOAD_FOLDER'],
                                           filename=filename, profile=profile, gcode_path=gcode_path)
            app.logger.info(cmd)
            ret = os.popen(cmd)
            response = ret.read()
            if "Done. Process took" in response:
                app.logger.info("Slicing was successful")
            else:
                app.logger.error("Slicing was executed with the warning: {}.".format(response))

            # Upload a file via API to octoprint
            # find the apikey in octoprint server, settings, access control
            url = "{}api/files/local{}".format(OCTOPRINT_URL, OCTOPRINT_APIKEY)
            outfile = "{gcode_path}".format(gcode_path=gcode_path)
            files = {'file': open(outfile, 'rb')}
            r = requests.post(url, files=files)
            app.logger.info("Loaded to Octoprint server with code '{}': {}".format(r.status_code, r.json()))

            return redirect(OCTOPRINT_URL)
        else:
            return render_template('tweak_slice.html', profiles=os.listdir(app.config['PROFILE_FOLDER']))
    except RequestEntityTooLarge:
        abort(413)


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
