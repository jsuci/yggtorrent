from json import loads, dumps
from requests import get


def main():
    data = {}
    titles = [
        "winrar 5.90 final licence",
        "photobash porous rocks 2017 multi webrip",
        "nitro pro v13.15.1.282 enterprise windows x32 x64 multi-langues"
        "windows 10 ltsc blue v2 edition 1809 fr",
        "musiclab realstrat 5 v5.0.2.7424 win",
        "lumion 10 pro crack", "autodesk sketchbook pro 2021 v8.8.0 x64",
        "winrar 5.90 final portable", "daemon tools ultra 5.7.0.1284",
        "serif affinity 1.8.2.620", "f-secure freedome vpn 2.32.6293",
        "photobash quaint neighborhood 2017 multi webrip",
        "photobash abandoned interiors 2017 multi webrip",
        "windows 10 pro x64 inclus office 2019 fr-fr",
        "photobash misty lagoon 2017 multi webrip",
        "yamicsoft w10 manager 3.2.4 portable",
        "android studio 3.6.1.0 windows 64-bit french", "pdf expert 2.5.3"
        "affinity photo beta 1.8.3.178",
        "microsoft windows 10.0.18363.720 version 1909",
        "windows 10 ltsc whitney edition 1809 fr x64",
        "folder marker pro 4.3.0.1",
        "serato dj pro 2.3.3 build 556 64 bits",
        "autodesk 3ds max 2021 multilingual crack",
        "comsol multiphysics 5.5.0.359", "windows 10 3en1 1909 fr x64",
        "capture one20 v20.0.4 build 13.0.4.10",
        "skylum aurora hdr v1.0.0.2550 standalone et plugins adobe",
        "madia tubemaster v 1.0", "foxit phantompdf business 9.7.1.29511",
        "skylum aurora hdr 2019 v1 0 0 6432", "vmware fusion pro v11.5.3",
        "cype 2017 m crack multilangue win", "apple logic pro x v10.4.8"
        "windows 10 ltsc katana v2 edition 1809 fr",
        "adobe dreamweaver cc 2020 v20.0", "busycal3 v3.9.0"]

    num = 134

    r_data = get(f"https://jaimelogiciel.com/www2.yggtorrent.se.json")
    entries = loads(r_data.text)

    data["titles"] = titles
    data["num"] = num
    data["entries"] = entries

    with open("vars.py", "w", encoding="utf-8") as fo:
        fo.write(dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    main()
