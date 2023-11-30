# -----------------------------------------#
#   Make Glossary 1.01
#   2023-11-26
#   (c)Robert Belton BSD 3-Clause License
#
#   Takes a text, extracts the kanji &
#   analyzes them by kyouiku level
#   Outputs a word list with links to
#   monokakido's Reikoku dictionary app.
#   Outputs a tsv file suitable for use in
#   Flashcard Deluxe
#
# -----------------------------------------#

import sys
import re
import dialogs
import time
import sqlite3
import os
import csv
from pathlib import Path


# decoration snippets
_line_ = "\n----------------\n"
_line2_ = ""


kanji = r'[㐀-䶵一-鿋豈-頻]'


def add_unique_postfix(fn):
    if not os.path.exists(fn):
        return fn

    path, name = os.path.split(fn)
    name, ext = os.path.splitext(name)

    make_fn = lambda i: os.path.join(path, f"{name}_{i}{ext}")

    for i in range(2, sys.maxsize):
        uni_fn = make_fn(i)
        if not os.path.exists(uni_fn):
            return uni_fn

    return None


def main():
    
    # select file to sieve
    filepath = dialogs.pick_document(
        types=["public.utf8-plain-text", "public.text"])
    if filepath is None:
        dialogs.alert("⚠️ Alert",
                      "No file found, script cancelled",
                      "OK",
                      hide_cancel_button=True)
        print("user cancelled")
        sys.exit("user cancelled")
    #_file = open(filepath, "r", encoding="utf-8")
    #text = _file.read()
    #_file.close()
            
    # choose a dictionary
    choice = dialogs.list_dialog(
        title='Choose a dictionary for links',
        items=["reikoku", "weblio", "jisho", "eijiro", "wiktionary"],
        multiple=False)
    if choice is None:
        dialogs.alert(
            "⚠️ Alert",
            "No dictionary selected, script cancelled.",
            "OK", hide_cancel_button=True)
        print("user cancelled")
        sys.exit("user cancelled")
        
    url_scheme_postfix = ""

    if choice == "weblio":
        url_scheme = "https://ejje.weblio.jp/content/"
    elif choice == "eijiro":
        url_scheme = "https://eow.alc.co.jp/search?q="
    elif choice == "jisho":
        url_scheme = "https://jisho.org/search/"
    elif choice == "reikoku":
        url_scheme = "mkreikoku:///search?text="
    elif choice == "wiktionary":
        url_scheme = "https://en.m.wiktionary.org/wiki/"
        url_scheme_postfix = "#Japanese"

    print(choice + " chosen ...")
    
    print("searching corelist...")
    
    # word list 
    wordlist = []
    with open(filepath, encoding = 'utf-8', newline='\n') as text2:
        input = csv.reader(text2)
        for row in input:
            wordlist = wordlist + [row[0]]

    # search corelist
    connection = sqlite3.connect("data/core.db")
    cursor = connection.cursor()
    core_output = ""
    core_omitted_words = []

    for target in wordlist:
        definition = cursor.execute(
            """SELECT main.kanji, main.kana, main.pos, main.eng
               FROM main WHERE main.kanji = ? """,
            (target,), ).fetchone()
        if definition is not None:
            core_output += ("[" + str(definition[0]) + "]"
                            + "(" + url_scheme + str(definition[0])
                            + url_scheme_postfix + ") : "
                            + "【" + str(definition[1]) + "】,"
                            + " (" + str(definition[2]) + "), "
                            + str(definition[3]) + "  \n")
        else:
            core_omitted_words += [target]
        
    connection.commit()
    connection.close()
    
    print("searching sieve list...")
    # search sieve list
    connection = sqlite3.connect("data/sieve.db")
    cursor = connection.cursor()
    sieve_output = ""
    sieve_omitted_words = []
    # search for kanji & kana
    for target in core_omitted_words:
        definition = cursor.execute(
            """SELECT main.kanji, main.kana, main.pos, main.eng, main.jp
               FROM main WHERE main.kanji = ? """,
            (target,),).fetchone()
        if definition is not None:
            sieve_output += ("[" + str(definition[0]) + "]"
                               + "(" + url_scheme + str(definition[0])
                               + url_scheme_postfix + ") :"
                               + "【" + str(definition[1]) + "】,"
                               + " (" + str(definition[2]) + "), "
                               + str(definition[3]) + ", "
                               + str(definition[4]) + "  \n")
        else:
            sieve_omitted_words += [target]
            
    connection.commit()
    connection.close()
    
    print("searching jmdict for kanji...")
    # search jmdict for kanji
    connection = sqlite3.connect("data/jmdict.db")
    cursor = connection.cursor()
    
    jmdict_output = ""
    jm_omitted_words = []
    
    for target in sieve_omitted_words:
        definition = cursor.execute(
            """SELECT words_jp.kanji, words_jp.reading, 
            words_jp.tags, words_en.def FROM words_jp  
            INNER JOIN words_en ON words_jp.ID=words_en.JPID
            WHERE words_jp.kanji = ? """,
            (target,), ).fetchone()
        if definition is not None:
            jmdict_output += ("[" + str(definition[0]) + "]"
                              + "(" + url_scheme + str(definition[0])
                              + url_scheme_postfix + ") : "
                              + "【" + str(definition[1]) + "】,"
                              + " (" + str(definition[2]) + "), "
                              + str(definition[3]) + "  \n")
        else:
            jm_omitted_words += [target]
    
    print("searching jmdict for kana...")
    #search for kana in jmdict
    jm_omitted_words_2 = []
    for target in jm_omitted_words: 
        definition = cursor.execute(
            """SELECT words_jp.kanji, words_jp.reading,
            words_jp.tags, words_en.def FROM words_jp  
            INNER JOIN words_en ON words_jp.ID=words_en.JPID 
            WHERE words_jp.reading = ? """,
            (target,),).fetchone()
        if definition is not None:
            jmdict_output += ("[" + str(definition[0]) + "]"
                              + "(" + url_scheme + str(definition[0])
                              + url_scheme_postfix + ") : "
                              + "【" + str(definition[1]) + "】,"
                              + " (" + str(definition[2]) + "), "
                              + str(definition[3]) + "  \n")
        else:
            jm_omitted_words_2 += [target]
    
    connection.commit()
    connection.close()   

    
    orphan = ""
    for word in jm_omitted_words_2:
        orphan = (orphan + "[" + word + "]"
                  + "(" + url_scheme + word + ") :  \n")
    
    print("formatting ... \n\n")
    
    # prettify text
    # list of tuples [(x,y)] to string x(y)
    def pretty(text):
        text = " ".join(map(str, text))
        text = text.replace("(", "").replace(", ", "(").replace("'", "")
        return text
    
    sieve_omitted_wordsp = str(sieve_omitted_words).replace("[", "").replace(
        "'", "").replace("]", "")
    jm_omitted_words_2p = str(jm_omitted_words_2).replace("[", "").replace(
        "'", "").replace("]", "")
    core_omitted_wordsp = str(core_omitted_words).replace("[", "").replace(
        "'", "").replace("]", "")
    
    # output to console
    print(_line_)
    print("core 6k list:  \n")
    print(core_output)
    print("omitted:", len(core_omitted_words), "\n")
    print(core_omitted_wordsp)
    print(_line_)
    print("sieve list:  \n")
    print(sieve_output)
    print("omitted:", len(sieve_omitted_words), "\n")
    print(sieve_omitted_wordsp)
    print(_line_)
    print("jmdict:  \n")
    print(jmdict_output)
    print("omitted:", len(jm_omitted_words_2), "\n")
    print(jm_omitted_words_2p)
    print(_line_)
    print(orphan)
    print("\n\nSaving to file ... \n\n")
    
    # text for output #
    sieved_text = f'''
__Glossary:__  \n
{_line2_}
__Core 6k list:__  \n\n
{core_output} \n
__omitted words:__ {len(core_omitted_words)}  \n
{core_omitted_wordsp}
{_line_}
__sieve list:__  \n
{sieve_output} \n
__omitted words:__ {len(sieve_omitted_words)}  \n
{sieve_omitted_wordsp}
{_line_}
__jmdict list:__  \n
{jmdict_output} \n
__omitted words:__  {len(jm_omitted_words_2)}  \n
{jm_omitted_words_2p}  \n
{_line_}
{orphan}  \n
'''

    # save output #
    newdir = "glossary output/"
    newfile = Path(newdir)
    if not newfile.is_dir(): os.mkdir(newdir)
    newname = Path(filepath).stem + "_" + choice + "_s.md"
    newpath = "glossary output/" + newname
    newfile = Path(newdir + newname)
    newpath = add_unique_postfix(newfile)
    newtext = (Path(filepath).stem
                + "  \n_" + time.ctime()
                + "_  \n\n" + sieved_text)
    newfile = open(newpath, "w", encoding="utf-8")
    newfile.write(newtext)
    newfile.close()
    
    # append to orphans file
    newfile = open("glossary output/orphans.md", "a", encoding="utf-8")
    newfile.write("\n\n" + newname + "  \n" + time.ctime() + "  \n" + orphan)
    newfile.close()

    print("saved \n")
    
    
if __name__ == '__main__':
    main()
    
    
    
