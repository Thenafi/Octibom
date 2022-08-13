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

def scraping(sku):
    res = requests.get(f"{os.environ.get('BASE_URL')}/AddProdut2.php?ProductID={sku}")
    data = {"sku":sku}
    if res.ok:
        soup_values = [i['value'] for i in BeautifulSoup(res.content, "html.parser").find_all('input')]
        data['description'] =  BeautifulSoup(res.content, "html.parser").find_all('textarea')[0]
        data['name'] = soup_values[2]
        if len(soup_values[2]) > 3:
            data['list_of_urls'] = [soup_values[i] for i in range(9,15)]
            checked_list = [imagecheck(i) for i in data['list_of_urls']]
            if not all(checked_list):
                data['report'] =  "Image Not Ok"
            else:
                data['report'] = None
        else :
            data['report'] =  "Issue With Title"

    else :
        data['report'] =  "Something Wrong With Design Claim"

    return data


