from re import compile, sub, I
from csv import DictWriter
from pathlib import Path
from json import load, dumps
from random import choice, shuffle, sample
from requests_html import HTML
from requests import post
from base64 import b64encode
from datetime import datetime
from time import sleep


def mk_rt_title(title):
    # removes _12.67Go
    fsize = compile(r"_\d+\..+")

    # removes ({[]}) characters
    fbracket = compile(r"[\[][a-zA-Z +0-9_,-\.].*?(?:[\]]|$)")
    fparenth = compile(r"[\(][a-zA-Z +0-9_,-\.].*?(?:[\)]|$)")
    fcurly = compile(r"[\{][a-zA-Z +0-9_,-\.].*?(?:[\}]|$)")

    fenclose = compile(r"^[\{\[\(]|[\}\]\)]|[\{\[\(]$")

    # remove custom strings
    fcustom = compile(
        r"(?:.PARAND.|R2R|P2P|RiTUELiSO|MAGNETRiXX|AMPED|KAYPA|H4S5S|"
        r"X\SFORCE|XFORCE|.RADIXX11.|.ONHAX.|ASTRA|D\SFOX|BOBY15000|"
        r"CASHMERE|by|LAXiTY|SYNTHiC4TE|0TH3Rside|NGEN|TSRh|WZTEAM|"
        r"Radixx11|.PARAND|No tag|part\d|TNT|\sCr$| l |SCHiZO)", flags=I)

    # removes extra spaces
    fspace = compile(r"\s{2,}")
    ftrim = compile(r"^\s|\s$")

    # removes extra characters
    fchar = compile(r"&|\+|\,|-{2,}|\_")

    # removes period in between words
    fdot1 = compile(r"(?<=[a-zA-Z. ])\.|^\.|\.$")
    fdot2 = compile(r"(?<=\d)\.(?=[a-zA-Z])")

    # removes DVDR word
    fdvdr = compile(r" DVDR .+|DVD\d")

    # removes \s-|\s–
    fdash = compile(r"\s-|\s–|-$")

    # removes macOS-eng
    fmaceng = compile(r"(?<=macOS)|(?<=macOSX)_|-(?=ENG-)", flags=I)

    # removes last letter
    flastch = compile(r"\s[a-wA-WyYzZ]$")

    # change english to french
    feng1 = compile(r"ENGLISH", flags=I)
    feng2 = compile(r"(\s|-|_)eng|engl(\s|-|_|$)", flags=I)

    # change pre-activated-
    fpre = compile(r"Pre-Activated-", flags=I)

    # change Anglais to Francais
    fang = compile(r"Anglais", flags=I)

    title = sub(fsize, "", title)
    title = sub(fbracket, "", title)
    title = sub(fparenth, "", title)
    title = sub(fcurly, "", title)
    title = sub(fchar, " ", title)
    title = sub(fenclose, "", title)

    title = sub(fdot1, " ", title)
    title = sub(fdot2, " ", title)

    title = sub(fdvdr, " ", title)
    title = sub(fmaceng, " ", title)
    title = sub(flastch, "", title)
    title = sub(feng1, "FRENCH", title)
    title = sub(feng2, " FR ", title)
    title = sub(fpre, "Pre-Activated", title)
    title = sub(fang, "Français", title)
    title = sub(fcustom, "", title)
    title = sub(fdash, " ", title)

    title = sub(fspace, " ", title)
    title = sub(ftrim, "", title)

    if len(title) > 0 and title[-1] == "-":
        title = title.replace("-", "")

    t_strip = title.split(" ")

    if len(t_strip) >= 7:
        cut = 8
        t_strip = t_strip[:cut]
        while len(t_strip[-1]) == 1:
            cut -= 1
            t_strip = t_strip[:cut]

    rt_title = " ".join(t_strip)

    return rt_title


def mk_kw_title(title):
    first = choice([
        "crack", "cracked", "précracké", "pré cracké", "full crack"])
    last = choice([
        "clé de produit", "clé activation",
        "licence", "pré activé", "keygen", "activator",
        "activated", "patch", "serial key"
        "license key", "product key", "patched",
        "active", "license", "serial"])

    lang = choice(["fr", "french", "français"])

    if "crack" in title:
        mk_list = [last, lang]
    else:
        mk_list = [first, last, lang]

    shuffle(mk_list)
    mk_shuffle = " ".join(mk_list)
    mk_kw_title = f"{title} {mk_shuffle.title()}"

    return mk_kw_title


