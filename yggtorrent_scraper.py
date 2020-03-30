"""
Program Flow:
1. Get all the links including new ones and export them into json file
"""


from cfscrape import create_scraper, urlparse
from fake_useragent import UserAgent
from urllib.parse import parse_qs
from bs4 import BeautifulSoup as BS
from time import sleep
from json import dump, load
from tqdm import tqdm
from pathlib import Path


class MyURL():
    def __init__(self, url):
        self.p = urlparse(url)

        self.full_url = self.p.geturl()
        self.hostname = self.p.hostname
        self.query = self.p.query
        self.path = self.p.path

        if "page" in parse_qs(self.p.query).keys():
            self.page = parse_qs(self.p.query)["page"][0]
        else:
            self.page = 0

        self.hpath = Path(f"{self.hostname}_page_{self.page}")

    # _replace accepts arguments in a form key=value
    # **kwargs handles key=value as is

    def replace(self, **kwargs):
        self.p = self.p._replace(**kwargs)

        return MyURL(self.p.geturl())


def save_html(html, fname):
    with open(fname, "wb") as f:
        f.write(html)


def open_html(fname):
    with open(fname, "rb") as f:
        return f.read()


def get_page(url, fname, save=True):
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random
    }
    fpath = Path(fname)

    if fpath.exists():
        doc = open_html(fname)
    else:
        cf = create_scraper()
        r = cf.get(url, headers=headers)
        doc = r.content

        if save:
            save_html(r.content, fname)

    return doc


def clean_data(data):
    d_set = set(tuple(d.items()) for d in data)
    new_data = [{k: v for k, v in t} for t in d_set]

    return new_data


def parse_entries(entries, page_url, data):

    t_path = page_url.path
    t_query = page_url.query
    page = page_url.page

    for entry in entries:
        d = {}

        rel_link = entry.select_one("a[id=torrent_name]")["href"]
        post_url = page_url.replace(path=rel_link, query="")
        name = entry.select_one("a[id=torrent_name]").text.strip()

        if len(name) >= 70:
            name = name[:71]

        safe_name = "".join([x for x in name if x not in "\\/?><|\":?%*"])
        size = entry.select_one("td:nth-of-type(6)").text.strip()
        cat = entry.select_one("td:nth-of-type(1)").text.strip()
        comments = entry.select_one("td:nth-of-type(4)").text.strip()

        if cat == "2173":
            category = "windows"
        elif cat == "2172":
            category = "macos"
        elif cat == "2174":
            category = "mobile"
        elif cat == "2176":
            category = "tutorials"
        else:
            category = "others"

        d["url"] = post_url.full_url
        d["name"] = f"{safe_name}_{size}"
        d["size"] = size
        d["cat"] = category
        d["comment"] = comments
        d["page"] = page

        data.append(d)
        new_data = clean_data(data)

        with open(f"{page_url.hostname}_posts.json", "w") as fo:
            dump(new_data, fo, ensure_ascii=False)

        get_page(d["url"], d["name"], save=True)

        sleep(5)

    page_url = page_url.replace(path=t_path, query=t_query)

    return data

    print(f"{page_url.full_url}")
    sleep(10)


def get_posts():

    home_url = ("https://www2.yggtorrent.me/engine/search?"
                "name=&description=&file=&uploader=&category=2144"
                "&sub_category=all&do=search&attempt=1")

    url = MyURL(home_url)
    hpath = url.hpath
    data_path = Path(f"{url.hostname}_posts.json")

    try:
        doc = get_page(url.full_url, hpath, save=True)
    except Exception as e:
        with open("error.log", "a") as f:
            f.write(f"{e}\n")

    html = BS(doc, "html.parser")
    next_page = html.find_all("a", string="suivante →", limit=1)
    page_count = 1
    pbar = tqdm(total=200)
    data = []

    if data_path.exists():
        with open(data_path, "r") as fd:
            data = clean_data(load(fd))

    try:
        while next_page:

            # Parsing current page html
            entries = html.select(".results > table > tbody > tr")
            parse_entries(entries, url, data)

            # Fetching next page html
            rel_next = min(next_page).get("href")
            rel_next = MyURL(rel_next).query
            url_next = url.replace(query=rel_next)
            url = url_next
            hpath = url.hpath

            doc = get_page(url.full_url, hpath, save=True)
            html = BS(doc, "html.parser")
            next_page = html.find_all("a", string="suivante →", limit=1)

            pbar.update(page_count)
            page_count += 1
            sleep(10)

    except Exception as e:
        with open("error.log", "a") as f:
            f.write(f"{e}\n")

    pbar.close()


def main():
    get_posts()


if __name__ == "__main__":
    main()
