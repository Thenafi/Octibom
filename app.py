from datetime import datetime
import re

from flask import Flask, render_template , request , redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from pantry_wrapper import *
import os
from service import *
basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///"+os.path.join(basedir, "posts.sqlite")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Info(db.Model):
    sku = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80),nullable=False)
    islisted = db.Column(db.Boolean, default=False, nullable=False)
    isproblem= db.Column(db.Boolean, default=False, nullable=False)
    listingdate =db.Column(db.DateTime, default = None)
    problem = db.Column(db.String(250), default = None)
    
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
        print('Error: Call failed')
    return data

@app.route('/storing/<id>')
def storing(id):
    try:
        data = {'idlist': [{"sku":int(id),"date":datetime.now().strftime("%x")}]}
        append_basket(my_pantry_id, my_basket,data,return_type='body')
    except:
        print('Error: call failed')
    return render_template('done.html')

@app.route('/datacreator', methods=["POST","GET"])
def datacreator():
    if request.method=="GET":
        return render_template("datacreator.html")
    if request.method =="POST":
        result ={
            "success" : 0,
            "allreadyexsts":0,
            "failed" : 0,
            "failed_id" : []
        }
        skulist =  [int(i) for i in re.findall("(\d+)", request.form["idboxname"])]
        skulist.sort()
        result['totalid'] = len(skulist)
        category = request.form['catboxname']
        for i in skulist:
            if db.session.query(Info.sku).filter_by(sku=i).first() is None:
                single_product = Info(sku=i, category= category)
                scraaped_info =  scraping(i)

                if scraaped_info['report'] is not None:
                    print(single_product, type(single_product))
                    single_product.isproblem = True
                    single_product.problem = stringogen(scraaped_info['report'])
                    result['failed']+=1
                    result['failed_id'].append(i)
                else:
                    result['success']+=1
                
                db.session.add(single_product)
                db.session.commit()
            else:
                result['allreadyexsts']+=1

        return result



@app.route("/get_listing")
def get_listing():
    single_product = Info.query.filter_by(islisted=False, isproblem = False).first()
    if single_product is not None:
        url = f'/get_listing/{single_product.sku}'
        return redirect(url)
    else:
        return "No Listing"

@app.route("/get_listing/<sku>")
def get_single_listing(sku):
    single_product = Info.query.get(sku)
    if single_product is None:
        return  "Not Listed"
    else:
        scraaped_info =  scraping(sku)
        scraaped_info['total_occasions'] =[
        "Anniversary",
        "Birthday",
        "Christmas",
        "Easter",
        "Engagement",
        "Father's Day",
        "Halloween",
        "Hanukkah",
        "Hen Party",
        "Mother's Day",
        "New Baby & Christenings",
        "New Year's",
        "Stag Party",
        "Valentine's Day",
        "Wedding",
        "Wedding Gifts",
    ]
        scraaped_info['occasions_present'] = list(occasion_finder(scraaped_info["description"],scraaped_info["total_occasions"]))
        return render_template('listing.html', data = scraaped_info)



@app.route("/done_listing/<sku>")
def done_listing(sku):
    single_product = Info.query.get(sku)
    if single_product is None:
        return  "Not Listed"
    else:
        single_product.islisted=True
        db.session.commit()
        return render_template('done.html')