def mk_content(name, mk_title, os, size):

    def dl_link(pname, size):
        domain = "https://jaimelogiciel.com/download.php"
        date = choice(range(2, 6))
        fname = pname.replace(" ", "_")

        link = (f"{domain}?name={fname}.rar"
                f"&size={size}&date=il y a {date} jours").replace(" ", "%20")

        return link

    def table_schema(os, pname, size, dlink):
        rating_c = str(choice(range(470, 500)) / 100)
        fname = f"{pname}.rar".replace(" ", "_")

        schema = {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": pname,
            "operatingSystem": os,
            "applicationCategory": "UtilitiesApplication",
            "fileSize": size,
            "offers": {
                "@type": "Offer",
                "availability": "InStock",
                "price": "00.00",
                "priceCurrency": "USD"
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": rating_c,
                "reviewCount": "[reviews]"
            },
            "installUrl": dlink
        }

        schema = dumps(schema, ensure_ascii=False)

        html_schema = (
            f"""<div style='text-align: center;'>"""
            f"""<script type='application/ld+json'>{schema}</script>"""
            f"""<div class='tg-wrap' style='display:inline-block;'>"""
            f"""<table class='tg'><tr>"""
            f"""<td class='tg-uzvj'>Nom de fichier : <br></td>"""
            f"""<td class='tg-9wq8'>{pname}</td></tr><tr>"""
            f"""<td class='tg-uzvj'>Taille du fichier : <br></td>"""
            f"""<td class='tg-9wq8'>{size}</td></tr><tr>"""
            f"""<td class='tg-uzvj'>Évaluation : <br></td>"""
            f"""<td class='tg-9wq8'>{rating_c} / 5 ([reviews] review(s))"""
            f"""</td></tr><tr><td class='tg-uzvj'>Plate-forme : <br></td>"""
            f"""<td class='tg-9wq8'>{os}</td></tr><tr>"""
            f"""<td class='tg-uzvj'>Télécharger : <br></td>"""
            f"""<td class='tg-9wq8'><a href='{dlink}' target='_blank'>"""
            f"""<u>{fname}</u></a>"""
            f"""</td></tr></table></div></div>"""
        )

        return html_schema

    def tags(name):
        all_kw = [name]

        k_one = ("""
        pour le partage de cette version du logiciel
        installation terminé activation ok tout est
        parfait torrent de l'instalation de windows
        taper ma clé d activation désinstallé le loader
        l'installer et l'activer avec un serial valide
        simple pour exécute premier boot après l'installation
        lors ce que l'assistant d'installation vous demande
        le nom d'utilisateur uploadeur fonctionne nickel et
        très complet avec de nombreux paramètres cette nouvelle
        version fonctionne très bien j'ai déjà téléchargé
        quelques vidéos avec fonctionnel et activé version optimisée sur
        lesquelles les logiciels standards de Microsoft et autres
        fonctionnent parfaitement installé votre version des
        performances avoir la version mac PC avec l'intégrité de la mémoire
        activée à jour de Windows 10  j'ai installé toute tes versions
        réinstaller toute les semaines activateurs générateur avec les
        logiciels""").replace("\n", "").split(" ")

        k_one = list(filter(lambda x: True if x else False, k_one))
        shuffle(k_one)
        all_kw.extend(sample(k_one, 20))

        k_two = ("""
        crack serial-key license license-key product product-key
        activation patch générateur activator gratuit telecharger
        full-version french francais fr complete multi language iso
        rar torrent exe winrar piratebay yggtorrent chinglui 64bit 32bit
        precrack cracked patched included with plus version installateur
        licence activateur pièce en-série numéro-de-série langue product-key
        logiciel extended nombre nouvelle-version code produit pour-mac
        pour-windows la-version licence OEM pro-version professional
        """).replace("\n", "").split(" ")

        k_two = list(filter(lambda x: True if x else False, k_two))
        k_two = list(map(lambda x: x.replace(
            "-", " ") if "-" in x else x, k_two))
        shuffle(k_two)
        all_kw.extend(sample(k_two, 20))

        k_three = ["crack", "serial key", "activated", "patch",
                   "generator", "product key", "license key",
                   "crack patch", "pre crack", "activated crack",
                   "license number", "license code", "product number"
                   "key generator"]
        shuffle(k_three)
        all_kw.extend(sample(k_three, 10))

        shuffle(all_kw)

        all_kw = " ".join(all_kw)

        tags = f"<p>{all_kw}</p>"

        return tags

    fpath = Path(name)
    pname = f"{mk_title}".title()

    with open(fpath, "r", encoding="utf-8", newline="") as f:
        html = HTML(html=f.read())

    # Remove /misc/safe_redirect
    fmisc = compile(r"\/misc\/safe_redirect\?url=[a-zA-Z0-9=]+")

    # Remove repeating symbols
    fsym = compile(r"[\*\-_— ]{10,}")

    # Fix image tags
    fimg = compile(r"(\[img.+\])(https:.+)(\[\/img\])")

    # Geth the main content
    r_content = html.xpath(
        "//section/div[@class='default']")

    r_comments = html.xpath("//div[@class='message']")

    if len(r_content) != 0:
        r_content = r_content[0].html.replace("\n", "")
        r_content = r_content.replace("https://images.weserv.nl/?url=", "")
        r_content = sub(fmisc, "#", r_content)
        r_content = sub(fsym, "", r_content)

        res = fimg.search(r_content)

        if res:
            r_content = r_content.replace(res[1], "<img src=\"")
            r_content = r_content.replace(res[3], "\"/>")

        # Generate schema
        dlink = dl_link(pname, size)
        schema = table_schema(os, pname, size, dlink)
        ctags = tags(pname)

        f_content = f"{r_content}{schema}{ctags}"

        # Generate comments
        f_comments = []
        for comment in r_comments:
            comm = {}
            comm_id = comment.xpath("//div[@class='message']/@id")[0]
            comm_auth = comment.xpath("//a/text()")[0]
            comm_msg = comment.xpath(
                "//span[@id='comment_text']/text()")[0].strip()

            comm["comm_id"] = comm_id
            comm["comm_auth"] = comm_auth
            comm["comm_msg"] = comm_msg

            f_comments.append(comm)

        return f_content, f_comments


