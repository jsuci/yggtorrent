from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup as BS
from urllib.parse import urlparse, parse_qs, urlencode
from pathlib import Path
from json import load, dump
from tqdm import tqdm
from os import system
from sys import argv
from random import randint
from time import sleep


class ParseURL():
    def __init__(self, url_str):
        self.parse = urlparse(url_str)

        self.domain = self.parse.hostname
        self.url = self.parse.geturl()
        self.query = self.parse.query

        self.qs = parse_qs(self.query, keep_blank_values=True)

    def fname(self):
        if "page" in self.qs.keys():
            if len(self.qs["page"]) == 0:
                page = 0
            else:
                page = self.qs["page"][0]
        else:
            page = 0

        return f"{self.domain}_{page}"

    def replace_qs(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.qs.keys():
                self.qs[k] = v
            else:
                self.qs[k] = ""

        self.query = urlencode(self.qs, doseq=True)
        self.parse = self.parse._replace(query=self.query)

        self.url = self.parse.geturl()

        return ParseURL(self.url)


def clean_data(data):
    print("Cleaning data...")
    p = Path(".").glob("*")

    files = [x.name for x in p]
    names = [x["name"] for x in data]

    # Remove duplicate
    for d in data:
        count = names.count(d["name"])
        if count == 2:
            print(f"Removing duplicate entry {d['name']}")
            names.remove(d["name"])
            data.remove(d)

    # Remove non existent files
    for c, n in enumerate(names):
        if n not in files:
            print(f"Removing non-existent file {n}")
            data.remove(data[c])
            names.remove(n)

    return (names, data)


def process_entries(entries, p):
    data_path = Path(p.domain + ".json")
    sleep_time = randint(5, 10)

    if data_path.exists():
        with open(data_path, "r", encoding="utf-8") as fi:
            try:
                data = load(fi)
            except Exception:
                data = []
    else:
        data = []

    names, data = clean_data(data)

    for e in tqdm(entries):
        d = dict()

        t_name = e.select_one("#torrent_name").text.strip()
        s_name = "".join([
            x for x in t_name if x not in """\\/?><|":;'?%*,()"""])
        size = e.select_one("td:nth-of-type(6)").text.strip()
        link = e.select_one("a[id=torrent_name]")["href"]
        comments = e.select_one("td:nth-of-type(4)").text.strip()
        category = e.select_one("td:nth-of-type(1)").text.strip()
        page = p.qs["page"][0]

        if category == "2173":
            category = "windows"
        elif category == "2172":
            category = "macos"
        elif category == "2174":
            category = "mobile"
        elif category == "2176":
            category = "tutorials"
        else:
            category = "others"

        if len(s_name) > 70:
            s_name = s_name[:70] + f"_{size}"
        else:
            s_name = s_name + f"_{size}"

        d["name"] = s_name
        d["link"] = link
        d["size"] = size
        d["comments"] = comments
        d["catergory"] = category
        d["page"] = page

        e_path = Path(d["name"])

        if (names.count(d["name"]) == 0) and (not e_path.exists()):
            data.append(d)

            output_doc(link, d["name"])
        else:
            sleep_time = 1

        with open(data_path, "w", encoding="utf-8") as fo:
            dump(data, fo, ensure_ascii=False)

        sleep(sleep_time)


def output_doc(url_str, name_str):

    def open_browser(url):

        def check_element(driver):
            return driver.find_element_by_xpath(
                "//*[contains(text(), 'Just a moment...')]")

        options = webdriver.ChromeOptions()
        options.add_argument("window-size=50,20")

        d = webdriver.Chrome("chromedriver.exe", options=options)

        d.get(url)

        WebDriverWait(d, timeout=60).until_not(check_element)

        doc = d.page_source

        d.quit()

        return doc

    f_name = Path(name_str)

    if f_name.exists():
        with open(f_name, "r", encoding="utf-8") as f:
            doc = f.read()
    else:
        doc = open_browser(url_str)

        with open(f_name, "w", encoding="utf-8") as f:
            f.write(doc)

    html = BS(doc, "html.parser")

    return html


def current_url():
    f_path = Path("page.log")

    if f_path.exists():
        with open(f_path, "r", encoding="utf-8") as fi:
            for entry in fi:
                if "://" in entry:
                    url = entry.strip()
    else:
        url = input("Enter url: ")

    p = ParseURL(url)

    return p


def get_all_posts():

    def next_page(html):

        rel_obj = html.select_one("a[rel=next]")

        if rel_obj is not None:
            rel_next_url = ParseURL(rel_obj.get("href"))
        else:
            rel_next_url = None

        return rel_next_url

    prev_url = current_url()

    while prev_url:
        html = output_doc(prev_url.url, prev_url.fname())
        entries = html.select(".results > table > tbody > tr")
        process_entries(entries, prev_url)

        prev_url = next_page(html)


def get_current_post():
    p = current_url()

    p = p.replace_qs(page=0)

    html = output_doc(p.url, p.domain)
    entries = html.select(".results > table > tbody > tr")
    process_entries(entries, p)


def auto_start(opt):
    if len(argv) == 1:
        ret = 0
    else:
        ret = int(argv[1])

    if ret < 3:
        ret += 1
        try:
            if opt == "all":
                get_all_posts()
            else:
                get_current_post()
        except Exception as e:
            print(f"Error: {e}\nRestarting script...")
            system(f"python yggtorrent_scraper_all.py {ret} {opt}")
    else:
        return None


def main():
    # select "all" or "current"
    auto_start("current")


if __name__ == "__main__":
    main()
