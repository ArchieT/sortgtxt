# -*- coding: utf-8 -*-

import re

from babel.messages.pofile import denormalize
# that's a fairly large dependency, from which I am using just a few lines
# of code (denormalize() function, and its dependency, unescape())

quot = re.compile(r'"(?:\\.|[^"\\])*"')

msgstrbracke = re.compile('msgstr\[(\d*)]')


def parse_entry(linie):
    for l in linie:
        if not l.strip():
            raise PustaLinia
    k = ""
    komenty = []
    mamyliste = False
    msgid = False
    for l in linie:
        if l.startswith('"'):
            if k == "msgid":
                msgid += denormalize(quot.findall(l)[0])
            elif k == "msgid_plural":
                msgid_plural += denormalize(quot.findall(l)[0])
            elif k == "msgstr":
                msgstr += denormalize(quot.findall(l)[0])
            elif k == "msgstr[":
                a = msgstrlist.pop()
                a += denormalize(quot.findall(l)[0])
                msgstrlist.append(a)
            else:
                raise UntiedQuote(l)

        elif l.startswith("msgid "):
            msgid = denormalize(quot.findall(l)[0])
            k = "msgid"
        elif l.startswith("msgid_plural "):
            msgid_plural = denormalize(quot.findall(l)[0])
            k = "msgid_plural"
        elif l.startswith("msgstr "):
            msgstr = denormalize(quot.findall(l)[0])
            k = "msgstr"
        elif l.startswith("msgstr["):
            if not mamyliste:
                mamyliste = True
                msgstrlist = []
            msgstrlist.append((
                msgstrbracke.findall(l)[0], 
                denormalize(quot.findall(l)[0])
            ))
            k = "msgstr["
        elif l.startswith("# "):
            komenty.append(TransComment(l))
        elif l.startswith("#."):
            komenty.append(ExtraComment(l))
        elif l.startswith("#:"):
            komenty.append(ReferenceComment(l))
        elif l.startswith("#,"):
            komenty.append(FlagsLine(l))
        elif l.startswith("#|"):
            komenty.append(PreviousComment(l))
        elif l.startswith("#~"):
            komenty.append(TildedComment(l))
        elif l.strip() == "#":
            komenty.append(SamHash(l))
        else:
            raise UnknownToken(l)
    if mamyliste:
        return Pluralny(linie, msgid, msgid_plural, msgstrlist, komenty)
    elif msgid == False:
        return Linijki(linie, komenty)
    elif len(msgid) == 0:
        return Metadane(linie, msgstr, komenty)
    else:
        return Wpis(linie, msgid, msgstr, komenty)


class PustaLinia(Exception):
    pass


class UnknownToken(Exception):
    pass


class UntiedQuote(UnknownToken):
    pass


def callbackentries(opened, callback):
    bufor = []
    for l in opened:
        if not l.strip():
            if len(bufor) > 0:
                callback(tuple(bufor))
                bufor = []
        else:
            bufor.append(l)
    if len(bufor) > 0:
        callback(tuple(bufor))


class Baza(object):

    def __init__(self, opened):
        self.wpisy = []
        callbackentries(opened, lambda x: self.wpisy.append(parse_entry(x)))
        popthem = []
        for i in range(len(self.wpisy)):
            if isinstance(self.wpisy[i], Metadane):
                popthem.append(i)
        for i in popthem:
            self.metadane = self.wpisy.pop(i)

    def rawzapisdopliku(self, opened):
        self.metadane.rawwrite(opened)
        for wpis in self.wpisy:
            wpis.rawwrite(opened)

    def sortbymsgid(self):
        self.wpisy = sorted(self.wpisy, key=lambda x: x.sortingname())


class Linijki(object):

    def __init__(self, listoflines, komenty):
        self.listoflines = listoflines
        self.komenty = komenty
        self.getourid()

    def getourid(self):
        cmsgid = None
        if not isinstance(self, Wpis):
            for i in self.komenty:
                if isinstance(i, TildedComment):
                    if cmsgid is None:
                        a = i.has_msgid()
                        if a is not None:
                            cmsgid = [a, ]
                    else:
                        a = i.has_quot()
                        if a is not None:
                            cmsgid.append(a)
        self.cmsgid = ''.join(cmsgid)

    def __str__(self):
        return str(self.listoflines) + "\nkomenty:" + str(self.komenty)

    def __repr__(self):
        return str(self)

    def rawwrite(self, opened):
        for line in self.listoflines:
            opened.write(line)
        opened.write("\n")

    def sortingname(self):
        if self.cmsgid is not None:
            return self.cmsgid
        print(self.komenty[0].line)
        return self.komenty[0].line


class Wpis(Linijki):

    def __init__(self, listoflines, msgid, msgstr, komenty):
        self.msgid = msgid
        self.msgstr = msgstr
        for l in listoflines:
            if not l.strip():
                raise PustaLinia
        Linijki.__init__(self, listoflines, komenty)

    def sortingname(self):
        print(self.msgid)
        return self.msgid

    def getourid(self):
        pass


class Pluralny(Wpis):

    def __init__(self, listoflines, msgid, msgid_plural, msgstrlist, komenty):
        self.msgid_plural = msgid_plural
        Wpis.__init__(self, listoflines, msgid, msgstrlist, komenty)


class Metadane(Wpis):

    def __init__(self, listoflines, msgstr, komenty):
        Wpis.__init__(self, listoflines, "", msgstr, komenty)


class Comment(object):

    def __init__(self, line):
        self.line = line

    def __str__(self):
        return self.line

    def __repr__(self):
        return self.line


class SamHash(Comment):
    pass


class TransComment(Comment):
    pass


class ExtraComment(Comment):
    pass


class ReferenceComment(Comment):
    pass


class FlagsLine(Comment):
    pass


class PreviousComment(Comment):
    pass


class TildedComment(Comment):

    def has_msgid(self):
        if self.line.startswith("#~ msgid "):
            return denormalize(quot.findall(self.line)[0])
        else:
            return None

    def has_quot(self):
        if self.line.startswith('#~ "'):
            return denormalize(quot.findall(self.line)[0])
        else:
            return None