def pr_entry(data):
    d = {}
    f_pos_title = Path("pos_title.txt")
    f_pos_num = Path("pos_num.txt")

    if f_pos_num.exists():
        with open(f_pos_num, "r") as f:
            pos_str = f.read()

            if pos_str == "":
                pos = 0
            else:
                pos = int(pos_str)
    else:
        with open(f_pos_num, "w") as f:
            f.write("0")
        pos = 0

    if f_pos_title.exists():
        with open(f_pos_title, "r") as f:
            posted_titles = list(map(lambda x: x.strip(), f))
    else:
        with open(f_pos_title, "w") as f:
            f.write("")
        posted_titles = []

    e = data[pos]

    while True:
        pos += 1
        e = data[pos]

        if (
            e["catergory"] == "windows"
            or e["catergory"] == "macos"
        ):
            name = e["name"]
            os = e["catergory"]
            size = e["size"]

            rt_title = mk_rt_title(name)
            rt_title_low = rt_title.lower()

            # Filter duplicates here
            if rt_title_low not in posted_titles:

                # For titles
                mk_title = mk_kw_title(rt_title)
                d["rt_title"] = rt_title
                d["mk_title"] = mk_title

                # For content and comments
                content, comments = mk_content(name, mk_title, os, size)
                d["content"] = content
                d["comments"] = comments
                d["post_count"] = pos

                return d


def post_wp(c):
    f_post_content = Path("pos_content.csv")
    f_post_comment = Path("pos_comm.txt")
    f_pos_title = Path("pos_title.txt")
    f_pos_num = Path("pos_num.txt")

    # Login and authentication
    usr_pass = b"jaimelogiciel:rugbyel.traje@d3_bano"
    token = b64encode(usr_pass).decode()
    headers = {
        "Authorization": f"Basic {token}"
    }

    # Post content
    if f_post_comment.exists():
        with open(f_post_comment, "r") as f:
            comm_ids = list(map(lambda x: x.strip(), f))
    else:
        with open(f_post_comment, "w") as f:
            f.write("")
            comm_ids = []

    post_endpoint = "https://jaimelogiciel.com/wp-json/wp/v2/posts"
    params = {
        "title": c["mk_title"],
        "content": c["content"],
        "status": "publish"
    }
    post_r = post(post_endpoint, headers=headers, json=params)
    post_id = post_r.json()["id"]
    post_title = post_r.json()["title"]["rendered"]

    c["post_id"] = post_id
    c["post_count"] += 1

    # Post comments
    comm_endpoint = "https://jaimelogiciel.com/wp-json/wp/v2/comments"

    if len(c["comments"]) >= 5:
        samp_comments = sample(c["comments"], choice(range(3, 5)))
    else:
        samp_comments = c["comments"]

    for e_comment in samp_comments:
        comm_id = e_comment["comm_id"]

        if comm_id not in comm_ids:
            comm_auth = e_comment["comm_auth"]
            comm_msg = e_comment["comm_msg"]

            r_month = choice(range(1, 12))
            r_day = choice(range(1, 30))
            r_year = datetime.now().year - 1

            comm_params = {
                "author_name": comm_auth,
                "author_email": f"{comm_auth}@gmail.com",
                "content": comm_msg,
                "status": "approve",
                "date": f"{r_year}-{r_month:0>2}-{r_day:0>2}T10:00:00",
                "post": post_id
            }

            post_comm = post(comm_endpoint, headers=headers, json=comm_params)

            with open(f_post_comment, "a") as f:
                f.write(f"{comm_id}\n")
        else:
            print(f"{comm_id} exits.")


    # Export entries
    with open(f_post_content, "a+", newline="",
              encoding="utf-8") as f:

        fieldnames = ["rt_title", "mk_title",
                      "content", "comments",
                      "post_count", "post_id"]
        writer = DictWriter(
            f, fieldnames=fieldnames, delimiter="$")

        writer.writerow(c)

    with open(f_pos_title, "a", encoding="utf-8") as f:
        f.write(f"{c['rt_title'].lower()}\n")

    with open(f_pos_num, "w") as f:
        f.write(f"{c['post_count']}")

    print(f"{post_title} posted.")


def main():
    f_json = Path("www2.yggtorrent.se.json")
    f_csv = Path("post_content.csv")

    with open(f_json, "r", encoding="utf-8") as f:
        data = load(f)

    content = pr_entry(data)
    post_wp(content)


if __name__ == "__main__":
    main()
