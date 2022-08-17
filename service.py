from gettext import find
from typing import Set
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
load_dotenv()


def imagecheck (url):
    res = requests.get(url)
    if res.ok :
        return True
    else :
        return False

def stringogen(item):
    if type(item)== "Array":
        return ','.join(item)
    elif type(item) == "String":
        item.split(',')
    elif item == None:
        return None
    else :
        print("Something Went Wrong array maker")
        return "Something Went Wrong array maker"


def occasion_finder(input_strng_st, occasion_list):
    _list = []
    input_strng = str(input_strng_st).lower()
    for word in [i for i in occasion_list]:
        if input_strng.find(word.lower())>0:
            _list.append(word)
        elif input_strng.find("valentine") or input_strng.find('valentines') or input_strng.find('valentine"s'):
            _list.append("Valentine's Day")
        elif input_strng.find("fathers day") or input_strng.find('father') or input_strng.find('father"s'):
            _list.append("Father's Day")
        elif input_strng.find("mothers day") or input_strng.find('mother') or input_strng.find('mother"s'):
            _list.append("Mother's Day")
    return set(_list)

def scraping(sku):
    res = requests.get(f"{os.environ.get('BASE_URL')}/AddProdut2.php?ProductID={sku}")
    data = {"sku":sku, "report":[], }
    if res.ok:
        soup_values = [i['value'] for i in BeautifulSoup(res.content, "html.parser").find_all('input')]
        data['description'] =  str(BeautifulSoup(res.content, "html.parser").find_all('textarea')[0])[10:-11]
        data['name'] = soup_values[2]
        data["source"] = BeautifulSoup(res.content, "html.parser").body
        if len(soup_values[2]) > 3:
            data['list_of_urls'] = [soup_values[i] for i in range(9,15)]
            checked_list = [imagecheck(i) for i in data['list_of_urls']]
            if not all(checked_list):
                data['report'].append("Image Not Ok")
            else:
                data['report'] = None
        else :
            data['report'].append("Issue With Title")

    else :
        data['report'].append("Something Wrong With Design Claim")

    return data




