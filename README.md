## Kanji Sieve v1.18

A wip script for Pythonista 3 that takes a Japanese text and outputs a markdown file giving a basic analysis of its kanji and a glossary of kanji based vocabulary with links to a dictionary resource. 


I hack this together for myself while learning python. As such it may not be robust, in terms of error capture etc., in the face of other people using it. 


The text to be sieved needs to be without furigana in plaintext utf-8 format. 
This could be generated by ocr from printed sources. I also have a utility script to help remove furigana from ocr output.

Run the script `kanji_sieve.py`. Select your preferences. Tap 'Sieve File' to select a file to sieve. 
You have a choice of dictionary to use for the links. 
- [Weblio](https://ejje.weblio.jp/content/笊), an online multi dictionary resource. 
- [Reikoku](https://apps.apple.com/app/%E4%BE%8B%E8%A7%A3%E5%AD%A6%E7%BF%92%E5%9B%BD%E8%AA%9E%E8%BE%9E%E5%85%B8-%E7%AC%AC%E4%B9%9D%E7%89%88-%E6%BC%A2%E6%A4%9C%E9%81%8E%E5%8E%BB%E5%95%8F%E3%83%89%E3%83%AA%E3%83%AB/id615900736), a children's dictionary app from Monokakido.
- [Jisho.org](https://jisho.org/search/笊), which will give similar results to the generated list, and
- [Eijiro](https://eow.alc.co.jp/search?q=ざる), an English to Japanese resource some of which is behind a paid subscription and annoying ads.
- [Wiktionary](https://en.wiktionary.org/wiki/笊#Japanese), wikipedia's dictionary project. both English and Japanese versions. 


The text is broken down by [TinySegmenter](https://github.com/SamuraiT/tinysegmenter). The lexical units can tend to be word fragments, like verb stems, which can affect the searches.  Because of this there is a chance to edit the terms searched for, and there is a user compiled substitutions file ``data/sub.csv`` which has pairs of words to substitute. 

Depending on preferences, as the dictionaries searched can be toggled on and off, first a 'Core 6k' vocabulary list is searched. Anything not found is searched for in a custom user list, and anything not found there is searched for in JMdict. Only the first result is returned in JMdict, and this might not be the most common. Any words left over are then listed.  
These 'orphans' and any strange returns from JMdict can then be researched and manually entered into the user table in ``dict.db`` using the``add to dictionary`` button for future searches, or for a second pass. Alternatively, also from the main view, they can be added to ``data/omit.ksv`` This file is a list of words (one word per line) to omit from searches; ideally because they are already very familiar. Or they can be added to ``data/sub.ksv`` with a substitution to improve the search. eg. the verb stem 乗っ	would be substituted by 乗る the dict form. Making these corrections and substitutions improves the search results in subsequent sieves. 

The output will appear in a scrollable textbox. A markdown file will also be generated, along with a tsv file of found words from the glossary, and a file listing the words not found. The complete session will also be in the console.
The whole process takes just a few seconds for a page of text. (800 to 1000 characters and approx 120 words to search)

The output is saved to the same directory as the script. The script needs to be in the same directory as a folder named data containing the the sqlite dictionary file, omit file, and substitutions file. Previous output won't be overwritten. The ``orphans.md`` file acts as a log and is written to each time the script is run. If deleted a new file will start on the next run. 

**NOTE**: The script depends on [tinysegmenter](https://github.com/SamuraiT/tinysegmenter) which needs to be installed to 'site packages (user)' in Pythonista. or the same directory as `kanji_sieve.py`


Although written for Pythonista, I see no reason why the iOS-only calls to dialogs and gui couldn't be rewritten for another platform.

### add to dictionary
A utility script to add entries to the user table of the sqlite file ``dict.db``. It has a gui interface allowing 6 entries at a time to be made. 'Term', 'Reading', and 'Translation' are required fields. If any are empty that row will not be entered. 
- 'Term' should be kanji, katakana, or hiragana. It is the item matched on a search.
- 'Reading' should be hiragana only.
- 'Translation' can be the language of your choice, often English.
- 'pos' is part of speech. eg: n, adv, i-adj, phrase, v5, v1, etc. be consistant. 
- 'Japanese' is a simple definition in Japanese using terms you know.
  
Remember: Garbage In, Garbage Out. Other than blank fields, nothing is checked for or enforced. 

#### remove_furigana
A utility script to remove furigana from ocr output. It works on text where the line structure is kept and the furigana appear between lines of text. The ouput will still need to be proofread and very short line lengths like 16 character newsprint columns may cause some errors. It tries to preserve paragraph returns while stripping line returns. 

#### generate_glossary
Similar to Kanji Sieve but only outputs a glossary from an already ordered list. Input needs to be a list of words, kana or kanji, on seperate lines rather than a text file. If given a csv file it will read the first column and ignore any others. It uses the same data resources as Kanji Sieve, it doesn't require tinysegmenter. It hasn't a preferences gui.

__notes:__  
⚠️**DO NOT COPY PASTE JAPANESE IN PYTHONISTA'S EDITOR**  
especially if you intend to key / search for that text. There is [a bug that substitutes characters on paste](https://github.com/omz/Pythonista-Issues/issues/722). (or an intended behaviour that messes up Japanese (and Korean I think))
