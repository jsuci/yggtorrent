from re import compile, sub, I
from csv import DictWriter
from pathlib import Path
from json import load
from random import choice


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
        r"Radixx11|.PARAND|No tag|part\d|TNT|\sCr$| l )", flags=I)

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
    title = sub(fdash, " ", title)
    title = sub(fcustom, "", title)

    title = sub(fspace, " ", title)
    title = sub(ftrim, "", title)

    t_strip = title.split(" ")

    if len(t_strip) >= 7:
        t_strip = t_strip[:8]

    # if len(tr_strip[-1]) == 1:
    #     return tr_strip

    # while len(t_strip[c_end]) == 1:
    #     print(t_strip)

    # rt_title = " ".join(t_strip)
    # else:
    #     rt_title = " ".join(t_strip)

    return t_strip


def mk_kw_title(title):
    second = choice([
        "crack", "multi-crack", "précracké", "pré cracké"])
    last = choice([
        "clé de produit", "clé activation",
        "licence", "pré-activé", "keygen", "activator", "activated",
        "patch", "français", "patch"])


def main():
    f_json = Path("www2.yggtorrent.se.json")
    f_csv = Path("post_content.csv")

    with open(f_json, "r", encoding="utf-8") as f:
        data = load(f)

    all_data = []

    for e in data:
        d = {}

        if (
            e["catergory"] == "windows"
            or e["catergory"] == "macos"
        ):
            rt_title = mk_rt_title(e["name"])
            all_data.append(rt_title)

    with open("titles.txt", "w", encoding="utf-8") as f:
        for d in all_data:
            f.write(f"{d}\n")

    #         kw_title = mk_kw_title(rt_title)

    #         d["rt_title"] = rt_title

    #         all_data.append(d)

    # with open(f_csv, "w", encoding="utf-8", newline="") as f:
    #     fieldnames = ["rt_title"]
    #     writer = DictWriter(f, fieldnames=fieldnames)

    #     writer.writeheader()

    #     for d in all_data:
    #         writer.writerow(d)


if __name__ == "__main__":
    main()
