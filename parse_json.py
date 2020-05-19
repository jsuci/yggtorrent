from re import compile, sub, I
from csv import DictWriter
from pathlib import Path
from json import load, dumps
from random import choice
from requests_html import HTML


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
    fchar = compile(r"\+|\,|-{2,}|\_")

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
        "crack", "multi-crack", "précracké", "pré cracké"])
    last = choice([
        "clé de produit", "clé activation",
        "licence", "pré-activé", "keygen", "activator", "activated",
        "patch", "français", "patch"])

    if "crack" in title:
        mk_title = f"{title} {last.title()}"
    else:
        mk_title = f"{title} {first.title()} {last.title()}"

    return mk_title


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
        review_c = str(choice(range(1, 3)))
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
                "reviewCount": review_c
            },
            "installUrl": dlink
        }

        schema = dumps(schema, ensure_ascii=False)

        html_schema = (
            f"""<script type='application/ld+json'>{schema}</script>"""
            f"""<div class='tg-wrap' style='display:inline-block;'>"""
            f"""<table class='tg'><tr>"""
            f"""<td class='tg-uzvj'>Nom de fichier : <br></td>"""
            f"""<td class='tg-9wq8'>{pname}</td></tr><tr>"""
            f"""<td class='tg-uzvj'>Taille du fichier : <br></td>"""
            f"""<td class='tg-9wq8'>{size}</td></tr><tr>"""
            f"""<td class='tg-uzvj'>Évaluation : <br></td>"""
            f"""<td class='tg-9wq8'>{rating_c} / 5 ([reviews])"""
            f"""</td></tr><tr><td class='tg-uzvj'>Plate-forme : <br></td>"""
            f"""<td class='tg-9wq8'>{os}</td></tr><tr>"""
            f"""<td class='tg-uzvj'>Télécharger : <br></td>"""
            f"""<td class='tg-9wq8'><a href='{dlink}' target='_blank'>"""
            f"""<u>{fname}</u></a>"""
            f"""</td></tr></table></div>"""
        )

        return html_schema

    fpath = Path(name)
    pname = f"{mk_title}".title()

    with open(fpath, "r", encoding="utf-8", newline="") as f:
        html = HTML(html=f.read())

    # Remove /misc/safe_redirect
    fmisc = compile(r"\/misc\/safe_redirect\?url=[a-zA-Z0-9=]+")

    r_content = html.xpath(
        "//section/div[@class='default']")

    if len(r_content) != 0:
        r_content = r_content[0].html.replace("\n", "")
        r_content = r_content.replace("https://images.weserv.nl/?url=", "")
        r_content = sub(fmisc, "#", r_content)

        # Generate schema
        dlink = dl_link(pname, size)
        schema = table_schema(os, pname, size, dlink)

        r_content = (f"{r_content}<div style='text-align: center;'>"
                     f"{schema}</div>")

        return r_content


def pr_entry(data):
    d = {}
    f_pos_title = Path("pos_title.txt")
    f_pos_num = Path("pos_num.txt")
    f_post_content = Path("post_content.csv")

    if f_pos_num.exists():
        with open(f_pos_num, "r") as f:
            pos = int(f.read())
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

            # Filter duplicates here
            if rt_title not in posted_titles:

                # For titles
                mk_title = mk_kw_title(rt_title)
                d["rt_title"] = rt_title
                d["mk_title"] = mk_title

                # For content
                content = mk_content(name, mk_title, os, size)
                d["content"] = content

                print(f"posting {rt_title}")

                # Update posted titles
                with open(f_pos_title, "a", encoding="utf-8") as f:
                    f.write(f"{rt_title}\n")

                # Export to csv
                with open(f_post_content, "a", newline="",
                          encoding="utf-8") as f:
                    fieldnames = ["rt_title", "mk_title", "content"]
                    writer = DictWriter(
                        f, fieldnames=fieldnames, delimiter="$")

                    writer.writeheader()
                    writer.writerow(d)

                # Update posted number
                with open(f_pos_num, "w") as f:
                    pos += 1
                    f.write(f"{pos}")

                return d


def main():
    f_json = Path("www2.yggtorrent.se.json")
    f_csv = Path("post_content.csv")

    with open(f_json, "r", encoding="utf-8") as f:
        data = load(f)

    pr_entry(data)


if __name__ == "__main__":
    main()
