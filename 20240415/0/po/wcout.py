import locale
import gettext

transltion = gettext.translation("wcout", "po", fallback = True)
_, gettext  = transltion.gettext, transltion.ngettext

while s := input():
    print(_("Entered {} word(s)").format(len(s.split())))


'''
transltion = gettext.translation("wcout", "po", fallback = True)
_, gettext  = transltion.gettext, transltion.ngettext

while True:
    
  
    input_string = input("Enter a string (type 'exit' to quit): ")
    if input_string.lower() == 'exit':
        break

    word_count = len(input_string.split())
    print(f"Entered {word_count} word(s)")
'''