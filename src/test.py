import os
import json
import requests

# url = 'http://localhost:2304/upload-octoprint'
# print(os.getcwd())
# files = {'model': open('uploads/example001.stl', 'rb'),
#          'profile': open('profiles/profile_015mm_brim.ini', 'rb')}
# r = requests.post(url, files=files,
#                   data={"machinecode_name": "output.gco", "tweak_option": "Tweak"})
#
# print(r.status_code)
#print(r.text)

# url = 'http://localhost:2304/upload-octoprint'
# print(os.getcwd())
# r = requests.get(url)
# print(r.status_code)
# #print(r.text)

# # Upload a file via API
# # find the apikey in octoprint server, settings, access control
# url = "http://il043/api/files/local?apikey=1E7A2CA92550406381A176D9C8C8B0C2"
# files = {'file': open('test/example001.stl', 'rb')}
# r = requests.post(url, files=files)
# print(r.status_code)
# print(r.json())


# Delete a file via API
# find the apikey in octoprint server, settings, access control
url = "http://localhost:5000/api/files/local/tmpapache_kafka_keychain.gco?apikey=A943AB47727A461F9CEF9ECD2E4E1E60"
r = requests.delete(url)
print(r.status_code)
print(r.text)


# # Upload a file via my own API of the tweak-service to octoprint
# # find the apikey in octoprint server, settings, access control
# url = "http://localhost:2304/upload-octoprint"
# files = {'file': open('uploads/example001.stl', 'rb')}
# r = requests.post(url, files=files, data={"command": "extendedTweak", "output": "binary STL"})
# print(r.status_code)
# print(r.text)

# # Download a file via API
# # find the apikey in octoprint server, settings, access control
# url = "http://il043/api/files/local/example001.stl?apikey=1E7A2CA92550406381A176D9C8C8B0C2"
# r = requests.get(url)
# print(r.status_code)
# print(json.dumps(r.json(), indent=2))

# # Slicing API
# # find the apikey in octoprint server, settings, access control
# url = "http://il043/api/slicing?apikey=1E7A2CA92550406381A176D9C8C8B0C2"
# r = requests.get(url)
# print(r.status_code)
# print(json.dumps(r.json(), indent=2))

# # get apikey
# # find the apikey in octoprint server, settings, access control
# url = "http://il043/api/setting/apikey?apikey=1E7A2CA92550406381A176D9C8C8B0C2"
# r = requests.get(url)
# print(r.status_code)
# print(json.dumps(r.json(), indent=2))

# SLIC3R_PATH = "/home/chris/Documents/software/Slic3r/Slic3rPE-1.41.2+linux64-full-201811221508/slic3r"
# UPLOAD_FOLDER = "/mnt/D/sr_config/cschranz/Dokumente/ToPrint/Gearbox_Keychain/files"
# profile = "profiles/profile_015mm_none.ini"
# gcode_path = "/mnt/D/sr_config/cschranz/Dokumente/ToPrint/Gearbox_Keychain/files/Gear_12_015mm_none.gcode"
# filename = "Gear_12.stl "
#
# cmd = "{SLIC3R_PATH} {UPLOAD_FOLDER}{sep}tweaked_{filename} --load {profile} " \
#       "-o {gcode_path}".format(sep=os.sep, SLIC3R_PATH=SLIC3R_PATH, UPLOAD_FOLDER=UPLOAD_FOLDER,
#                                filename=filename, profile=profile, gcode_path=gcode_path)
#
# ret = os.popen(cmd)
# print(ret.read())
