# -----------------------------------------#
#   Kanji Sieve 1.12.1 for Pythonista 3
#   2023-12-02
#   (c)Robert Belton BSD 3-Clause License
#
#   Takes a text, extracts the kanji &
#   analyzes them by kyouiku level
#   Outputs a word list with links to
#   monokakido's Reikoku dictionary app.
#   Outputs a tsv file suitable for use in
#   Flashcard Deluxe
#
#   requires:
#      data/core.db
#      data/sieve.db
#      data/jmdict.db
#      data/omit.csv
#      data/sub.csv
#
#   dependencies:
#      tinysegmenter
#
# -----------------------------------------#

import sys
import tinysegmenter
import re
import dialogs  # pythonista only
import time
import sqlite3
import os
import csv
import zipfile
from pathlib import Path

# constants
VERSION = "1.12.1"

# decoration snippets
_line_ = "\n----------------\n"
_line2_ = ""

kanji = r'[㐀-䶵一-鿋豈-頻]'
ascii_char = r'[ -~]'


def user_editlist(ulist, alert_text):
    # manually edit word_list to improve search
    # ****Fragile due to user****
    ulist2 = ulist
    ulist = "\n".join(map(str, ulist))

    ulist = (dialogs.text_dialog(
        title=alert_text, text=str(ulist),
        font=("Inconsolata", 16),
        done_button_title='Commit'))

    if ulist is None:
        print("user cancelled edit; continuing...")
        return ulist2

    if ulist == '':
        print("list cannot be empty; continuing")
        ulist3 = user_editlist(ulist2, "⚠️ list cannot be empty!")
        return ulist3

    ulist = (re.sub(r"\n\n+", "\n", ulist)).strip()
    ulist = ulist.split("\n")

    return ulist


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


# kyouiku lists #
k1 = """一 右 雨 円 王 音 下 火 花 貝 学 気 九 休 玉 金 空 月 犬 見 五 口 校 左 三 山 子 四 糸 字 耳 七 車 手 十 出
 女 小 上 森 人 水 正 生 青 夕 石 赤 千 川 先 早 草 足 村 大 男 竹 中 虫 町 天 田 土 二 日 入 年 白 八 百 文 木 本 名
 目 立 力 林 六"""
k2 = """引 羽 雲 園 遠 何 科 夏 家 歌 画 回 会 海 絵 外 角 楽 活 間 丸 岩 顔 汽 記 帰 弓 牛 魚 京 強 教 近 兄 形 計
 元 言 原 戸 古 午 後 語 工 公 広 交 光 考 行 高 黄 合 谷 国 黒 今 才 細 作 算 止 市 矢 姉 思 紙 寺 自 時 室 社 弱 首
 秋 週 春 書 少 場 色 食 心 新 親 図 数 西 声 星 晴 切 雪 船 線 前 組 走 多 太 体 台 地 池 知 茶 昼 長 鳥 朝 直 通 弟
 店 点 電 刀 冬 当 東 答 頭 同 道 読 内 南 肉 馬 売 買 麦 半 番 父 風 分 聞 米 歩 母 方 北 毎 妹 万 明 鳴 毛 門 夜 野
 友 用 曜 来 里 理 話"""
k3 = """悪 安 暗 医 委 意 育 員 院 飲 運 泳 駅 央 横 屋 温 化 荷 界 開 階 寒 感 漢 館 岸 起 期 客 究 急 級 宮 球 去
 橋 業 曲 局 銀 区 苦 具 君 係 軽 血 決 研 県 庫 湖 向 幸 港 号 根 祭 皿 仕 死 使 始 指 歯 詩 次 事 持 式 実 写 者 主
 守 取 酒 受 州 拾 終 習 集 住 重 宿 所 暑 助 昭 消 商 章 勝 乗 植 申 身 神 真 深 進 世 整 昔 全 相 送 想 息 速 族 他
 打 対 待 代 第 題 炭 短 談 着 注 柱 丁 帳 調 追 定 庭 笛 鉄 転 都 度 投 豆 島 湯 登 等 動 童 農 波 配 倍 箱 畑 発 反
 坂 板 皮 悲 美 鼻 筆 氷 表 秒 病 品 負 部 服 福 物 平 返 勉 放 味 命 面 問 役 薬 由 油 有 遊 予 羊 洋 葉 陽 様 落 流
 旅 両 緑 礼 列 練 路 和"""
