from datetime import datetime
import re
import string
from unicodedata import category
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
    if cat:
        single_product = Info.query.filter_by(islisted=False, isproblem = False,category=cat).first()
    else:
        single_product = Info.query.filter_by(islisted=False, isproblem = False).first()
   
    if single_product is not None:
        url = f'/listing/{single_product.sku}'
        return redirect(url)
    else:
        return "No Listing"

@app.route("/listing/<sku>")
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
        scraaped_info['occasions_present'] = list(occasion_finder(scraaped_info["name"] + " "+ scraaped_info["description"]   ,scraaped_info["total_occasions"]))
        scraaped_info['done'] = single_product.islisted
        scraaped_info['category'] = single_product.category
        scraaped_info['extra_image'] = f'https://www.qfonic.com/images/products/{sku}/image07_2000.jpg'
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
    dic ={"idlist":[{"sku":27291,"date":"08/08/22"},{"sku":27290,"date":"08/08/22"},{"sku":27289,"date":"08/08/22"},{"sku":27288,"date":"08/08/22"},{"sku":27287,"date":"08/08/22"},{"sku":27286,"date":"08/08/22"},{"sku":27285,"date":"08/08/22"},{"sku":27284,"date":"08/08/22"},{"sku":27283,"date":"08/08/22"},{"sku":27282,"date":"08/08/22"},{"sku":27281,"date":"08/08/22"},{"sku":27280,"date":"08/08/22"},{"sku":27279,"date":"08/08/22"},{"sku":27278,"date":"08/08/22"},{"sku":27277,"date":"08/08/22"},{"sku":27276,"date":"08/08/22"},{"sku":27275,"date":"08/08/22"},{"sku":27274,"date":"08/08/22"},{"sku":27273,"date":"08/08/22"},{"sku":27272,"date":"08/08/22"},{"sku":27271,"date":"08/08/22"},{"sku":27270,"date":"08/08/22"},{"sku":27269,"date":"08/08/22"},{"sku":27268,"date":"08/08/22"},{"sku":27267,"date":"08/08/22"},{"sku":27266,"date":"08/08/22"},{"sku":27264,"date":"08/08/22"},{"sku":27261,"date":"08/08/22"},{"sku":27258,"date":"08/08/22"},{"sku":27255,"date":"08/08/22"},{"sku":27253,"date":"08/08/22"},{"sku":27252,"date":"08/08/22"},{"sku":27251,"date":"08/08/22"},{"sku":27250,"date":"08/08/22"},{"sku":27248,"date":"08/09/22"},{"sku":27249,"date":"08/09/22"},{"sku":27247,"date":"08/09/22"},{"sku":27246,"date":"08/09/22"},{"sku":27245,"date":"08/09/22"},{"sku":27244,"date":"08/09/22"},{"sku":27243,"date":"08/09/22"},{"sku":27242,"date":"08/09/22"},{"sku":27241,"date":"08/09/22"},{"sku":27240,"date":"08/09/22"},{"sku":27239,"date":"08/09/22"},{"sku":27238,"date":"08/09/22"},{"sku":27237,"date":"08/09/22"},{"sku":27236,"date":"08/09/22"},{"sku":27235,"date":"08/09/22"},{"sku":27234,"date":"08/09/22"},{"sku":27233,"date":"08/09/22"},{"sku":27232,"date":"08/09/22"},{"sku":27231,"date":"08/09/22"},{"sku":27230,"date":"08/10/22"},{"sku":27229,"date":"08/10/22"},{"sku":27228,"date":"08/10/22"},{"sku":27227,"date":"08/10/22"},{"sku":27226,"date":"08/10/22"},{"sku":27225,"date":"08/10/22"},{"sku":27224,"date":"08/10/22"},{"sku":27223,"date":"08/10/22"},{"sku":27222,"date":"08/10/22"},{"sku":27221,"date":"08/10/22"},{"sku":27220,"date":"08/10/22"},{"sku":27219,"date":"08/10/22"},{"sku":27218,"date":"08/10/22"},{"sku":27217,"date":"08/10/22"},{"sku":27216,"date":"08/10/22"},{"sku":27215,"date":"08/10/22"},{"sku":27214,"date":"08/10/22"},{"sku":27209,"date":"08/10/22"},{"sku":27208,"date":"08/10/22"},{"sku":27207,"date":"08/10/22"},{"sku":27206,"date":"08/10/22"},{"sku":27205,"date":"08/10/22"},{"sku":27204,"date":"08/10/22"},{"sku":27212,"date":"08/10/22"},{"sku":27213,"date":"08/10/22"},{"sku":27203,"date":"08/10/22"},{"sku":27202,"date":"08/10/22"},{"sku":27201,"date":"08/10/22"},{"sku":27200,"date":"08/10/22"},{"sku":27211,"date":"08/10/22"},{"sku":27210,"date":"08/10/22"},{"sku":27199,"date":"08/10/22"},{"sku":27198,"date":"08/10/22"},{"sku":27197,"date":"08/10/22"},{"sku":27196,"date":"08/10/22"},{"sku":27195,"date":"08/10/22"},{"sku":27194,"date":"08/10/22"},{"sku":27193,"date":"08/10/22"},{"sku":27192,"date":"08/10/22"},{"sku":27191,"date":"08/10/22"},{"sku":27190,"date":"08/10/22"},{"sku":27189,"date":"08/10/22"},{"sku":27188,"date":"08/10/22"},{"sku":27187,"date":"08/10/22"},{"sku":27186,"date":"08/10/22"},{"sku":27185,"date":"08/10/22"},{"sku":27184,"date":"08/10/22"},{"sku":27183,"date":"08/10/22"},{"sku":27182,"date":"08/10/22"},{"sku":27181,"date":"08/10/22"},{"sku":27180,"date":"08/10/22"},{"sku":27179,"date":"08/10/22"},{"sku":27178,"date":"08/10/22"},{"sku":27177,"date":"08/10/22"},{"sku":27176,"date":"08/10/22"},{"sku":27175,"date":"08/10/22"},{"sku":27174,"date":"08/10/22"},{"sku":27173,"date":"08/10/22"},{"sku":27172,"date":"08/10/22"},{"sku":27169,"date":"08/10/22"},{"sku":27168,"date":"08/10/22"},{"sku":27167,"date":"08/10/22"},{"sku":27166,"date":"08/10/22"},{"sku":27165,"date":"08/10/22"},{"sku":27164,"date":"08/10/22"},{"sku":27163,"date":"08/10/22"},{"sku":27162,"date":"08/10/22"},{"sku":27160,"date":"08/10/22"},{"sku":27159,"date":"08/10/22"},{"sku":27158,"date":"08/10/22"},{"sku":27157,"date":"08/10/22"},{"sku":27156,"date":"08/10/22"},{"sku":27155,"date":"08/10/22"},{"sku":27154,"date":"08/10/22"},{"sku":27153,"date":"08/10/22"},{"sku":27152,"date":"08/10/22"},{"sku":27151,"date":"08/10/22"},{"sku":27150,"date":"08/11/22"},{"sku":27149,"date":"08/11/22"},{"sku":27148,"date":"08/11/22"},{"sku":27147,"date":"08/11/22"},{"sku":27146,"date":"08/11/22"},{"sku":27145,"date":"08/11/22"},{"sku":27144,"date":"08/11/22"},{"sku":27143,"date":"08/11/22"},{"sku":27142,"date":"08/11/22"},{"sku":27141,"date":"08/11/22"},{"sku":27140,"date":"08/11/22"},{"sku":27139,"date":"08/11/22"},{"sku":27138,"date":"08/12/22"},{"sku":27137,"date":"08/12/22"},{"sku":27136,"date":"08/12/22"},{"sku":27135,"date":"08/12/22"},{"sku":27134,"date":"08/12/22"},{"sku":27133,"date":"08/12/22"},{"sku":27132,"date":"08/12/22"},{"sku":27131,"date":"08/12/22"},{"sku":27130,"date":"08/12/22"},{"sku":27129,"date":"08/12/22"},{"sku":27128,"date":"08/12/22"},{"sku":27127,"date":"08/12/22"},{"sku":27126,"date":"08/12/22"},{"sku":27125,"date":"08/12/22"},{"sku":27124,"date":"08/12/22"},{"sku":27123,"date":"08/12/22"},{"sku":27122,"date":"08/12/22"},{"sku":27121,"date":"08/12/22"},{"sku":27120,"date":"08/12/22"},{"sku":27119,"date":"08/12/22"},{"sku":27118,"date":"08/12/22"},{"sku":27117,"date":"08/12/22"},{"sku":27116,"date":"08/12/22"},{"sku":27115,"date":"08/12/22"},{"sku":27114,"date":"08/12/22"},{"sku":27113,"date":"08/12/22"},{"sku":27112,"date":"08/12/22"},{"sku":27111,"date":"08/12/22"},{"sku":27110,"date":"08/12/22"},{"sku":27109,"date":"08/12/22"},{"sku":27108,"date":"08/12/22"},{"sku":27107,"date":"08/12/22"},{"sku":27106,"date":"08/12/22"},{"sku":27104,"date":"08/12/22"},{"sku":27103,"date":"08/12/22"},{"sku":27102,"date":"08/12/22"},{"sku":27101,"date":"08/12/22"},{"sku":27100,"date":"08/12/22"},{"sku":27099,"date":"08/12/22"},{"sku":27098,"date":"08/12/22"},{"sku":27097,"date":"08/12/22"},{"sku":27096,"date":"08/12/22"},{"sku":27095,"date":"08/12/22"},{"sku":27094,"date":"08/12/22"},{"sku":27093,"date":"08/12/22"},{"sku":27092,"date":"08/12/22"},{"sku":27091,"date":"08/12/22"},{"sku":27090,"date":"08/12/22"},{"sku":27089,"date":"08/12/22"},{"sku":27088,"date":"08/12/22"},{"sku":27087,"date":"08/12/22"},{"sku":27086,"date":"08/12/22"},{"sku":27085,"date":"08/12/22"},{"sku":27084,"date":"08/12/22"},{"sku":27082,"date":"08/12/22"},{"sku":27081,"date":"08/12/22"},{"sku":27080,"date":"08/12/22"},{"sku":27079,"date":"08/12/22"},{"sku":27078,"date":"08/12/22"},{"sku":27077,"date":"08/12/22"},{"sku":27076,"date":"08/12/22"},{"sku":27075,"date":"08/12/22"},{"sku":27074,"date":"08/12/22"},{"sku":27073,"date":"08/12/22"},{"sku":27072,"date":"08/12/22"},{"sku":27071,"date":"08/12/22"},{"sku":27070,"date":"08/12/22"},{"sku":27069,"date":"08/12/22"},{"sku":27068,"date":"08/12/22"},{"sku":27067,"date":"08/12/22"},{"sku":27066,"date":"08/12/22"},{"sku":27065,"date":"08/12/22"},{"sku":27064,"date":"08/12/22"},{"sku":27063,"date":"08/12/22"},{"sku":27062,"date":"08/12/22"},{"sku":27061,"date":"08/12/22"},{"sku":27060,"date":"08/12/22"},{"sku":27059,"date":"08/12/22"},{"sku":27058,"date":"08/12/22"},{"sku":27057,"date":"08/12/22"},{"sku":27056,"date":"08/12/22"},{"sku":27055,"date":"08/12/22"},{"sku":27054,"date":"08/12/22"},{"sku":27053,"date":"08/12/22"},{"sku":27052,"date":"08/12/22"},{"sku":27051,"date":"08/12/22"},{"sku":27050,"date":"08/12/22"},{"sku":27049,"date":"08/12/22"},{"sku":27048,"date":"08/12/22"},{"sku":27047,"date":"08/12/22"},{"sku":27046,"date":"08/12/22"},{"sku":27045,"date":"08/12/22"},{"sku":27044,"date":"08/12/22"},{"sku":27043,"date":"08/12/22"},{"sku":27042,"date":"08/12/22"},{"sku":27041,"date":"08/12/22"},{"sku":27040,"date":"08/12/22"},{"sku":27039,"date":"08/12/22"},{"sku":27038,"date":"08/12/22"},{"sku":27037,"date":"08/12/22"},{"sku":27036,"date":"08/12/22"},{"sku":27035,"date":"08/12/22"},{"sku":27034,"date":"08/12/22"},{"sku":27033,"date":"08/12/22"},{"sku":27031,"date":"08/12/22"},{"sku":27030,"date":"08/12/22"},{"sku":27029,"date":"08/12/22"},{"sku":27028,"date":"08/12/22"},{"sku":27027,"date":"08/13/22"},{"sku":27026,"date":"08/13/22"},{"sku":27025,"date":"08/13/22"},{"sku":27024,"date":"08/13/22"},{"sku":27023,"date":"08/13/22"},{"sku":27022,"date":"08/13/22"},{"sku":27021,"date":"08/13/22"},{"sku":27020,"date":"08/13/22"},{"sku":27019,"date":"08/13/22"},{"sku":27018,"date":"08/13/22"},{"sku":27017,"date":"08/13/22"},{"sku":27016,"date":"08/13/22"},{"sku":27015,"date":"08/13/22"},{"sku":27014,"date":"08/13/22"},{"sku":27013,"date":"08/13/22"},{"sku":27012,"date":"08/13/22"},{"sku":27011,"date":"08/13/22"},{"sku":27010,"date":"08/13/22"},{"sku":27009,"date":"08/13/22"},{"sku":27008,"date":"08/13/22"},{"sku":27007,"date":"08/13/22"},{"sku":27006,"date":"08/13/22"},{"sku":27005,"date":"08/13/22"},{"sku":27004,"date":"08/13/22"},{"sku":27003,"date":"08/13/22"},{"sku":27002,"date":"08/13/22"},{"sku":27001,"date":"08/13/22"},{"sku":26167,"date":"08/13/22"},{"sku":26136,"date":"08/13/22"},{"sku":26135,"date":"08/13/22"},{"sku":26117,"date":"08/13/22"},{"sku":26116,"date":"08/13/22"},{"sku":26115,"date":"08/13/22"},{"sku":26050,"date":"08/13/22"},{"sku":26049,"date":"08/13/22"},{"sku":26048,"date":"08/13/22"},{"sku":26047,"date":"08/13/22"},{"sku":26046,"date":"08/13/22"},{"sku":26045,"date":"08/13/22"},{"sku":26043,"date":"08/13/22"},{"sku":26042,"date":"08/13/22"},{"sku":26041,"date":"08/13/22"},{"sku":26030,"date":"08/13/22"},{"sku":26027,"date":"08/15/22"},{"sku":26024,"date":"08/15/22"},{"sku":26017,"date":"08/15/22"},{"sku":26012,"date":"08/15/22"},{"sku":26011,"date":"08/15/22"},{"sku":26010,"date":"08/15/22"},{"sku":26009,"date":"08/15/22"},{"sku":26008,"date":"08/15/22"},{"sku":26007,"date":"08/15/22"},{"sku":26006,"date":"08/15/22"},{"sku":26005,"date":"08/15/22"},{"sku":26004,"date":"08/15/22"},{"sku":26003,"date":"08/15/22"},{"sku":26002,"date":"08/15/22"},{"sku":26001,"date":"08/15/22"},{"sku":25998,"date":"08/15/22"},{"sku":25997,"date":"08/15/22"},{"sku":25996,"date":"08/15/22"},{"sku":25995,"date":"08/15/22"},{"sku":25994,"date":"08/15/22"},{"sku":25993,"date":"08/15/22"},{"sku":25992,"date":"08/15/22"},{"sku":25991,"date":"08/15/22"},{"sku":25990,"date":"08/15/22"},{"sku":25989,"date":"08/15/22"},{"sku":25988,"date":"08/15/22"},{"sku":25987,"date":"08/15/22"},{"sku":25986,"date":"08/15/22"},{"sku":25985,"date":"08/15/22"},{"sku":25984,"date":"08/15/22"},{"sku":25983,"date":"08/15/22"},{"sku":25980,"date":"08/15/22"},{"sku":25978,"date":"08/15/22"},{"sku":25977,"date":"08/15/22"},{"sku":25976,"date":"08/15/22"},{"sku":25975,"date":"08/15/22"},{"sku":25974,"date":"08/15/22"},{"sku":25973,"date":"08/15/22"},{"sku":25972,"date":"08/15/22"},{"sku":25969,"date":"08/15/22"},{"sku":25968,"date":"08/15/22"},{"sku":25967,"date":"08/15/22"},{"sku":25966,"date":"08/15/22"},{"sku":25965,"date":"08/15/22"},{"sku":25958,"date":"08/15/22"},{"sku":25950,"date":"08/15/22"},{"sku":25949,"date":"08/15/22"},{"sku":25948,"date":"08/15/22"},{"sku":25947,"date":"08/15/22"},{"sku":25946,"date":"08/15/22"},{"sku":25945,"date":"08/15/22"},{"sku":25944,"date":"08/15/22"},{"sku":25943,"date":"08/15/22"},{"sku":25942,"date":"08/15/22"},{"sku":25941,"date":"08/15/22"},{"sku":25939,"date":"08/15/22"},{"sku":25938,"date":"08/15/22"},{"sku":25937,"date":"08/15/22"},{"sku":25936,"date":"08/15/22"},{"sku":25935,"date":"08/15/22"},{"sku":25936,"date":"08/16/22"},{"sku":27639,"date":"08/16/22"},{"sku":27638,"date":"08/16/22"},{"sku":27634,"date":"08/16/22"},{"sku":27633,"date":"08/16/22"},{"sku":27632,"date":"08/16/22"},{"sku":27631,"date":"08/16/22"},{"sku":27630,"date":"08/16/22"},{"sku":27628,"date":"08/16/22"},{"sku":27627,"date":"08/16/22"},{"sku":27626,"date":"08/16/22"},{"sku":27625,"date":"08/16/22"},{"sku":27624,"date":"08/16/22"},{"sku":27623,"date":"08/16/22"},{"sku":27622,"date":"08/16/22"},{"sku":27621,"date":"08/16/22"},{"sku":27620,"date":"08/16/22"},{"sku":27619,"date":"08/16/22"},{"sku":27618,"date":"08/16/22"},{"sku":27617,"date":"08/16/22"},{"sku":27616,"date":"08/16/22"},{"sku":27615,"date":"08/16/22"},{"sku":27614,"date":"08/16/22"},{"sku":27613,"date":"08/16/22"},{"sku":27612,"date":"08/16/22"},{"sku":27611,"date":"08/16/22"},{"sku":27610,"date":"08/16/22"},{"sku":27609,"date":"08/16/22"},{"sku":27608,"date":"08/16/22"},{"sku":27606,"date":"08/16/22"},{"sku":27605,"date":"08/16/22"},{"sku":27604,"date":"08/16/22"},{"sku":27603,"date":"08/16/22"},{"sku":27602,"date":"08/16/22"},{"sku":27601,"date":"08/16/22"},{"sku":27600,"date":"08/16/22"},{"sku":27599,"date":"08/16/22"},{"sku":27598,"date":"08/16/22"},{"sku":27597,"date":"08/16/22"},{"sku":27596,"date":"08/16/22"},{"sku":27595,"date":"08/16/22"},{"sku":27594,"date":"08/16/22"},{"sku":27593,"date":"08/17/22"},{"sku":27592,"date":"08/17/22"},{"sku":27591,"date":"08/17/22"},{"sku":27590,"date":"08/17/22"},{"sku":27589,"date":"08/17/22"},{"sku":27588,"date":"08/17/22"},{"sku":27587,"date":"08/17/22"},{"sku":27586,"date":"08/17/22"},{"sku":27585,"date":"08/17/22"},{"sku":27584,"date":"08/17/22"},{"sku":27583,"date":"08/17/22"},{"sku":27582,"date":"08/17/22"},{"sku":27581,"date":"08/17/22"},{"sku":27580,"date":"08/17/22"},{"sku":27579,"date":"08/17/22"},{"sku":27578,"date":"08/17/22"},{"sku":27577,"date":"08/17/22"},{"sku":27576,"date":"08/17/22"},{"sku":27575,"date":"08/17/22"},{"sku":27574,"date":"08/17/22"},{"sku":27573,"date":"08/17/22"},{"sku":27572,"date":"08/17/22"},{"sku":27571,"date":"08/17/22"},{"sku":27570,"date":"08/17/22"},{"sku":27569,"date":"08/17/22"},{"sku":27567,"date":"08/17/22"},{"sku":27566,"date":"08/17/22"},{"sku":27565,"date":"08/17/22"},{"sku":27564,"date":"08/17/22"},{"sku":27563,"date":"08/17/22"},{"sku":27562,"date":"08/17/22"},{"sku":27561,"date":"08/17/22"},{"sku":27560,"date":"08/17/22"},{"sku":27559,"date":"08/17/22"},{"sku":27558,"date":"08/17/22"},{"sku":27557,"date":"08/17/22"},{"sku":27556,"date":"08/17/22"},{"sku":27555,"date":"08/17/22"},{"sku":27554,"date":"08/17/22"},{"sku":27552,"date":"08/17/22"},{"sku":27551,"date":"08/17/22"},{"sku":27550,"date":"08/17/22"},{"sku":27549,"date":"08/17/22"},{"sku":27548,"date":"08/17/22"},{"sku":27547,"date":"08/17/22"},{"sku":27546,"date":"08/17/22"},{"sku":27545,"date":"08/17/22"},{"sku":27544,"date":"08/17/22"},{"sku":27543,"date":"08/17/22"},{"sku":27542,"date":"08/17/22"},{"sku":27541,"date":"08/17/22"},{"sku":27540,"date":"08/17/22"},{"sku":27539,"date":"08/17/22"},{"sku":27538,"date":"08/17/22"},{"sku":27536,"date":"08/18/22"},{"sku":27535,"date":"08/18/22"},{"sku":27534,"date":"08/18/22"},{"sku":27533,"date":"08/18/22"},{"sku":27532,"date":"08/18/22"},{"sku":27531,"date":"08/18/22"},{"sku":27530,"date":"08/18/22"},{"sku":27529,"date":"08/18/22"},{"sku":27528,"date":"08/18/22"},{"sku":27527,"date":"08/18/22"},{"sku":27464,"date":"08/18/22"},{"sku":27458,"date":"08/18/22"},{"sku":27456,"date":"08/18/22"},{"sku":27454,"date":"08/18/22"},{"sku":27360,"date":"08/18/22"},{"sku":27350,"date":"08/18/22"},{"sku":27348,"date":"08/18/22"},{"sku":27344,"date":"08/18/22"},{"sku":27297,"date":"08/18/22"},{"sku":27296,"date":"08/18/22"},{"sku":27295,"date":"08/18/22"},{"sku":27256,"date":"08/18/22"},{"sku":27216,"date":"08/18/22"},{"sku":27214,"date":"08/18/22"},{"sku":27161,"date":"08/18/22"},{"sku":27150,"date":"08/18/22"},{"sku":27149,"date":"08/18/22"},{"sku":27069,"date":"08/18/22"}]}

    for i in fruit_names:
        i.islisted=True
        i.listingdate = datetime.now()
        for iss in dic["idlist"]:
            if iss['sku'] == i.sku:
                i.listingdate = datetime.strptime(iss['date'],"%x") 
    db.session.add_all(fruit_names)
    db.session.commit()
    return "meh"

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