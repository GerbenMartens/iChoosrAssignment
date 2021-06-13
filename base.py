#imports
import sys
import argparse
from numpy import true_divide
import pandas as pd
import json
import flask
from flask import request, jsonify, render_template

#to help people understand the call of the script through the -h command, example:
#python base.py -h
parser = argparse.ArgumentParser(description="Searches for a part of the camera name.")
#allow script to be called with parameter --name
parser.add_argument('--name', metavar='name', type=str, help='The name of the camera you are looking for')

#get name var
args = parser.parse_args()
name = args.name

#get camera data
cameras = pd.read_csv('./data/cameras-defb.csv', sep=';')

#get correct camera names
correctCameras = cameras[cameras['Camera'].map(lambda x: name in x)]
#turn correct cameras to dataframe for numbers
correctCamerasDf = pd.DataFrame(correctCameras, columns=['Camera', 'Latitude', 'Longitude'])

#assuming numbers are always on the same spot
def findCameraNumber(x):
    if 'UTR-CM' in x:
        return x[7:10]

#get the correct numbers for the corresponding camera
cameraNumbers = correctCamerasDf['Camera'].map(lambda x: findCameraNumber(x))
#add it to the dataframe
correctCamerasDf = pd.concat([correctCamerasDf, cameraNumbers.rename('Number')], axis=1)
#make it a numeric type for html purposes
correctCamerasDf["Number"] = pd.to_numeric(correctCamerasDf["Number"])

#show the entire dataframe instead of a preview
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

#reset index so missing values dont take up numbers
correctCamerasDf = correctCamerasDf.reset_index(drop=True)

print(correctCamerasDf)

#create flask api
app = flask.Flask(__name__, template_folder='code')
app.config["DEBUG"] = False

#route index, give data and markers as datasets
#data = entire dataframe as dictionary in records format [{column -> value}, … , {column -> value}]
#markers = entire dataframe as json in index format {index -> {column -> value}}
@app.route('/')
def home():
    return render_template('./index.html', data=correctCamerasDf.to_dict(orient='records'), markers=json.loads(correctCamerasDf.to_json(orient='index')))

app.run()