k4 = """愛 案 以 衣 位 囲 胃 印 英 栄 塩 億 加 果 貨 課 芽 改 械 害 街 各 覚 完 官 管 関 観 願 希 季 紀 喜 旗 器 機
 議 求 泣 救 給 挙 漁 共 協 鏡 競 極 訓 軍 郡 径 型 景 芸 欠 結 建 健 験 固 功 好 候 航 康 告 差 菜 最 材 昨 札 刷 殺
 察 参 産 散 残 士 氏 史 司 試 児 治 辞 失 借 種 周 祝 順 初 松 笑 唱 焼 象 照 賞 臣 信 成 省 清 静 席 積 折 節 説 浅
 戦 選 然 争 倉 巣 束 側 続 卒 孫 帯 隊 達 単 置 仲 貯 兆 腸 低 底 停 的 典 伝 徒 努 灯 堂 働 特 得 毒 熱 念 敗 梅 博
 飯 飛 費 必 票 標 不 夫 付 府 副 粉 兵 別 辺 変 便 包 法 望 牧 末 満 未 脈 民 無 約 勇 要 養 浴 利 陸 良 料 量 輪 類
 令 冷 例 歴 連 老 労 録"""
k5 = """圧 移 因 永 営 衛 易 益 液 演 応 往 桜 恩 可 仮 価 河 過 賀 快 解 格 確 額 刊 幹 慣 眼 基 寄 規 技 義 逆 久
 旧 居 許 境 均 禁 句 群 経 潔 件 券 険 検 限 現 減 故 個 護 効 厚 耕 鉱 構 興 講 混 査 再 災 妻 採 際 在 財 罪 雑 酸
 賛 支 志 枝 師 資 飼 示 似 識 質 舎 謝 授 修 述 術 準 序 招 承 証 条 状 常 情 織 職 制 性 政 勢 精 製 税 責 績 接 設
 舌 絶 銭 祖 素 総 造 像 増 則 測 属 率 損 退 貸 態 団 断 築 張 提 程 適 敵 統 銅 導 徳 独 任 燃 能 破 犯 判 版 比 肥
 非 備 俵 評 貧 布 婦 富 武 復 複 仏 編 弁 保 墓 報 豊 防 貿 暴 務 夢 迷 綿 輸 余 預 容 略 留 領"""
k6 = """異 遺 域 宇 映 延 沿 我 灰 拡 革 閣 割 株 干 巻 看 簡 危 机 揮 貴 疑 吸 供 胸 郷 勤 筋 系 敬 警 劇 激 穴 絹
 権 憲 源 厳 己 呼 誤 后 孝 皇 紅 降 鋼 刻 穀 骨 困 砂 座 済 裁 策 冊 蚕 至 私 姿 視 詞 誌 磁 射 捨 尺 若 樹 収 宗 就
 衆 従 縦 縮 熟 純 処 署 諸 除 将 傷 障 城 蒸 針 仁 垂 推 寸 盛 聖 誠 宣 専 泉 洗 染 善 奏 窓 創 装 層 操 蔵 臓 存 尊
 宅 担 探 誕 段 暖 値 宙 忠 著 庁 頂 潮 賃 痛 展 討 党 糖 届 難 乳 認 納 脳 派 拝 背 肺 俳 班 晩 否 批 秘 腹 奮 並 陛
 閉 片 補 暮 宝 訪 亡 忘 棒 枚 幕 密 盟 模 訳 郵 優 幼 欲 翌 乱 卵 覧 裏 律 臨 朗 論"""


