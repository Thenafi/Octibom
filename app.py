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
            "failed_id" : [],
            "existingid":[]
        }
        skulist =  [int(i) for i in re.findall("(\d+)", request.form["idboxname"])]
        skulist.sort()
        result['totalid'] = len(skulist)
        category = request.form['catboxname']
        objects=[]
        for e,i in enumerate(skulist):
            print(e,end='\r')
            if Info.query.get(i) is None:
                single_product = Info(sku=i, category= category)
                scraaped_info =  scraping(i)

                if scraaped_info['report'] is not None:
                    single_product.isproblem = True
                    single_product.problem = stringogen(scraaped_info['report'])
                    result['failed']+=1
                    result['failed_id'].append(i)
                else:
                    result['success']+=1
                objects.append(single_product)
            else:
                result['allreadyexsts']+=1
                result['existingid'].append(i)

        db.session.add_all(objects)
        db.session.commit()
        return result



@app.route("/get_listing")
@app.route("/get_listing/")
@app.route("/get_listing/<cat>")
def get_listing(cat=None):
    key_feature= request.args.get("key1")
    key_feature2= request.args.get("key2")
    key_feature3= request.args.get("key3")
    qtgry= request.args.get("qtgry")
    if cat:
        single_product = Info.query.filter_by(islisted=False, isproblem = False,category=cat).order_by(Info.sku.desc()).first()
    else:
        single_product = Info.query.filter_by(islisted=False, isproblem = False).first()
   
    if single_product is not None:
        url = f'/listing/{single_product.sku}'
        return redirect(url_for("get_single_listing", sku=single_product.sku,qtgry =  qtgry))
    else:
        return "No Listing"

@app.route("/listing/<sku>")
def get_single_listing(sku):
    single_product = Info.query.get(sku)
    key_feature= request.args.get("key1")
    key_feature2= request.args.get("key2")
    key_feature3= request.args.get("key3")
    qtgry= request.args.get("qtgry")
    if single_product is None:
        return  "Not Listed"
    else:
        scraaped_info =  scraping(sku)
        scraaped_info['total_occasions'] =["Birthday", "Anniversary", "kitchen", "Akshaya Tritiya", "Baby Shower", "Bachelor Party", "Back to School", "Baptism", "Bhai Dooj", "Bridal Shower", "Christmas", "Cocktail Party", "Congratulations", "Diwali", "Easter", "Eid", "Engagement", "Farewell", "Father's Day", "Friendship Day", "Funeral", "Galentine's Day", "Get Well", "Good Luck", "Graduation", "Grandparent's Day", "Halloween", "Hanukkah", "Holiday", "Housewarming", "Karwa Chauth", "Kwanzaa", "Mardi Gras", "Memorial Day", "Miss You", "Mother's Day", "New Year", "Onam", "Passover", "Pregnancy Announcement", "Prom", "Raksha Bandhan", "Retirement", "St. Patrick's Day", "Sympathy", "Thank You", "Thanksgiving", "Valentine's Day", "Veteran's Day", "Wedding", "Women's Day"]
        scraaped_info['total_department'] =["Women's", "Girl's", "Unisex", "Baby Boys", "Baby Girls", "Boy's", "Men's", "Unisex Baby", "Unisex Kids"] # dont need it or else planned to manually select the items
        scraaped_info['occasions_present'] = list(occasion_finder(scraaped_info["name"]  ,scraaped_info["total_occasions"]))
        scraaped_info['audience_present'] = list(audience_finder(scraaped_info["name"] + " "+ scraaped_info["description"]  ))
        scraaped_info['done'] = single_product.islisted
        scraaped_info['category'] = single_product.category
        scraaped_info['material_from_keywords_cleaned'] = cleaning_materila_keyword(scraaped_info['material_from_keywords'], ['Metal Opener','Wooden Handle'])
        scraaped_info['extra_image'] = f'https://www.qfonic.com/images/products/{sku}/image07_2000.jpg'
        scraaped_info['key_features'] = [key_feature,key_feature2,key_feature3]
        if qtgry ==None:
            scraaped_info['url_address'] = url_maker(scraaped_info['occasions_present'])
        else:
            scraaped_info['url_address'] = url_maker((scraaped_info['name']),"Key")

        
        return render_template('listing.html', data = scraaped_info)




@app.route("/done_listing/<sku>")
def done_listing(sku):
    single_product = Info.query.get(sku)
    if single_product is None:
        return  "Not Listed"
    else:
        single_product.islisted=True
        single_product.listingdate = datetime.now()
        db.session.commit()
        try:
            data = {'idlist': [{"sku":int(sku),"date":datetime.now().strftime("%x")}]}
            append_basket(my_pantry_id, my_basket,data,return_type='body')
        except:
            print('Error: call failed')
        return render_template('done.html',data = str("Listing Added"))

#app the problem pathaile always array patha the hobe strinogen er bhitore
@app.route("/issue/<sku>")
def issue(sku):
    single_product = Info.query.get(sku)
    if single_product is None:
        return  "Not Listed"
    else:
        single_product.isproblem=True
        if single_product.problem == None:
            single_product.problem = stringogen(['Manual Issue'])
        else :
            single_product.problem = stringogen(stringogen(single_product.problem).append("Manual Issue"))
        db.session.commit()
        return render_template('done.html', data = "Issue Added")

@app.route("/notlisted/<sku>")
def notlisted(sku):
    single_product = Info.query.get(sku)
    if single_product is None:
        return  "This SKU is Listed"
    else:
        
        if single_product.islisted == False:
            return render_template('done.html', data = "This Not Listed Yet")
        else :
            single_product.islisted = True
            db.session.commit()
            return render_template('done.html', data = "Listing Info Update to not listed")

@app.route("/setallaslisted")
def setallaslisted():
    fruit_names = Info.query.all()
    dic ={}

    for i in fruit_names:
        i.islisted=True
        i.listingdate = datetime.now()
        for iss in dic["idlist"]:
            if iss['sku'] == i.sku:
                i.listingdate = datetime.strptime(iss['date'],"%x") 
    db.session.add_all(fruit_names)
    db.session.commit()
    return "meh"



@app.route("/removelisting")
def removelisting():
    for i in []:
        Info.query.filter_by(sku=i).delete()
    db.session.commit()
    return "done"

@app.route("/info")
def info():
    todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    list_of_products = Info.query.filter(Info.listingdate >= todays_datetime).all()
    totaldone = Info.query.filter_by(islisted=True).all()
    addedindatabse =Info.query.all()
    return render_template('done.html', data = [len(list_of_products),len(totaldone), len(addedindatabse)])


@app.route("/listingtable")
def listingtable(): 
        page = request.args.get('page', 1, type=int)
        pagination = Info.query.filter_by(islisted=True).order_by(Info.listingdate.desc()).paginate(
            page, per_page=100)
        return render_template('listingtable.html', pagination=pagination)

@app.route("/listingtable2")
def listingtable2(): 
    return redirect(url_for('listingtable'))

if __name__ == "__main__":
  app.run()