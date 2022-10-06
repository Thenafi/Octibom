import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()


def imagecheck(url):
    res = requests.get(url)
    if res.ok:
        return True
    else:
        return False


def stringogen(item):
    if type(item) is list:
        return ",".join(item)
    elif type(item) is str:
        item.split(",")
    elif item == None:
        return None
    else:
        print(item, type(item))
        return "Something Went Wrong array maker"


def occasion_finder(input_strng_st, occasion_list):
    _list = []
    input_strng = str(input_strng_st).lower()
    for word in occasion_list:
        if word.lower() in input_strng:
            _list.append(word)
        elif (
            "valentine" in input_strng
            or "valentines" in input_strng
            or 'valentine"s' in input_strng
        ):
            _list.append("Valentine's Day")
        elif (
            "fathers day" in input_strng
            or "father" in input_strng
            or 'father"s' in input_strng
        ):
            _list.append("Father's Day")
        elif (
            "mothers day" in input_strng
            or "mother" in input_strng
            or 'mother"s' in input_strng
        ):
            _list.append("Mother's Day")
        elif (
            "pregnancy" in input_strng
            or "new baby" in input_strng
            or "pregnancy annoucement" in input_strng
        ):
            _list.append("New Baby & Christenings")
    return set(_list)


def scraping(sku):
    print(sku)
    res = requests.get(f"{os.environ.get('BASE_URL')}/AddProdut2.php?ProductID={sku}")
    data = {
        "sku": sku,
        "report": [],
    }
    if res.ok:
        soup_values = [
            i["value"]
            for i in BeautifulSoup(res.content, "html.parser").find_all("input")
        ]
        data["description"] = str(
            BeautifulSoup(res.content, "html.parser").find_all("textarea")[0]
        )[10:-11]
        data["name"] = soup_values[2]
        data["source"] = BeautifulSoup(res.content, "html.parser").body
        if len(soup_values[2]) > 3:
            data["list_of_urls"] = [soup_values[i] for i in range(9, 15)]
            # [soup_values[i] for i in range(46,50)]
            checked_list = [imagecheck(i) for i in data["list_of_urls"]]
            if not all(checked_list):
                data["report"].append("Image Not Ok")
            else:
                data["report"] = None
        else:
            data["report"].append("Issue With Title")

    else:
        data["report"].append("Something Wrong With Design Claim")

    return data
