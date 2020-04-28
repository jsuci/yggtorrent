from re import compile, sub
from pathlib import Path
from json import load


def mk_title(title):
    # removes _12.67Go
    fsize = compile(r"_\d+\..+")

    # removes double space
    fspace = compile(r"\s{2,}")

    # removes dot between a-z characters
    fdot = compile(r"(?<=[a-zA-Z])\.")

    fbracket = compile(r"\[[a-zA-Z +0-9_,-].+?(\]|\n)")

    fparenth = compile(r"")

    title = sub(fsize, "", title)
    title = sub(fdot, " ", title)
    # title = sub(fbracket, "", title).strip()
    # title = sub(fspace, " ", title)

    return title


def main():
    f_json = Path("www2.yggtorrent.se.json")

    with open(f_json, "r", encoding="utf-8") as f:
        data = load(f)

    for e in data:
        if (
            e["catergory"] == "windows"
            or e["catergory"] == "macos"
        ):
            title = mk_title(e["name"])

            with open("titles.txt", "a", encoding="utf-8") as f:
                f.write(f"{title}\n")


if __name__ == "__main__":
    main()
