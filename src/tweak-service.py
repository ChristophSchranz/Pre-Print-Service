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

app.config['UPLOAD_FOLDER'] = os.path.join(CURPATH, "uploads")
app.config['PROFILE_FOLDER'] = os.path.join(CURPATH, "profiles")
app.config['DEFAULT_PROFILE'] = os.path.join(app.config['PROFILE_FOLDER'], "/profile_015mm_none.ini")
app.config['SLIC3R_PATHS'] = ["/Slic3r/slic3r-dist/slic3r", "/home/chris/Documents/software/Slic3r/Slic3rPE-1.41.2+linux64-full-201811221508/slic3r"]
for path in app.config['SLIC3R_PATHS']:
    if os.path.isfile(path):
        app.config['SLIC3R_PATH'] = path
        break

OCTOPRINT_URL = os.getenv("OCTOPRINT_URL", "http://localhost:5000/")  # "http://192.168.48.43/")
OCTOPRINT_APIKEY = "?apikey=" + os.getenv("OCTOPRINT_APIKEY", "A943AB47727A461F9CEF9ECD2E4E1E60")  # "1E7A2CA92550406381A176D9C8C8B0C2")
# app.logger.info("Using octoprint server with url: {}".format(OCTOPRINT_URL))


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

            cmd = "python3 {curpath}Tweaker-3{sep}Tweaker.py -i {upload_folder}{sep}{input} {cmd} " \
                  "{output} -o {upload_folder}{sep}tweaked_{input}"\
                .format(curpath=CURPATH, sep=os.sep, upload_folder=app.config['UPLOAD_FOLDER'], input=filename,
                        cmd=cmd_map[command], output=cmd_map[output_format])

            app.logger.info("command: '{}'".format(cmd))
            ret = os.popen(cmd)

            if ret.read() == "":
                app.logger.info("Tweaking was successful")
            else:
                app.logger.error("Tweaking was executed with the warning: {}.".format(ret.read()))

            outfile = open("{upload_folder}{sep}tweaked_{input}"
                           .format(curpath=CURPATH, sep=os.sep, upload_folder=app.config['UPLOAD_FOLDER'],
                                   input=filename), "rb")
            output_content = outfile.read()

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


@app.route("/", methods=['GET', 'POST'])
@app.route("/upload-octoprint", methods=['GET', 'POST'])
def tweak_slice_file():
    try:
        if request.method == 'POST':
            # 1) Check if the input is correct
            # 1.1) Get the model file and check for correctness
            app.logger.debug("request: %s", request)
            if 'model' not in request.files:
                flash('No model file in request')
            # manage the file
            uploaded_file = request.files['model']
            # if no file was selected, submit an empty one
            if uploaded_file.filename == '':
                flash('No selected model')
                return redirect(request.url)
            if not (uploaded_file and allowed_file(uploaded_file.filename)):
                flash('Invalid model')
                return redirect(request.url)
            filename = secure_filename(uploaded_file.filename)
            app.logger.info("Uploaded new model: {}".format(filename))
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            app.logger.info("Saved model to {}/{}".format(app.config['UPLOAD_FOLDER'], filename))

            # 1.2) Get the profile
            if 'profile' not in request.files:
                flash('No profile in request, using default profile')
            profile = request.files.get("profile", app.config['DEFAULT_PROFILE'])
            app.logger.info("Using profile: {}".format(profile))
            if profile.filename == '':
                flash('No selected model')
                return redirect(request.url)
            profile_path = os.path.join(app.config['PROFILE_FOLDER'], secure_filename(profile.filename))
            profile.save(profile_path)
            app.logger.info("Saved profile to {}".format(profile_path))

            # 1.3) Get the tweak option
            # Get the tweak option and use extendedTweak minimize the volume as default
            command = request.form.get("tweak_option", "extendedTweakVol")
            app.logger.info("Using Tweaker option {}".format(command))
            cmd_map = dict({"Tweak": "",
                            "extendedTweak": "-x",
                            "extendedTweakVol": "-x -vol",
                            "Convert": "-c",
                            "ascii STL": "-t asciistl",
                            "binary STL": "-t binarystl"})

            # 1.4) Get the machinecode_name
            machinecode_name = request.form.get("machinecode_name", filename.replace(".stl", ".gcode"))
            gcode_path = os.path.join(app.config["UPLOAD_FOLDER"], machinecode_name)
            app.logger.info("Machinecode will have name {}".format(machinecode_name))

            # 2) retrieve the model file and perform the tweaking
            cmd = "python3 {curpath}Tweaker-3{sep}Tweaker.py -i {upload_folder}{sep}{input} {cmd} " \
                  "{output} -o {upload_folder}{sep}tweaked_{input}" \
                .format(curpath=CURPATH, sep=os.sep, upload_folder=app.config['UPLOAD_FOLDER'], input=filename,
                        cmd=cmd_map[command], output=cmd_map["binary STL"])

            app.logger.info("Running Tweak with command: '{}'".format(cmd))
            ret = os.popen(cmd)
            response = ret.read()
            if response == "":
                app.logger.info("Tweaking was successful")
            else:
                app.logger.error("Tweaking was executed with the warning: {}.".format(response))

            # 3) Slice the tweaked model using Slic3r
            # Slice the file
            cmd = "{SLIC3R_PATH} {UPLOAD_FOLDER}{sep}tweaked_{filename} --load {profile} -o {gcode_path}".format(
                sep=os.sep, SLIC3R_PATH=app.config['SLIC3R_PATH'], UPLOAD_FOLDER=app.config['UPLOAD_FOLDER'],
                filename=filename, profile=profile_path, gcode_path=gcode_path)
            # TODO improve gcode name
            app.logger.info("Slicing the tweaked model with command: {}".format(cmd))
            # ret = os.popen(cmd)
            response = os.popen(cmd).read()
            if "Done. Process took" in response:
                app.logger.info("Slicing was successful")
            else:
                app.logger.error("Slicing was executed with the warning: {}.".format(response))

            # 4) Redirect the ready gcode
            # Upload a model via API to octoprint
            # find the apikey in octoprint server, settings, access control
            app.logger.info("Redirecting processed machinecode to {}".format(request.url))
            url = "{}api/files/local{}".format(OCTOPRINT_URL, OCTOPRINT_APIKEY)  # Todo check for validity
            outfile = "{gcode_path}".format(gcode_path=gcode_path)
            app.logger.info("sending file '{}' to URL '{}'".format(outfile, url))
            files = {'file': open(gcode_path, 'rb')}
            r = requests.post(url, files=files)
            app.logger.info("Loaded to Octoprint server with code '{}'".format(r.status_code))  # TODO if code==201...
            # sys.exit()
            return redirect(request.url)

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

    app.secret_key = 'secret_key'
    # app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host="0.0.0.0", port=int(args.port), debug=True)
