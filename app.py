from datetime import datetime
import re
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from pantry_wrapper import *
import os
from service import *

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()
app = Flask(__name__)

mysql = os.environ.get("MYSQL")

app.config["SQLALCHEMY_DATABASE_URI"] = mysql
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Info(db.Model):
    sku = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80), nullable=False)
    islisted = db.Column(db.Boolean, default=False, nullable=False)
    isproblem = db.Column(db.Boolean, default=False, nullable=False)
    listingdate = db.Column(db.DateTime, default=None)
    problem = db.Column(db.String(250), default=None)
    prodlem_josn = db.Column(db.JSON, default=None)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/render")
def render():
    return render_template("render.html")


@app.route("/IDmaker")
def IDmaker():
    return render_template("regex.html")


@app.route("/datacreator", methods=["POST", "GET"])
def datacreator():
    if request.method == "GET":
        return render_template("datacreator.html")
    if request.method == "POST":
        result = {
            "success": 0,
            "allreadyexsts": 0,
            "failed": 0,
            "failed_id": [],
            "existingid": [],
        }
        skulist = [int(i) for i in re.findall("(\d+)", request.form["idboxname"])]
        skulist.sort()
        result["totalid"] = len(skulist)
        category = request.form["catboxname"]
        objects = []
        for e, i in enumerate(skulist):
            print(e, end="\r")
            if Info.query.get(i) is None:
                single_product = Info(sku=i, category=category)
                scraaped_info = scraping(i)

                if scraaped_info["report"] is not None:
                    single_product.isproblem = True
                    single_product.problem = stringogen(scraaped_info["report"])
                    result["failed"] += 1
                    result["failed_id"].append(i)
                else:
                    result["success"] += 1
                objects.append(single_product)
            else:
                result["allreadyexsts"] += 1
                result["existingid"].append(i)

        db.session.add_all(objects)
        db.session.commit()
        return result


@app.route("/get_listing")
@app.route("/get_listing/")
@app.route("/get_listing/<cat>")
def get_listing(cat=None):
    if cat:
        single_product = Info.query.filter_by(
            islisted=False, isproblem=False, category=cat
        ).first()
    else:
        single_product = Info.query.filter_by(islisted=False, isproblem=False).first()

    if single_product is not None:
        url = f"/listing/{single_product.sku}"
        return redirect(url)
    else:
        return "No Listing"


@app.route("/get_listing_etsy")
@app.route("/get_listing_etsy/")
@app.route("/get_listing_etsy/<cat>")
def get_listing_etsy(cat=None):
    if cat:
        single_product = Info.query.filter_by(
            islisted=False, isproblem=False, category=cat
        ).first()
    else:
        single_product = Info.query.filter_by(islisted=False, isproblem=False).first()

    if single_product is not None:
        sku = single_product.sku
        scraaped_info = scraping(sku)
        if scraaped_info["report"] != None:
            single_product = Info.query.get(sku)
            single_product.isproblem = True
            single_product.problem = stringogen(scraaped_info["report"])
            db.session.commit()
            url = f"/get_listing_etsy/{cat}"
            return redirect(url)
        url = f"http://192.168.123.77/sitex/ListingManager/amazon/AddProdut.php?ProductID={single_product.sku}"
        return redirect(url)
    else:
        return "No Listing"


@app.route("/listing/<sku>")
def get_single_listing(sku):
    single_product = Info.query.get(sku)
    key_feature = request.args.get("key1")
    key_feature2 = request.args.get("key2")
    key_feature3 = request.args.get("key3")

    if single_product is None:
        return "Not Listed"
    else:
        scraaped_info = scraping(sku)
        scraaped_info["total_occasions"] = []
        scraaped_info["occasions_present"] = list(
            occasion_finder(
                scraaped_info["name"] + " " + scraaped_info["description"],
                scraaped_info["total_occasions"],
            )
        )
        scraaped_info["done"] = single_product.islisted
        scraaped_info["category"] = single_product.category
        scraaped_info[
            "extra_image"
        ] = f"https://www.qfonic.com/images/products/{sku}/image07_2000.jpg"
        scraaped_info["key_features"] = [key_feature, key_feature2, key_feature3]

        return render_template("listing.html", data=scraaped_info)


@app.route("/done_listing/<sku>", methods=("GET", "POST"))
def done_listing(sku):
    single_product = Info.query.get(sku)
    if request.method == "POST":
        content = request.form["content"]
        single_product.prodlem_josn = content
        db.session.commit()
        return render_template("done.html", data=str(content))

    else:
        if single_product is None:
            return "Not Listed"
        else:
            single_product.islisted = True
            single_product.listingdate = datetime.now()
        db.session.commit()
        return render_template("done.html", data=str("Listing Added"))


# app the problem pathaile always array patha the hobe strinogen er bhitore
@app.route("/issue/<sku>")
def issue(sku):
    single_product = Info.query.get(sku)
    if single_product is None:
        return "Not Listed"
    elif single_product.isproblem:
        return "Issue already added"
    else:
        single_product.isproblem = True
        if single_product.problem == None:
            single_product.problem = stringogen(["Manual Issue"])
        else:
            single_product.problem = stringogen(
                stringogen(single_product.problem).append("Manual Issue")
            )
        db.session.commit()
        return render_template("done.html", data="Issue Added")


@app.route("/notlisted/<sku>")
def notlisted(sku):
    single_product = Info.query.get(sku)
    if single_product is None:
        return "This SKU is Listed"
    else:

        if single_product.islisted == False:
            return render_template("done.html", data="This Not Listed Yet")
        else:
            single_product.islisted = True
            db.session.commit()
            return render_template(
                "done.html", data="Listing Info Update to not listed"
            )


@app.route("/setallaslisted")
def setallaslisted():
    fruit_names = Info.query.all()
    dic = {}
    for i in fruit_names:
        i.islisted = True
        i.listingdate = datetime.now()
        # for iss in dic["idlist"]:
        #     if iss["sku"] == i.sku:
        #         i.listingdate = datetime.strptime(iss["date"], "%x")
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
    todays_datetime = datetime(
        datetime.today().year, datetime.today().month, datetime.today().day
    )
    list_of_products = Info.query.filter(Info.listingdate >= todays_datetime).all()
    totaldone = Info.query.filter_by(islisted=True).all()
    addedindatabse = Info.query.all()
    return render_template(
        "done.html", data=[len(list_of_products), len(totaldone), len(addedindatabse)]
    )


@app.route("/listingtable")
def listingtable():
    page = request.args.get("page", 1, type=int)
    pagination = (
        Info.query.filter_by(islisted=True)
        .order_by(Info.listingdate.desc())
        .paginate(page, per_page=100)
    )
    return render_template("listingtable.html", pagination=pagination)


@app.route("/listingtable2")
def listingtable2():
    return redirect(url_for("listingtable"))


if __name__ == "__main__":
    app.run(host="0.0.0.0")
