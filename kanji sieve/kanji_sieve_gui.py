# -----------------------------------------#
#   Kanji Sieve GUI 1.14 for Pythonista 3
#   2023-12-09
#   (c)Robert Belton BSD 3-Clause License
#
#   Interface for 'kanji_sieve.py'
#   Allows setting preferences
#
#   requires:
#      kanji_sieve_gui.pyui
#      
#   dependencies:
#      kanji_sieve.py
#
# -----------------------------------------#

import ui
import csv
import os
import kanji_sieve


def init_dict_pref(pref):
    if pref == "reikoku":
        v['reikoku'].title = "✔︎"
        v['weblio'].title = ""
        v['wik-eng'].title = ""
        v['wik-jpn'].title = ""
        v['jisho'].title = ""
        v['eijiro'].title = ""
    elif pref == "weblio":
        v['reikoku'].title = ""
        v['weblio'].title = "✔︎"
        v['wik-eng'].title = ""
        v['wik-jpn'].title = ""
        v['jisho'].title = ""
        v['eijiro'].title = ""
    elif pref == "wik-eng":
        v['reikoku'].title = ""
        v['weblio'].title = ""
        v['wik-eng'].title = "✔︎"
        v['wik-jpn'].title = ""
        v['jisho'].title = ""
        v['eijiro'].title = ""
    elif pref == "wik-jpn":
        v['reikoku'].title = ""
        v['weblio'].title = ""
        v['wik-eng'].title = ""
        v['wik-jpn'].title = "✔︎"
        v['jisho'].title = ""
        v['eijiro'].title = ""
    elif pref == "jisho":
        v['reikoku'].title = ""
        v['weblio'].title = ""
        v['wik-eng'].title = ""
        v['wik-jpn'].title = ""
        v['jisho'].title = "✔︎"
        v['eijiro'].title = ""
    elif pref == "eijiro":
        v['reikoku'].title = ""
        v['weblio'].title = ""
        v['wik-eng'].title = ""
        v['wik-jpn'].title = ""
        v['jisho'].title = ""
        v['eijiro'].title = "✔︎"


def init_bool_pref(pref, value):
        if value == "1":
            v[pref].title = "✔︎"
        elif value == "0":
            v[pref].title = ""
        else:
            pass
        

def select_dict(self):
    if self.title == "":
        self.title = "✔︎"
        dict_pref = self.name
        if self.name == "reikoku":
            v['weblio'].title = ""
            v['wik-eng'].title = ""
            v['wik-jpn'].title = ""
            v['jisho'].title = ""
            v['eijiro'].title = ""
        elif self.name == "weblio":
            v['reikoku'].title = ""
            v['wik-eng'].title = ""
            v['wik-jpn'].title = ""
            v['jisho'].title = ""
            v['eijiro'].title = ""
        elif self.name == "wik-eng":
            v['weblio'].title = ""
            v['reikoku'].title = ""
            v['wik-jpn'].title = ""
            v['jisho'].title = ""
            v['eijiro'].title = ""
        elif self.name == "wik-jpn":
            v['weblio'].title = ""
            v['reikoku'].title = ""
            v['wik-eng'].title = ""
            v['jisho'].title = ""
            v['eijiro'].title = ""
        elif self.name == "jisho":
            v['weblio'].title = ""
            v['reikoku'].title = ""
            v['wik-eng'].title = ""
            v['wik-jpn'].title = ""
            v['eijiro'].title = ""
        elif self.name == "eijiro":
            v['weblio'].title = ""
            v['reikoku'].title = ""
            v['wik-eng'].title = ""
            v['wik-jpn'].title = ""
            v['jisho'].title = ""
    PREFS.update({"dict": dict_pref})


def load_prefs(path):
    if os.path.isfile(path) is False:
        defaultprefs = {'dict': 'weblio', 'tsv_out': '1', 'orphan_out': '1', 'jyouyou': '1', 'core': '1', 'user': '1', 'orphan': '1', 'jmdict': '1'}
        write_prefs(defaultprefs, path)
    with open(path, encoding='utf-8', newline='\n') as csvtext:
        input = csv.reader(csvtext)
        prefs = {str(row[0]):str(row[1]) for row in input}
    return prefs

def write_prefs(prefs, path): 
    with open(path,'w') as f:
        w = csv.writer(f)
        w.writerows(prefs.items())
        
def set_pref(self):
    if self.title == "":
        self.title = "✔︎"
        PREFS.update({self.name: "1"})
    else:
        self.title = ""
        PREFS.update({self.name: "0"})
        
def exit_action(sender):
    v.close()

def sieve_action(sender):
    kanji_sieve.main(PREFS)

v = ui.load_view()

exit_button = ui.ButtonItem()
exit_button.title = 'Exit'
exit_button.tint_color = 'black'
exit_button.action = exit_action
sieve_button = ui.ButtonItem()
sieve_button.title = 'Sieve File'
sieve_button.tint_color = 'blue'
sieve_button.action = sieve_action
v.left_button_items = [exit_button]
v.right_button_items = [sieve_button]

v.present('sheet', hide_close_button=True)

# initialise prefs
PREFS = load_prefs("data/kanji_sieve.pref")
dict_pref = PREFS["dict"]
init_dict_pref(dict_pref)
for pref, value in PREFS.items():
    init_bool_pref(pref, value)

v.wait_modal()

# on close write prefs
write_prefs(PREFS, "data/kanji_sieve.pref")

