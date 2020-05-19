import math
import re
import os
import string
import numpy as np
import shapefile
import zipfile
import json
import geopandas as gpd

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.shortcuts import render
#from statsmodels.regression.linear_model import OLSResults

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def clean_special_chars(line):
    filter_chars = string.punctuation.replace("|", '').replace('@', '').replace('#', '') + '¿' + '¡'
    chars = re.escape(filter_chars)
    return re.sub(r'[' + chars + ']', '', line)

def clean_url(line):
    new_line = line.replace("|", "|;;").split('|')
    complement = new_line[1] if len(new_line) > 1 else ''
    return re.sub(r'http\S+', '', new_line[0]) + complement.replace(";;", "|")


def cleanTweet(text):
    texto = clean_special_chars(clean_url(text))
    return texto

def response_options():
    response = HttpResponse(status=200)
    response['Allow'] = 'OPTIONS, GET, POST'
    response['Access-Control-Request-Method'] = 'OPTIONS, GET, POST'
    response['Access-Control-Request-Headers'] = 'Content-Type'
    response['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

def response_cors(response):
    response['Access-Control-Allow-Origin'] = '*'
    return response

@csrf_exempt
def datos_compuesto_list(request):
    """
    """
    if request.method == 'GET':
        return response_cors(HttpResponse(status=501))

    elif request.method == 'POST':
        #datos = JSONParser().parse(request)
        shp = request.FILES['file']

        z = zipfile.ZipFile(shp, "r")
        password = None
        for path in z.namelist():
            name, extension = os.path.splitext(path)
            if extension == '.shp':
                shp = path
        try:
            z.extractall(pwd=password)
        except:
            print('Error')
            pass
        z.close()

        print (shp)
        tmp = gpd.GeoDataFrame.from_file(shp)
        tmpWGS84 = tmp.to_crs('EPSG:3857')
        tmpWGS84.to_file(shp)

        tmpWGS84.to_file("temp.geojson", driver='GeoJSON')

        with open('temp.geojson') as json_file:
            data = json.load(json_file)

        return response_cors(JSONResponse(json.dumps(data, indent=2), status=200))

    elif request.method == 'OPTIONS':
        return response_cors(response_options())
