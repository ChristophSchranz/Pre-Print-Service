#!/usr/bin/env python3
print("Hello docker")
import os
from flask import Flask, request, Response, render_template
from werkzeug import secure_filename
from werkzeug.exceptions import abort, RequestEntityTooLarge

import tempfile
import logging
import time
import argparse

app = Flask(__name__)

# If filesize is over 100MB, tweaking would lack due to perfomance issues.
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024


@app.route("/tweak", methods=['GET', 'POST'])
@app.route("/", methods=['GET', 'POST'])
def tweak_file():
    try:
        if request.method == 'POST':
            app.logger.debug("request: %s", request)
            curpath = os.path.dirname(os.path.abspath(__file__))+os.sep

            # Find out if the file is to convert or to tweak
            command = list(request.files.keys())[0]
            print("command", command)

            if command == "file2convert":
                req_file = request.files['file2convert']
                app.logger.debug("file2convert: %s", req_file)
                
                filename = secure_filename(req_file.filename)
                app.logger.info("secure filename: %s", filename)
                tmp = tempfile.gettempdir() + os.path.sep + str(time.time()) + "_tmp_" + filename
                req_file.save(tmp)
                app.logger.info("saved file %s", tmp)
                ret = os.popen("python3 {}Tweaker-3{}Tweaker.py -i {} -c -o {}tmpoutfile.stl"
                                        .format(curpath, os.sep, tmp, curpath))
                if ret.read() == "":
                    print("Tweaking was successful")
                else:
                    print("Tweaking was executed with warning {}".format(ret.read()))

                outfile = open("{}tmpoutfile.stl".format(curpath), "rb")
                output_content = outfile.read()
                os.remove(tmp)
                os.remove("{}tmpoutfile.stl".format(curpath))
                app.logger.info("removed temporary file %s", tmp)
                try:
                    print("tweaked length: %s", len(output_content))
                except:
                    print("tweaked length: ValueError: View function did not return a response")

            elif command == "file2tweak":
                req_file = request.files['file2tweak']
                app.logger.debug("file: %s", req_file)
            
                filename = secure_filename(req_file.filename)
                app.logger.info("secure filename: %s", filename)
                # tmp = tempfile.gettempdir() + os.path.sep + str(time.time()) + "_tmp_" + filename
                tmp = curpath + os.path.sep + str(time.time()) + "_tmp_" + filename
                req_file.save(tmp)
                app.logger.info("saved file %s", tmp)
                print("Saved temp file as ", tmp)
                
                ret = os.popen("python3 {}Tweaker-3{}Tweaker.py -i {} -x -o {}tmpoutfile.stl"
                                        .format(curpath, os.sep, tmp, curpath))
                if len(str(ret.read()).replace("\n", "")) == 0:
                    print("Tweaking was successful")
                else:
                    print("Tweaking was executed with warning {}".format(ret.read()))

                outfile = open("{}tmpoutfile.stl".format(curpath, os.sep), "rb")
                output_content = outfile.read()
                
                os.remove(tmp)
                os.remove("{}tmpoutfile.stl".format(curpath, os.sep))
                print("removed temporary file %s", tmp)
                try:
                    print("tweaked length: {}".format(len(output_content)))
                except:
                    print("tweaked length: ValueError: View function did not return a response")

            else:
                print("Input form not found: {}".format(command))

            # handling the download of the binary data
            if request.headers.get('Accept') == "text/plain":
                response = Response(output_content)
            else:
                response = Response(output_content, mimetype='application/octet-stream')
                response.headers['Content-Disposition'] = "inline; filename=tweaked_" + filename.split(".")[0] + ".stl"
            response.headers['Access-Control-Allow-Origin'] = "*"

            return response

        else:
            return render_template('tweak.html')
    except RequestEntityTooLarge:
        abort(413)
    except Exception:
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='STL Tweaking Service.')
    parser.add_argument("-p", dest="port", help="port to listen on default: 5000", default="5000")
    parser.add_argument("-l", dest="logfile", help="logfile, default: None", default=None)
    args = parser.parse_args()

    if args.logfile:
        fmt = "%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s"
        level = logging.DEBUG
        logging.basicConfig(format=fmt, filename=args.logfile, level=level)

    app.run(host="0.0.0.0", port=int(args.port))