def main():

    # first run unzip jmdict
    if (os.path.isfile('data/jmdict.zip') is True
        and os.path.isfile('data/jmdict.db') is False):
        try:
            with zipfile.ZipFile('data/jmdict.zip', 'r') as zip:
                zip.extractall('data/')
                # cleanup
                if os.path.isfile('data/jmdict.zip'):
                    os.remove('data/jmdict.zip')
                if os.path.isdir('data/__MACOSX'):
                    os.remove('data/__MACOSX')
        except:
            pass

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
    _file = open(filepath, "r", encoding="utf-8")
    text = _file.read()
    _file.close()

    # extract kanji - count kanji - sort count
    text2 = re.findall(kanji, text)

    if text2 is []:
        dialogs.alert("⚠️ Alert",
                      "This file contains no kanji, script cancelled",
                      "OK",
                      hide_cancel_button=True)
        print("file contains no kanji")
        sys.exit("file contains no kanji")
    kanji_count = (list(map(lambda kanji_character:
                  (kanji_character, text2.count(kanji_character)), set(text2))))
    kanji_count.sort(key=lambda a: a[1], reverse=True)
    kanji_list = list(map(lambda kanji_character: kanji_character, set(text2)))

    # show kanji count at each level
    tk1 = []
    tk2 = []
    tk3 = []
    tk4 = []
    tk5 = []
    tk6 = []
    tk0 = []

    # sieve and seperate kanji by level
    for i in kanji_count:
        if i[0] in k1:
            tk1 = tk1 + [i]
        elif i[0] in k2:
            tk2 = tk2 + [i]
        elif i[0] in k3:
            tk3 = tk3 + [i]
        elif i[0] in k4:
            tk4 = tk4 + [i]
        elif i[0] in k5:
            tk5 = tk5 + [i]
        elif i[0] in k6:
            tk6 = tk6 + [i]
        else:
            tk0 = tk0 + [i]

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

    # word list --  segment text then discard all but kanji groups #
    segmenter = tinysegmenter.TinySegmenter()
    text_tokenized = ' | '.join(segmenter.tokenize(text))
    word_list = text_tokenized.split(" | ")

    # filter for kanji words
    kanji_word_list = []
    for segment in word_list:
        for i in kanji_list:
            if i in segment:
                kanji_word_list.append(segment)

    kanji_word_list = list(set(kanji_word_list))
    kanji_word_list.sort()
    # build dictionary from sub.csv
    # fragile ?
    with open("data/sub.csv", encoding='utf-8', newline='\n') as csvtext:
        input = csv.reader(csvtext)
        subdict = {str(row[0]):str(row[1]) for row in input}
    # substitute values in kanji_word_list
    sublist =  [subdict.get(item,item) for item in kanji_word_list]
    sublist = set(sublist)
    try: sublist.remove("x")
    except: pass
    kanji_word_list = sublist

    kanji_word_list = user_editlist(kanji_word_list, "Edit kanji list")

    # filter for kana words

    # filter segments beginning or ending with ッ or っ as non-words
    temp_word_list = []
    for x in word_list:
        if re.search(r"^っ.|.っ$|^ッ.|.ッ$", x) is None:
            temp_word_list += [x]
    word_list = temp_word_list
    kana_word_list = []
    for x in word_list:
        if (len(x) >= 3
            and re.search(kanji, x) is None
            and re.search(ascii_char, x) is None):
            kana_word_list += [x]
    kana_word_list = list(set(kana_word_list))
    kana_word_list.sort()
    # substitute values in kana_word_list
    sublist =  [subdict.get(item, item) for item in kana_word_list]
    sublist = set(sublist)
    try: sublist.remove("x")
    except: pass
    kana_word_list = sublist

    kana_word_list = user_editlist(kana_word_list, "Edit kana list")

    # note : change variable name ?
    kanji_word_list += kana_word_list

    kanji_word_listp = ", ".join(map(str, kanji_word_list))  # pretty

    # omit list
    # fragile ?
    omitwordlist = []
    omitted_words = []
    with open("data/omit.csv", encoding='utf-8', newline='\n') as text3:
        input = csv.reader(text3)
        for row in input:
            if re.search(r"//", str(row)) is None:
                try: omitwordlist.append(row[0])
                except: pass  # ignore index out of range for blank lines
        omitted_words = list(
            set(omitwordlist).intersection(set(kanji_word_list)))
        kanji_word_list = list(
            set(kanji_word_list).difference(set(omitwordlist)))
        omitted_wordsp = ", ".join(map(str, omitted_words))  # pretty

    # search corelist
    print("searching corelist...")
    connection = sqlite3.connect("data/core.db")
    cursor = connection.cursor()
    core_output = ""
    flashcards = ""
    core_remaining_words = []

    for target in kanji_word_list:
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
            flashcards += (str(definition[0]) + "\t" + str(definition[1])
                           + "\t" + str(definition[3]) + "\n")
        else:
            core_remaining_words += [target]

    connection.commit()
    connection.close()

    # search sieve list
    print("searching sieve list...")
    connection = sqlite3.connect("data/sieve.db")
    cursor = connection.cursor()
    sieve_output = ""
    sieve_remaining_words = []
    # search for kanji & kana
    for target in core_remaining_words:
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
            flashcards += (str(definition[0]) + "\t" + str(definition[1])
                           + "\t" + str(definition[3]) + "\n")
        else:
            sieve_remaining_words += [target]

    connection.commit()
    connection.close()

    # search jmdict
    print("searching jmdict for kanji...")
    connection = sqlite3.connect("data/jmdict.db")
    cursor = connection.cursor()

    # search for kanji and katakana
    jmdict_output = ""
    jm_remaining_words = []
    for target in sieve_remaining_words:
        definition = cursor.execute(
            """SELECT words_jp.kanji, words_jp.reading,
                      words_jp.tags, words_en.def
               FROM words_jp  INNER JOIN words_en ON words_jp.ID=words_en.JPID
               WHERE words_jp.kanji = ? """,
            (target,), ).fetchone()
        if definition is not None:
            jmdict_output += ("[" + str(definition[0]) + "]"
                              + "(" + url_scheme + str(definition[0])
                              + url_scheme_postfix + ") : "
                              + "【" + str(definition[1]) + "】,"
                              + " (" + str(definition[2]) + "), "
                              + str(definition[3]) + "  \n")
            flashcards += (str(definition[0]) + "\t" + str(definition[1])
                           + "\t" + str(definition[3]) + "\n")
        else:
            jm_remaining_words += [target]

    # search jmdict for kana only
    print("searching jmdict for kana...")

    sieve_remaining_kana = list(
        set(jm_remaining_words).intersection(set(kana_word_list)))
    jm_remaining_kanji = list(
        set(jm_remaining_words).difference(set(kana_word_list)))
    jm_remaining_kana = []
    for target in sieve_remaining_kana:
        definition = cursor.execute(
            """SELECT words_jp.kanji, words_jp.reading,
                      words_jp.tags, words_en.def
               FROM words_jp  INNER JOIN words_en ON words_jp.ID=words_en.JPID
               WHERE words_jp.reading = ? """,
            (target,), ).fetchone()
        if definition is not None:
            jmdict_output += ("[" + str(definition[0]) + "]"
                              + "(" + url_scheme + str(definition[0])
                              + url_scheme_postfix + ") : "
                              + "【" + str(definition[1]) + "】,"
                              + " (" + str(definition[2]) + "), "
                              + str(definition[3]) + "  \n")
            flashcards += (str(definition[0]) + "\t" + str(definition[1])
                           + "\t" + str(definition[3]) + "\n")
        else:
            jm_remaining_kana += [target]

    connection.commit()
    connection.close()

    remaining_words = jm_remaining_kana + jm_remaining_kanji
    orphan = ""
    for word in remaining_words:
        orphan = (orphan + "[" + word + "]"
                  + "(" + url_scheme + word + ") :  \n")

    print("formatting ... \n\n")

    # prettify text
    # list of tuples [(x,y)] to string x(y)
    def pretty(text):
        text = " ".join(map(str, text))
        text = text.replace("(", "").replace(", ", "(").replace("'", "")
        return text

    kanji_countp = pretty(kanji_count)

    tk1p = pretty(tk1)
    tk2p = pretty(tk2)
    tk3p = pretty(tk3)
    tk4p = pretty(tk4)
    tk5p = pretty(tk5)
    tk6p = pretty(tk6)
    tk0p = pretty(tk0)

    sieve_remaining_wordsp = str(sieve_remaining_words).replace(
        "[", "").replace("'", "").replace("]", "")
    remaining_wordsp = str(remaining_words).replace("[", "").replace(
        "'", "").replace("]", "")
    core_remaining_wordsp = str(core_remaining_words).replace("[", "").replace(
        "'", "").replace("]", "")

    # output to console #
    print(text)
    print("\ncharacters in text:", len(text))
    print(_line_)
    print("kanji in text:", len(text2))
    print("discrete kanji in text:", len(kanji_count), "\n")
    print(kanji_countp)
    print(_line_)
    print("    1年:", len(tk1))
    print(tk1p)
    print(_line_)
    print("    2年:", len(tk2))
    print(tk2p)
    print(_line_)
    print("    3年:", len(tk3))
    print(tk3p)
    print(_line_)
    print("    4年:", len(tk4))
    print(tk4p)
    print(_line_)
    print("    5年:", len(tk5))
    print(tk5p)
    print(_line_)
    print("    6年:", len(tk6))
    print(tk6p)
    print(_line_)
    print("   中学+:", len(tk0))
    print(tk0p)
    print(_line_)
    print("words or word fragments searched in text:",
          len(kanji_word_list), "\n")
    print(kanji_word_listp, "\n")
    print("omitted from search:", len(omitted_words), "\n")
    print(omitted_wordsp)
    print(_line_)
    print("core 6k list:  \n")
    print(core_output)
    print("remaining:", len(core_remaining_words), "\n")
    print(core_remaining_wordsp)
    print(_line_)
    print("sieve list:  \n")
    print(sieve_output)
    print("remaining:", len(sieve_remaining_words), "\n")
    print(sieve_remaining_wordsp)
    print(_line_)
    print("jmdict:  \n")
    print(jmdict_output)
    print("remaining:", len(remaining_words), "\n")
    print(remaining_wordsp)
    print(_line_)
    print(orphan)
    print("\n\nSaving to file ... \n\n")

    # text for output #
    sieved_text = (f'''
{text} \n
__characters in text:__ {len(text)}
{_line_}
__kanji in text:__ {len(text2)}  \n
__discrete kanji in text:__ {len(kanji_count)} \n
{kanji_countp}
{_line_}
1.  __第一学年:__ {len(tk1)}  \n
{tk1p}
{_line2_}
2.  __第二学年:__ {len(tk2)}  \n
{tk2p}
{_line2_}
3.  __第三学年:__ {len(tk3)}  \n
{tk3p}
{_line2_}
4.  __第四学年:__ {len(tk4)}  \n
{tk4p}
{_line2_}
5.  __第五学年:__ {len(tk5)}  \n
{tk5p}
{_line2_}
6.  __第六学年:__ {len(tk6)}  \n
{tk6p}
{_line2_}
7.  __中学以上:__ {len(tk0)}  \n
{tk0p}
{_line_}
__words or word fragments searched in text:__ {len(kanji_word_list)} \n
{kanji_word_listp} \n
__omitted from search:__ {len(omitted_words)} \n
{omitted_wordsp} \n
{_line_}
__Glossary:__  \n
{_line2_}
__Core 6k list:__  \n\n
{core_output} \n
__remaining words:__ {len(core_remaining_words)}  \n
{core_remaining_wordsp}
{_line_}
__sieve list:__  \n
{sieve_output} \n
__remaining words:__ {len(sieve_remaining_words)}  \n
{sieve_remaining_wordsp}
{_line_}
__jmdict list:__  \n
{jmdict_output} \n
__remaining words:__  {len(remaining_words)}  \n
{remaining_wordsp}  \n
{_line_}
{orphan}  \n
{_line2_}
_generated with [Kanji Sieve {VERSION}](https://github.com/takarabune/kanji_sieve)_
    ''')

    # save output #
    newdir = "kanji sieve output/"
    newfile = Path(newdir)
    if not newfile.is_dir():
        os.mkdir(newdir)
    newname = Path(filepath).stem + "_" + choice + "_笊.md"
    newpath = "kanji sieve output/" + newname
    newfile = Path(newdir + newname)
    newpath = add_unique_postfix(newfile)
    newtext = ("### " + Path(filepath).stem
               + "  \n_" + time.ctime()
               + "_  \n\n" + sieved_text)
    newfile = open(newpath, "w", encoding="utf-8")
    newfile.write(newtext)
    newfile.close()

    # save flashcards #
    newdir = "flashcards output/"
    newfile = Path(newdir)
    if not newfile.is_dir():
        os.mkdir(newdir)
    newname = Path(filepath).stem + "_flashcards.tsv"
    newpath = "flashcards output/" + newname
    newfile = Path(newdir + newname)
    newpath = add_unique_postfix(newfile)
    newtext = flashcards
    newfile = open(newpath, "w", encoding="utf-8")
    newfile.write(newtext)
    newfile.close()

    # append to orphans file
    newfile = open("kanji sieve output/orphans.md", "a", encoding="utf-8")
    newfile.write("\n\n" + Path(filepath).stem + "  \n"
                 + time.ctime() + "  \n" + orphan)
    newfile.close()

    # prepare substitute list from orphans.
    newfile = open("kanji sieve output/" + Path(filepath).stem
                 + "_orphans.csv", "w", encoding="utf-8")
    newfile.write("\n".join(map(str, remaining_words)))
    newfile.close()

    print("saved \n")


if __name__ == '__main__':
    main()


