import gettext
import locale


LOCALES = {
    ("ru_RU", "UTF-8"): gettext.translation("wc", "po", ["ru_RU.UTF-8"]),
    ("en_US", "UTF-8"): gettext.NullTranslations()
}


def ngettext(msgid, msgid2, n):
    return LOCALES[locale.getlocale()].ngettext(msgid, msgid2, n)


while s := input():
    n = len(s.split())
    for loc in LOCALES:
        locale.setlocale(locale.LC_ALL, loc)
        print(ngettext("Entered {} word", "Entered {} words", n).format(n))
