from flask import Flask, render_template
from dotenv import load_dotenv
from pantry_wrapper import *
import os

load_dotenv()
app = Flask(__name__)

my_pantry_id = os.environ.get('PANID')
my_basket = 'amzondonelist'

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/render')
def render():
    return render_template('render.html')

@app.route('/IDmaker')
def IDmaker():
    return render_template('regex.html')

@app.route('/getallid')
def getallid():
    try:
        data = get_contents(my_pantry_id, my_basket, return_type='body')
    except:
        print('Error: call failed')
    return data

@app.route('/storing/<id>')
def storing(id):
    my_pantry_id = os.environ.get('PANID')
    try:
        data = get_contents(my_pantry_id, my_basket, return_type='body')
    except:
        print('Error: call failed')
    data['idlist'].append(int(id))
    append_basket(my_pantry_id, my_basket,data,return_type='body')
    return "Done"

