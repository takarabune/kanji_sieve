### ---------------------------------------------------###
#   Remove Furigana 1.03
#   2023-11-22
#   Robert Belton
#
#   Takes text with furigana from the output of ocr 
#   and strips out the furigana.
#   It accepts input from the clipboard or a file.
#   It strips linebreaks but tries to preserve 
#   paragraph breaks.
#   It processes line by line. Furigana line defined
#   as a line without Kanji or punctuation or longer
#   than the average line width.   
#
### ---------------------------------------------------###

import sys
import os
import re
import dialogs
import clipboard
import statistics
from pathlib import Path
from datetime import datetime

##### jp_regex #####

kanji = r'[㐀-䶵一-鿋豈-頻]'
symbols_punct = r'[、-〿]'

def extract_unicode_block(unicode_block, string):
    return re.findall(unicode_block, string)

#### end jp_regex ####

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
    
    
### end functions ###

temp_text = clipboard.get()
temp_text = temp_text.replace(" ", "")
if temp_text != "":
    try:
         temp = dialogs.alert("", "Use clipboard?", 
                        "Yes", "No", hide_cancel_button=True)
    except KeyboardInterrupt :
         print("user cancelled")
         sys.exit("user cancelled")
else: temp = 0
     
if temp == 1:
    temp_text = clipboard.get()
    temp_path = "_temp.txt"
    tempfile = open(temp_path, "w", encoding="utf-8")
    tempfile.write(temp_text)
    tempfile.close()
    
if temp != 1:
## select file to read
    filepath = dialogs.pick_document(types = ["public.utf8-plain-text",
                                              "public.text"])
    if filepath == None:
        print("user cancelled")
        sys.exit("user cancelled")
else:
    filepath = temp_path
      
new_text = ""
line_length = []
# analyse line lengths
with open(filepath, "r", encoding="utf-8") as fp:
    for line in fp:
        line = line.replace(" ", "")
        line_length.append(len(line.strip()))
         
line_length.sort()
x = int(4 * len(line_length)/5)
try: top20_lines = line_length[x:]
except: 
    print("file empty")
    sys.exit()
y = statistics.mode(top20_lines)
z = 4 # magic number, used to determine lines likely to be paragraph returns. 

with open(filepath, "r", encoding="utf-8") as fp:
    for line in fp:
        # line = line.replace(" ", "")
        # discard furigana
        if (extract_unicode_block(kanji, line) != [] or 
            extract_unicode_block(symbols_punct, line) != [] or 
            len(line.replace(" ", "").strip()) >= y - 2):
             # if line has kanji or punctuation it is not furigana
             if  (y - z) >= len(line.strip()) :
                 new_text = new_text + line  #retain \n as paragraph break 
             else:
                 new_text = new_text + line.strip()

print("\n\n\n")
print(new_text)
print("\n\n\n")

try:
    name = dialogs.input_alert("💾 Save...", "Save file as:", 
                           "untitled_noruby", "Save", hide_cancel_button=False)
except KeyboardInterrupt :
     print("user cancelled")
     sys.exit("user cancelled")

newname = name + ".txt"
newdir = "removefurigana output/"
newfile = Path(newdir)
if not newfile.is_dir(): os.mkdir(newdir)
newfile = Path(newdir + newname)
newpath = add_unique_postfix(newfile)
newfile = open(newpath, "w", encoding="utf-8")
newfile.write(new_text)
newfile.close()


if temp == 1:
    if os.path.isfile(temp_path):
        os.remove(temp_path)
temp = 0
try: temp = dialogs.alert("", "📋 Save output text to clipboard ?", 
                         "Yes", "No", hide_cancel_button=True)
except KeyboardInterrupt :
     print("user cancelled")
     sys.exit("user cancelled")
     
if temp == 1:
    clipboard.set(new_text)


    
      
        
          
            
              
                
                  
                    
                      
                        
                          
                            
                              
                                
                                  
                                    
                                      
                                        
                                          
                                            
                                                
