# -----------------------------------------#
#   Add to Dict  2.1.1 gui 
#   2023-12-14
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
        
    def populate_grid():
        if PREFS["add_orphans"] == "1":
            
            if len(orphans_list) in range (len(orphans_list), 7):
                for i in range (1, len(orphans_list)+1 ):
                    v[("kanji" + str(i))].text = (orphans_list[len(orphans_list)-1])
                    orphans_list.pop(len(orphans_list)-1)
                    
            elif len(orphans_list) > 6:
                for i in range(1,7):
                    v[("kanji" + str(i))].text = (orphans_list[len(orphans_list)-1])
                    orphans_list.pop(len(orphans_list)-1)
                    
    
    def insert_data(data):
        con = sqlite3.connect("data/dict.db")
        cur = con.cursor()
        cur.executemany("INSERT INTO user VALUES(?, ?, ?, ?, ?)", data)
        con.commit()
        con.close()
     
     
    def save_action(sender):
        data = []
        row = []
        
        for i in range(1, 7):
            row = (v['kanji'+ str(i)].text, v['kana'+ str(i)].text, v['eng'+ str(i)].text, v['pos'+ str(i)].text, v['jpn'+str(i)].text)
            if v['kanji'+str(i)].text != "" and v['kana'+str(i)].text != "" and v['eng'+str(i)].text != "":
                data.append(row)
        
        if data != []:
            print("terms added:\n", data)
            insert_data(data)
        clear_action(sender)
        dialogs.hud_alert(str(len(data))+" entries saved")
        populate_grid() 
        v['kanji1'].begin_editing()

   
    def clear_action(sender):
        for i in range(1,7):
            v['kanji'+str(i)].text = ""
            v['kana'+str(i)].text = ""
            v['eng'+str(i)].text = ""
            v['pos'+str(i)].text = ""
            v['jpn'+str(i)].text = ""
    
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
    orphans_list =[]
    
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
    
    
