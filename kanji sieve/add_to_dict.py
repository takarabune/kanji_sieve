# -----------------------------------------#
#   Add to Dict  2.1 gui 
#   2023-12-12
#   (c)Robert Belton BSD 3-Clause License
#
#   Adds entries to user table dict.db
#
#   requires:
#        add_to_dict.pyui
#        data/dict.db
#        data/orphans.ksv
#   
#   will build (if not present):
#        data/kanji_sieve.pref
#
# -----------------------------------------#

import ui
import dialogs
import sqlite3
import sys
import csv
import os

def load_prefs(path):
    if os.path.isfile(path) is False:
        defaultprefs = {'dict': 'weblio', 'tsv_out': '1', 'orphan_out': '1', 'kyouiku': '1', 'core': '1', 'user': '1', 'orphan': '1', 'jmdict': '1', 'add_orphans': '1'} 
        write_prefs(defaultprefs, path)
    with open(path, encoding='utf-8', newline='\n') as csvtext:
        input = csv.reader(csvtext)
        prefs = {str(row[0]):str(row[1]) for row in input}
    return prefs

def main():
    
    PREFS = load_prefs("data/kanji_sieve.pref")
    
    orphans_list =[]
    
    def populate_grid():
        if PREFS["add_orphans"] == "1":
            if len(orphans_list) > 0 and len(orphans_list) < 7:
                i = len(orphans_list) 
                while i == (len(orphans_list)) and i > 0:
                    v[("kanji" + str(i))].text = (orphans_list[len(orphans_list)-1])
                    orphans_list.pop(len(orphans_list)-1)
                    i -= 1
            elif len(orphans_list) > 6:
                i = 0
                while i < 6:
                    v[("kanji" + str(i+1))].text = (orphans_list[len(orphans_list)-1])
                    orphans_list.pop(len(orphans_list)-1)
                    i += 1

    
    def insert_data(data):
        con = sqlite3.connect("data/dict.db")
        cur = con.cursor()
        cur.executemany("INSERT INTO user VALUES(?, ?, ?, ?, ?)", data)
        con.commit()
        con.close()
     
            
    def save_action(sender):
        data = []
        row1 = (v['kanji1'].text, v['kana1'].text, v['eng1'].text, v['pos1'].text, v['jpn1'].text)
        row2 = (v['kanji2'].text, v['kana2'].text, v['eng2'].text, v['pos2'].text, v['jpn2'].text)
        row3 = (v['kanji3'].text, v['kana3'].text, v['eng3'].text, v['pos3'].text, v['jpn3'].text)
        row4 = (v['kanji4'].text, v['kana4'].text, v['eng4'].text, v['pos4'].text, v['jpn4'].text)
        row5 = (v['kanji5'].text, v['kana5'].text, v['eng5'].text, v['pos5'].text, v['jpn5'].text)
        row6 = (v['kanji6'].text, v['kana6'].text, v['eng6'].text, v['pos6'].text, v['jpn6'].text)
        if v['kanji1'].text != "" and v['kana1'].text != "" and v['eng1'].text != "":
            data += [row1]
        if v['kanji2'].text != "" and v['kana2'].text != "" and v['eng2'].text != "":
            data += [row2]
        if v['kanji3'].text != "" and v['kana3'].text != "" and v['eng3'].text != "":
            data += [row3]
        if v['kanji4'].text != "" and v['kana4'].text != "" and v['eng4'].text != "":
            data += [row4]
        if v['kanji5'].text != "" and v['kana5'].text != "" and v['eng5'].text != "":
            data += [row5]
        if v['kanji6'].text != "" and v['kana6'].text != "" and v['eng6'].text != "":
            data += [row6]
        print(data)
        insert_data(data)
        clear_action(sender)
        dialogs.hud_alert("saved to dictionary")
        populate_grid()
        v['kanji1'].begin_editing()
    
       
    def clear_action(sender):
        v['kanji1'].text, v['kana1'].text, v['eng1'].text, v['pos1'].text, v['jpn1'].text = "","","","",""
        v['kanji2'].text, v['kana2'].text, v['eng2'].text, v['pos2'].text, v['jpn2'].text = "","","","",""
        v['kanji3'].text, v['kana3'].text, v['eng3'].text, v['pos3'].text, v['jpn3'].text = "","","","",""
        v['kanji4'].text, v['kana4'].text, v['eng4'].text, v['pos4'].text, v['jpn4'].text = "","","","",""
        v['kanji5'].text, v['kana5'].text, v['eng5'].text, v['pos5'].text, v['jpn5'].text = "","","","",""
        v['kanji6'].text, v['kana6'].text, v['eng6'].text, v['pos6'].text, v['jpn6'].text = "","","","",""
        v['kanji1'].begin_editing()
        
        
    def exit_action(sender):
        v.close()
    
    #-------------------------------------------------- build gui
    v = ui.load_view()
    
    save_button = ui.ButtonItem()
    save_button.title = 'Save'
    save_button.action = save_action
    
    clear_button = ui.ButtonItem()
    clear_button.title = 'Clear'
    clear_button.tint_color = 'red'
    clear_button.action = clear_action
    
    exit_button = ui.ButtonItem()
    exit_button.title = 'Exit'
    exit_button.tint_color = 'black'
    exit_button.action = exit_action
    
    v.right_button_items = [save_button, clear_button]
    v.left_button_items = [exit_button]
    
    v.present('fullscreen', hide_close_button=True)
    
    # -------------------------------------------------------- initialise grid
    with open("data/orphans.ksv", encoding='utf-8', newline='\n') as csvtext:
        input = csv.reader(csvtext)
        orphans_list = [row[0] for row in input]
    
    populate_grid()

    v['kanji1'].begin_editing()
    print(" terms added:")
    v.wait_modal()
    
    # ---------------------------------------   on exit show user list contents
    con = sqlite3.connect("data/dict.db")
    cur = con.cursor()
    print("\n\n user dictionary entries: \n")
    for row in cur.execute(
        "SELECT rowid, kanji, kana, eng, pos, jp FROM user ORDER by rowid"):
        print(row)
    con.commit()
    con.close()
    

if __name__ == '__main__':
    main()
    
    
