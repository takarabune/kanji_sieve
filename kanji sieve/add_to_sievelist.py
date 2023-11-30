# -----------------------------------------#
#   Add to Sieve  1.01
#   2023-11-26
#   (c)Robert Belton BSD 3-Clause License
#
#   Adds entries to sieve.db
#
# -----------------------------------------#
import sqlite3
import dialogs
import sys

con = sqlite3.connect("data/sieve.db")
cur = con.cursor()

data =[]

while exit != 2:
    words = dialogs.form_dialog(
        title='Enter a word',
        fields=[
            {"type":"text","key":"kanji","value":"","title":"kanji: "},
            {"type":"text","key":"kana","value":"","title":"kana: "},
            {"type":"text","key":"eng","value":"","title":"eng: "},
            {"type":"text","key":"pos","value":"","title":"pos: "},
            {"type":"text","key":"jp","value":"","title":"jpn: "}
            ])
    if words == None:
        print("user cancelled")
        sys.exit("user cancelled")
    print(tuple(words.values()))
    entry = [tuple(words.values())]
    data += entry
    exit = dialogs.alert(
        "⚠️ Alert",
        "Do you have more words to enter?",
        "Yes", "No",
         hide_cancel_button=True)
    
alert = dialogs.alert(
    "⚠️ Alert",
    "Commit these entries?",
    "Yes", "No",
     hide_cancel_button=True)
if alert == 1:
    cur.executemany("INSERT INTO main VALUES(?, ?, ?, ?, ?)", data)
    con.commit()
    con.close()
else:
    print("changes abandoned")
    
print("\n\n sieve dictionary entries: \n")
for row in cur.execute(
    "SELECT kanji, kana, eng, pos, jp FROM main ORDER by kana"):
    print(row)
    

