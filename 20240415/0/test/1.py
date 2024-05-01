from babel.support import Translations


translations = Translations.load("translations", "ru")

print(translations.gettext("Hello"))
print(translations.ngettext("{} file", "{} files", 3).format(3))
