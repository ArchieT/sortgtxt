import re

quot = re.compile('"([^"]*)"')
msgstrbracke = re.compile('msgstr\[(\d*)]')


def jakbyco(linie):
    for l in linie:
        if len(l) == 0:
            raise PustaLinia
    k = ""
    transcomme = []
    extracomme = []
    refere = []
    flagslines = []
    previouscomme = []
    for l in linie:
        if l.startswith('"'):
            if k == "msgid":
                msgid += quot.search(l)
            elif k == "msgid_plural":
                msgid_plural += quot.search(l)
            elif k == "msgstr":
                msgstr += quot.search(l)
            elif k == "msgstr[":
                a = msgstrlist.pop()
                a += quot.search(l)
                msgstrlist.append(a)
            else:
                raise UntiedQuote

        elif l.startswith("msgid "):
            msgid = quot.search(l)
            k = "msgid"
        elif l.startswith("msgid_plural "):
            msgid_plural = quot.search(l)
            k = "msgid_plural"
        elif l.startswith("msgstr "):
            msgstr = quot.search(l)
            k = "msgstr"
        elif l.startswith("msgstr["):
            if not mamyliste:
                mamyliste = true
                msgstrlist = []
            msgstrlist.append((msgstrbracke.search(l), quot.search(l)))
            k = "msgstr["
        elif l.startswith("# "):
            transcomme.append(l)
        elif l.startswith("#."):
            extracomme.append(l)
        elif l.startswith("#:"):
            refere.append(l)
        elif l.startswith("#,"):
            flagslines.append(l)
        elif l.startswith("#|"):
            previouscomme.append(l)


class PustaLinia(Exception):
    pass


class UntiedQuote(Exception):
    pass


class baza(Object):

    def __init__(opened):
        self.wpisy = []


class wpis(Object):

    def __init__(listoflines):
        self.listoflines = listoflines
        for l in linie:
            if len(l) == 0:
                raise PustaLinia


class metadane(wpis):
    pass