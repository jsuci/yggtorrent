from cfscrape import create_scraper, Session
from cfscrape import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from fake_useragent import UserAgent
from bs4 import BeautifulSoup as BS
from urllib.parse import urlparse, parse_qs, urlencode
from time import sleep
from pathlib import Path
from json import load, dump
from tqdm import tqdm
from sys import exit
from atexit import register


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
                print("Key not found.")

        self.query = urlencode(self.qs, doseq=True)
        self.parse = self.parse._replace(query=self.query)
        self.url = self.parse.geturl()

        return ParseURL(self.url)


def process_entries(entries, index_url_str):
    p = ParseURL(index_url_str)
    data_path = Path(p.domain + ".json")
    data = []
    sleep_time = 10

    if len(p.qs["page"][0]) == 0:
        page = 0
    else:
        page = p.qs["page"][0]

    # print(f"Processing page {page}")

    if data_path.exists():
        # print("Reading exisitng data.")

        with open(data_path, "r", encoding="utf-8") as fi:
            try:
                data = load(fi)
            except Exception:
                data = []

    names = [x["name"] for x in data]

    for e in tqdm(entries):
        d = dict()

        name = e.select_one("#torrent_name").text.strip()
        name = "".join([x for x in name if x not in "\\/?><|\":?%*"])
        size = e.select_one("td:nth-of-type(6)").text.strip()
        link = e.select_one("a[id=torrent_name]")["href"]
        comments = e.select_one("td:nth-of-type(4)").text.strip()
        category = e.select_one("td:nth-of-type(1)").text.strip()

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

        if len(name) > 70:
            name = name[:71] + f"_{size}"
        else:
            name = name + f"_{size}"

        d["name"] = name
        d["link"] = link
        d["size"] = size
        d["comments"] = comments
        d["catergory"] = category
        d["page"] = page

        e_path = Path(name)

        if d["name"] in names or e_path.exists():
            if d["name"] not in names:
                # print("Adding entry.")
                data.append(d)
                with open(data_path, "w", encoding="utf-8") as fo:
                    dump(data, fo, ensure_ascii=False)

            if not e_path.exists():
                # print("Exporting page.")
                get_page(link, name)
                sleep_time = 10
            else:
                sleep_time = 1

        else:
            data.append(d)
            with open(data_path, "w", encoding="utf-8") as fo:
                dump(data, fo, ensure_ascii=False)

            get_page(link, name)
            sleep_time = 10

        sleep(sleep_time)


def get_page(url_str, name_str):

    u = ParseURL(url_str)
    f_name = Path(name_str)

    if f_name.exists():
        with open(f_name, "rb") as f:
            doc = f.read()

    if not f_name.exists() or len(doc) == 0:
        ua = UserAgent()
        cf = Session()
        retries = Retry(total=10, backoff_factor=1)
        headers = {"User-Agent": ua.random}
        cf.mount(u.parse.scheme, HTTPAdapter(max_retries=retries))
        cfs = create_scraper(sess=cf)
        r = cfs.get(url_str, headers=headers)

        doc = r.content

        with open(f_name, "wb") as f:
            f.write(doc)

    return doc


def next_page(url_str):

    p = ParseURL(url_str)
    p = p.replace_qs(attempt=1)

    doc = get_page(p.url, p.fname())

    # Parsing index
    html = BS(doc, "html.parser")
    rel_obj = html.select("a[rel=next]")

    if len(rel_obj) != 0:
        rel_next_url = rel_obj[0].get("href")
        return (html, rel_next_url)
    else:
        return (None, None)


def get_posts():
    try:

        def export_log():
            with open(f_path, "w") as f:
                f.write(f"{index}\n")

            get_posts()

        f_path = Path("page.log")

        if f_path.exists():
            with open(f_path, "r", encoding="utf-8") as fi:
                for entry in fi:
                    if "://" in entry:
                        index = entry.strip()
                        print(f"Processing {index}")
        else:
            index = input("Enter index / page url: ")

        register(export_log)

        html_index, rel_next = next_page(index)

        while rel_next:
            entry_index = html_index.select(".results > table > tbody > tr")
            process_entries(entry_index, index)

            index = rel_next
            html_index, rel_next = next_page(index)

    except Exception:
        exit(0)


def main():
    get_posts()


if __name__ == "__main__":
    main()
