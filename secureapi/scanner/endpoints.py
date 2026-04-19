import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_endpoints(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        links = set()
        for tag in soup.find_all("a", href=True):
            links.add(urljoin(url, tag["href"]))

        return list(links)

    except Exception as e:
        return {"error": str(e)}