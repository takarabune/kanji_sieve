# -----------------------------------------#
#   Kanji Sieve 1.18 for Pythonista 3
#   2023-12-16
#   (c)Robert Belton BSD 3-Clause License
#
#
#   Takes a text, extracts the kanji &
#   analyzes them by kyouiku level
#   Outputs a word list with links to
#   monokakido's Reikoku dictionary app.
#   Outputs a tsv file suitable for use in
#   Flashcard Deluxe
#
#   requires:
#      data/dict.db
#
#   will build (if not present):
#      data/omit.ksv
#      data/sub.ksv
#      data/kanji_sieve.pref
#      data/orphans.ksv
#
#   dependencies:
#      tinysegmenter
#      
#
# -----------------------------------------#


import tinysegmenter # 3rd party
import dialogs  # pythonista only
import ui  # pythonista only
import re
import sys
import time
import sqlite3
import os
import csv
import zipfile
import webbrowser
import bz2
from base64 import b64decode
from markdown2 import Markdown 
from pathlib import Path

# ------------------------------------------------------------------- constants
VERSION = "1.18"

# decoration snippets
_LINE_ = "\n----------------\n"

# regex patterns
KANJI = r'[㐀-䶵一-鿋豈-頻]'
ASCII_CHAR = r'[ -~]'

# html fragments to build webview # 
HTML_1 = '''
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes" />
        <title>Markdown</title>
        <style>
        '''
HTML_2 = '''            
        </style>
        </head>
        <body>

                <div id="content">
'''
HTML_3 = '''
                </div>
        </body>
        </html>
'''
CSS = '''
        * {
                font-size: 16px;
                font-family: AppleSDGothicNeo-Regular, Helvetica, sans-serif;
                color: #000000;
                text-align: left;
                -webkit-text-size-adjust: none;
                -webkit-tap-highlight-color: transparent;
        }
        a {
                color: #ff0000;
                text-decoration: none;
        }
        h1 {
                font-size: larger;
        }
        h3 {
                font-style: bold;
        }
        h4 {
                font-weight: normal;
                font-style: italic;
        }
        code {
                font-family: monospace;
        }
        li {
                margin: .4em 0;
        }
        body {
                line-height: 1.5;
        }
'''

# ---------------------------------------------------base 64 encoded pyui files
ks_gui = '''\
QlpoOTFBWSZTWRM2EsgAHvlfgHUQUGd/9T/fn4q//9/6YAo/B8ifWAREKAAOxqlCShQHQy
kmhpoBoyGTQNAGmjQMgGgADjJkyYjEwAmTBMgBowjAEMBxkyZMRiYATJgmQA0YRgCGAaaS
ZINAjTRkwCMCZMTJhGGQCMIpCZGgTUxSaGnpGjQGmgGgGhgmIClJECTQyaTMqemoaaDEeg
j0mRoD1APKcZ3MeQYskpiJL6Unjvfnw8ejbG+CfckxVWyTEnkScDpno1a1jMZmWNa1GMxr
N0qcBZKlisqYcuXPpKgnSCl6lOowql72OmIwyMZDDMrFYiYrJVjCE0RRPT5/PX05+r/I8u
aiW9+QixMkl9pKJqiJLXw96CDt+abOCcRM+2JzqGoe3kLpONSjaLSGtss2Zb41mhN1TR2p
WaZm2NHZwmMpaTDFaVo1kU29yNUtYrCrlSaxG+1JzR7/T5eWPUqUuLEOAidzE7Faql/DfM
9UFPTcQ1QOxUpLojHZu7d9H0liAiCGjipihy/m4TBk+EcE7TGiRXJeV4rJDzPGkyZAiJoK
UwQSTAqEoYZZL9km85ahrz/veNcGyd6HpBjPlmGcAnuAPdCHshlgvo9iTSvZiswjUMhlTK
mZtrW+EyZm7RVb4G5lijKm5G+kmyTfW6MxbJNtDbMQzfUNMSYlPalbJXje7nrwy1Ewk2Sa
SaSeFkfT+1WkcchkMi+rFmV67hvtI44zMwj5chaymYMsKt/XFoWubZnDGmzW21yqbq5qyP
bmmWtNNuLg9ummZ0uAm3PG5jLCDCMO2JUlIqSNERNlArEwChhUkXMcAqUhEMLFsAoNYVKQ
GUfeECwHBw7KmguOKpAuU4ZPgkLT81Seos7NFTXt+Z2JXVIzFYVhgmUW2SqeNt+7Z1q8cd
WMx3QwXm4ff5FeO+0PrDDKMxgwMLLMZk4SqdTFVOnMHkRFPkVJYGY7Brariqc9XqVcbqkb
qn4ONsYiKkEjsofH43VUgE2AwQMaxGjKRBEEaFnhVHsV9uKNAHqL2OYDTdUmySiIc0GQsn
p13AaBV3uHdpkz5ykYgPh6b0q8qvI6PE9NTnNqN1ZEeLsaOxwNdSljpAUJhTQXHN+7uSIY
MC6iWFjmxBEQREOsMq4G7pADAcYopsswDGZcgJGMjinAuHJjdnQnRHOFdAkIzKVdWypnJG
8iMbTJ3VKi2JC6i0ls8IMzVEN5bG7dNEQkqbWBDhq7qmdyBaURDcc7XOVAJkYFywslTmqZ
EhgXJkBJ0tDcWWQcc9dXDgXIxFuyMirUCbWYtDNtY8GRGqpS36iyccQoqcj4erNwNrU0VO
OjW1LIHZNRxAaBxU6tCWUBlkqYSFvfMXQyVIOMiJizIjXIDpZUoarnU1bhi7kqTHkLKqpy
dOuCpdrZzNhYVsQ6aIiiaqnsVOYi1a7aBkqZi4aixgLuLFz8lQ1VLtGrwyVLqn7iLiIFtO
InIWTpHKnuAtRHbnOjn5pW6qmyplngEt0Q7BdGqtgoqcYi5ZeYRd/RNPxgUTBj+vXOZBJo
ox14I4iJIaSkFgI9vhCQKZIIzOPggiJwKCOeX8Ptq1lifOrWK0vq/DQt83+/2bDdGJOX38
N0eZU+ypx38RXmJxR4aF1pXCg3kn9Huw6cv8cTZSf8dKToz4zyyBfWiB1goVQKIhvU9CKU
HCXPbPIK4dJJySso9HNN4XCGabu30NkiiiYixDPcFi3jgxMUQyUS48csPF5DVzOiP4+VHb
SdfYrqqZmMveyVXwibfHnD4uVmGZZkzb57+T07QuPfSa818u4725PFhFO1EDRAeWSpe30Z
8APrxNVC/wCEiOprVJqU8nAeetUmwvnZTvHr60rT1+VEtJ4vNh1KPArfojuXj/L6N9nyq+
HilPT3J9L1JOiPo/zPx81d4uz5OTT8jo9vHtef5tbMU7b6t3a+b5GpxhrGkeiJ+L3j3zwd
tKHXvIsg75BbqiBCp06VRE52QNkD4su/dAZ3E8PNRIAfioYZCLQRdSdTZr07ijsFu9/q5b
CdfHVaxNZt1C66TY6ivMjyOLHLPzC5UmxuLlBhCAFOU7eCUqzobKJn3jhA6CLgXwugTEyd
yJ50rlI+vn/PEdHf1bfh/12lbvX1bvXwXf6ns5jzej0pWd+Ct0eeSbb1HToO3bnKaVw2R8
TwK0+PGZxnA8HW8sk9Wshik4Zux1eCVkL4cdDn1uyCTmiJM5qnQqYVzqexU0AYlztp3R3g
ma3PXjJmMyZnDk5w582bbZGy0LbsGomm+9JzqdKp10O9Hm5NuKPWxqHJvD1dnTd2CayU3n
DjuJ3Smzk6HP5s8JySdbv6OzYrqR4vI8N3olOxz8P7Q3WQ50nk+LfFs7u5GnVvSZkjtO77
PG89TtidT/STEnuqwVjJhMmQzBiMqeKSbbf7kn3bRPuSGeGKJWDawKVACb4mCENVoKl8q+
C1rnKXlCsY7dWxyVvZRwy9zaHFlT/4u5IpwoSAmbCWQA==
    '''
ks_pyui = bz2.decompress(b64decode(ks_gui))


a2d_gui = 	data = '''\
QlpoOTFBWSZTWUhVyW8AFmtfgFUQUGd/9T+UHYq//976YAbfAOgT7fYOuiBURJJHMABMmA
BMJgmEMARgA5gAJkwAJhMEwhgCMADI0KU3qgAxNAAAyaAAAAYqRoDQZAZADCAADQ0ACaqk
NI2jKn6TIJMgAABo0AA0ClJFNMqfpCPKPQU09CGeKjygPUPSY09TKdEuoGVEndQ53xz5c9
G2G+VX96GRLahlDqodHnxmSz0amsWY3qV0SslFiydPTx5FQHJSk9T8cJF0qmUMBclEPjtE
cMI3qGt/X9pnqxrIenPj+vloe5VmTx2TcrxjZsVZm1anRKMVYWZKPxW61QwjhIwjqfHs9f
XjgfBmYMymYt6Gp7BdfUq3XhPFbC7Pp/Du7e/nnMmqquJ0QZoDMIvEGQWX3fi/a17NSzoi
IgYiLNmc+UwZdi7f02b5OwXBeqdi4i3nFVTuoff3UNKu5i3m01MVYq3ytgt8WaiW26tUMk
3kt9qGi2ob6rVDW0TfKG9Q9EbR6Xv468+WkMUNqGqGlXfMEd01oad7I1mGYFssDUzMNsq1
kawACFkw4MTOSAEzpknTJOmGvsU9M7JkgHKIdEIFyQA9VQSdMkkLEkAZ5JsGDMDdivbXoh
rDzrCGxbIcFb6rDCS7peHlrZV5Jn86/CswZjQPoVZB5vYACoQQNZDJFYElp/ytHd+CWW7i
SSVlhhJJsEUFsh1jwhtKtiqwqX2rctYcs9NNOhlDJasFsh4rbDxeEMcVyWPfFWfLPPPI8l
nDicoq2UXFYrhwyyy5lWvg44WGGGGFhyPHMq6FWkPUtNNNNO3sXSGwvFnDM2xlllll0jeZ
GCzh5rjy7/HrtURECZEzMy0RCENMzMXAksSgScBGkqBJxWDruOCyXfDwXJb4cCrOOEPBjV
a3oZOc+qc1EP30O+h0zqjrDhDavJepflV+2FYLCWGE3rGHdDGGi4Q9auUO9dV4wxXatFzX
mh2zNYw5+9DoVfVQ7ldip6yrCKcCPv7/Ch7vT7fmr2ZQ0sofwF/IWLFssX/U75r8/b0LzU
PgR0VDaoeK/bFr8t+Qj9eJHELKr2hlf1kZOhVtzVbVDhGL3KtkHDbKGpHAq47hfNXAjjXS
v7EdhHlCyVhZKPlQ2+X1/kq8hHNV2ka84MId45UOFK5Q3lXmMyr/ltXDmsX7baIwjblzI2
nQVYvWR9IMlRYQ7ErsKvLfMoeyapX2dSr+p8VD2alXPjDiqtk6lWk1laBqNi2Crd2w3VU7
8Yemle0Vbov3Roj5wuvehvuqHOhr0LFWy3+uhyI348Vw7elYq0vsodIWt6G/SoanfzLrVY
R9Ea4A8qh88amNK1NOX90O6HnmpqrWV0mYq9G4yhqlb9s6YQ28sN3EVdZsqVicyNdRHVQ7
NKuVQ81Dj4nRQzzKuQWkG1Q6yOqhqcJHKnaYZbw3Q36JXp7d6VnQ59hVtqmvhMvBK3Q5FX
dwmBJwuVD2FXAq8j9KGUP/YrKyYZWWSMFYOVQ218Kh4bIeFD81e+YrFXu1Xvir/xdyRThQ
kEhVyW8=
    '''
a2d_pyui = bz2.decompress(b64decode(a2d_gui))


# kyouiku lists #
K1 = """一 右 雨 円 王 音 下 火 花 貝 学 気 九 休 玉 金 空 月 犬 見 五 口 校 左 三 山 子 四 糸 字 耳 七 車 手 十 出
 女 小 上 森 人 水 正 生 青 夕 石 赤 千 川 先 早 草 足 村 大 男 竹 中 虫 町 天 田 土 二 日 入 年 白 八 百 文 木 本 名
 目 立 力 林 六"""
K2 = """引 羽 雲 園 遠 何 科 夏 家 歌 画 回 会 海 絵 外 角 楽 活 間 丸 岩 顔 汽 記 帰 弓 牛 魚 京 強 教 近 兄 形 計
 元 言 原 戸 古 午 後 語 工 公 広 交 光 考 行 高 黄 合 谷 国 黒 今 才 細 作 算 止 市 矢 姉 思 紙 寺 自 時 室 社 弱 首
 秋 週 春 書 少 場 色 食 心 新 親 図 数 西 声 星 晴 切 雪 船 線 前 組 走 多 太 体 台 地 池 知 茶 昼 長 鳥 朝 直 通 弟
 店 点 電 刀 冬 当 東 答 頭 同 道 読 内 南 肉 馬 売 買 麦 半 番 父 風 分 聞 米 歩 母 方 北 毎 妹 万 明 鳴 毛 門 夜 野
 友 用 曜 来 里 理 話"""
K3 = """悪 安 暗 医 委 意 育 員 院 飲 運 泳 駅 央 横 屋 温 化 荷 界 開 階 寒 感 漢 館 岸 起 期 客 究 急 級 宮 球 去
 橋 業 曲 局 銀 区 苦 具 君 係 軽 血 決 研 県 庫 湖 向 幸 港 号 根 祭 皿 仕 死 使 始 指 歯 詩 次 事 持 式 実 写 者 主
 守 取 酒 受 州 拾 終 習 集 住 重 宿 所 暑 助 昭 消 商 章 勝 乗 植 申 身 神 真 深 進 世 整 昔 全 相 送 想 息 速 族 他
 打 対 待 代 第 題 炭 短 談 着 注 柱 丁 帳 調 追 定 庭 笛 鉄 転 都 度 投 豆 島 湯 登 等 動 童 農 波 配 倍 箱 畑 発 反
 坂 板 皮 悲 美 鼻 筆 氷 表 秒 病 品 負 部 服 福 物 平 返 勉 放 味 命 面 問 役 薬 由 油 有 遊 予 羊 洋 葉 陽 様 落 流
 旅 両 緑 礼 列 練 路 和"""
K4 = """愛 案 以 衣 位 囲 胃 印 英 栄 塩 億 加 果 貨 課 芽 改 械 害 街 各 覚 完 官 管 関 観 願 希 季 紀 喜 旗 器 機
 議 求 泣 救 給 挙 漁 共 協 鏡 競 極 訓 軍 郡 径 型 景 芸 欠 結 建 健 験 固 功 好 候 航 康 告 差 菜 最 材 昨 札 刷 殺
 察 参 産 散 残 士 氏 史 司 試 児 治 辞 失 借 種 周 祝 順 初 松 笑 唱 焼 象 照 賞 臣 信 成 省 清 静 席 積 折 節 説 浅
 戦 選 然 争 倉 巣 束 側 続 卒 孫 帯 隊 達 単 置 仲 貯 兆 腸 低 底 停 的 典 伝 徒 努 灯 堂 働 特 得 毒 熱 念 敗 梅 博
 飯 飛 費 必 票 標 不 夫 付 府 副 粉 兵 別 辺 変 便 包 法 望 牧 末 満 未 脈 民 無 約 勇 要 養 浴 利 陸 良 料 量 輪 類
 令 冷 例 歴 連 老 労 録"""
K5 = """圧 移 因 永 営 衛 易 益 液 演 応 往 桜 恩 可 仮 価 河 過 賀 快 解 格 確 額 刊 幹 慣 眼 基 寄 規 技 義 逆 久
 旧 居 許 境 均 禁 句 群 経 潔 件 券 険 検 限 現 減 故 個 護 効 厚 耕 鉱 構 興 講 混 査 再 災 妻 採 際 在 財 罪 雑 酸
 賛 支 志 枝 師 資 飼 示 似 識 質 舎 謝 授 修 述 術 準 序 招 承 証 条 状 常 情 織 職 制 性 政 勢 精 製 税 責 績 接 設
 舌 絶 銭 祖 素 総 造 像 増 則 測 属 率 損 退 貸 態 団 断 築 張 提 程 適 敵 統 銅 導 徳 独 任 燃 能 破 犯 判 版 比 肥
 非 備 俵 評 貧 布 婦 富 武 復 複 仏 編 弁 保 墓 報 豊 防 貿 暴 務 夢 迷 綿 輸 余 預 容 略 留 領"""
K6 = """異 遺 域 宇 映 延 沿 我 灰 拡 革 閣 割 株 干 巻 看 簡 危 机 揮 貴 疑 吸 供 胸 郷 勤 筋 系 敬 警 劇 激 穴 絹
 権 憲 源 厳 己 呼 誤 后 孝 皇 紅 降 鋼 刻 穀 骨 困 砂 座 済 裁 策 冊 蚕 至 私 姿 視 詞 誌 磁 射 捨 尺 若 樹 収 宗 就
 衆 従 縦 縮 熟 純 処 署 諸 除 将 傷 障 城 蒸 針 仁 垂 推 寸 盛 聖 誠 宣 専 泉 洗 染 善 奏 窓 創 装 層 操 蔵 臓 存 尊
 宅 担 探 誕 段 暖 値 宙 忠 著 庁 頂 潮 賃 痛 展 討 党 糖 届 難 乳 認 納 脳 派 拝 背 肺 俳 班 晩 否 批 秘 腹 奮 並 陛
 閉 片 補 暮 宝 訪 亡 忘 棒 枚 幕 密 盟 模 訳 郵 優 幼 欲 翌 乱 卵 覧 裏 律 臨 朗 論"""

class HTMLviewer (object):
    def webview_should_start_load(self, webview, url, nav_type):
        # Open 'http(s)' links in Safari
        # x-url for Reikoku 
        if nav_type == 'link_clicked':
            if url.startswith('http:') or url.startswith('https:'):
                url = 'safari-' + url
            webbrowser.open(url)
            return False
        return True
        

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
     

def init_bool_pref(pref, value):
        if value == "1":
            v[pref].title = "✔︎"
        elif value == "0":
            v[pref].title = ""
        else:
            pass
            
            
def init_dict_pref(pref):
        v[pref].title = "✔︎"


def select_dict(self):
    v['weblio'].title = ""
    v['wik-eng'].title = ""
    v['wik-jpn'].title = ""
    v['jisho'].title = ""
    v['eijiro'].title = ""
    v['reikoku'].title = ""
    self.title = "✔︎"
    PREFS.update({"dict":self.name})   


def load_prefs(path):
    if os.path.isfile(path) is False:
        defaultprefs = {'dict': 'weblio', 'tsv_out': '1', 'orphan_out': '1', 'kyouiku': '1', 'core': '1', 'user': '1', 'orphan': '1', 'jmdict': '1', 'add_orphans': '1'} 
        write_prefs(defaultprefs, path)
    with open(path, encoding='utf-8', newline='\n') as csvtext:
        input = csv.reader(csvtext)
        prefs = {str(row[0]):str(row[1]) for row in input}
    return prefs


def write_prefs(PREFS, path): 
    with open(path,'w') as f:
        w = csv.writer(f)
        w.writerows(PREFS.items())
        

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
    sieve()


def echo(text):
    print(text)
    #v['textbox'].text += text + "  \n"


def html_convert_display(md_text):
    markdowner = Markdown()
    html_text = markdowner.convert(md_text)
    html_text_raw = HTML_1 + CSS + HTML_2  +  html_text + HTML_3
    v['webview1'].load_html(html_text_raw)

def text_transform(text):
    out = text.replace("//,", "//=")
    out = out.replace(",", " <---> ")
    out = out.replace("//=", "//,")
    return out
    

def sanitise_text(text):
    out = text.replace("<--->", ",")
    out = out.replace("、", ",")
    out = out.replace(" ", "")
    out = out.replace("\n,\n", "\n")
    out = out.replace(",\n", ",x\n")
    out = out.replace("\n", "\n\n")
    out = re.sub(r"\n([^,^\n]+)\n", r"\n\1,x\n", out)
    out = out.replace("\n\n", "\n")
    out = out.replace("\n\n", "\n")
    out = out.replace("\n,", "\nx,")
    return out


def edit_substitutes_button(sender):
    # initialise file 
    if os.path.isfile("data/sub.ksv") is False:
        default_text = '''//,on.save.this.file.will.be.stripped.of.white.space
//,Japanese.comma.will.be.convereted.to.ascii.comma
//,the.script.expects.pairs.of.terms.seperated.by.a.comma
//,term.[comma].substitute
//,.,.is.only.for.display.purposes.
//,.,.will.be.converted.to.commas.on.save.or.exit.
//,entry.should.be.made.using.commas.between.terms
//,for.a.blank.substitute.an.x.will.be.inserted.and.the.term
//,won't.be.used.for.search.
//,multiple.blank.lines. will.be.reduced.by.half.
//,blank.lines.and.lines.starting '//[comma]'are.ignored.in
//,.the.script.but.are.still.stripped.of.white.space.
//,.this.text.can.be.deleted.
    '''
        with open("data/sub.ksv", "w", encoding = "utf8") as newfile:
            newfile.write(default_text)
            newfile.close()
        
    with open("data/sub.ksv", "r", encoding = "utf8") as file:
        if PREFS["add_orphans"] == "1":
            with open("data/orphans.ksv", "r", encoding = "utf8") as file2:
                d_input = text_transform(file.read()) + "\n" + file2.read()
        else:
            d_input = text_transform(file.read())
            
        output = dialogs.text_dialog(title="Edit Substitute List", text=d_input )
        
    if output is not None:
        output = sanitise_text(output)
        with open("data/sub.ksv", "w", encoding = "utf8") as newfile:
            newfile.write(output)
            newfile.close()


def edit_omit_button(sender):
    # initialise file 
    if os.path.isfile("data/omit.ksv") is False:
        default_text = '''//this file contains words to omit from searches in kanji sieve.
//one word per line.
//a double slash at the start of a line will comment out the line. 
//blank lines ignored.
    '''
        with open("data/omit.ksv", "w", encoding = "utf8") as newfile:
            newfile.write(default_text)
            newfile.close()
        
    with open("data/omit.ksv", "r", encoding = "utf8") as file:
        if PREFS["add_orphans"] == "1":
            with open("data/orphans.ksv", "r", encoding = "utf8") as file2:
                d_input = file.read() + "\n" + file2.read()
        else:
            d_input = file.read()
            
        output = dialogs.text_dialog(title="Edit Omit List", text=d_input)
        
    if output is not None:
        with open("data/omit.ksv", "w", encoding = "utf8") as newfile:
            newfile.write(output)
            newfile.close()
    
    

def add2dict_button(sender):
    #write_prefs(PREFS, "data/kanji_sieve.pref")
    add_to_dict()


# --------------------------------------------------------------- add_to_dict
def add_to_dict():
        
    def populate_grid():
        if PREFS["add_orphans"] == "1":
            
            if len(orphans_list) in range (len(orphans_list), 7):
                for i in range (1, len(orphans_list)+1 ):
                    v2[("kanji" + str(i))].text = (orphans_list[len(orphans_list)-1])
                    orphans_list.pop(len(orphans_list)-1)
                    
            elif len(orphans_list) > 6:
                for i in range(1,7):
                    v2[("kanji" + str(i))].text = (orphans_list[len(orphans_list)-1])
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
            row = (v2['kanji'+ str(i)].text, v2['kana'+ str(i)].text, v2['eng'+ str(i)].text, v2['pos'+ str(i)].text, v2['jpn'+str(i)].text)
            if v2['kanji'+str(i)].text != "" and v2['kana'+str(i)].text != "" and v2['eng'+str(i)].text != "":
                data.append(row)
        
        if data != []:
            print("terms added:\n", data)
            #insert_data(data)
        clear_action(sender)
        dialogs.hud_alert(str(len(data))+" entries saved")
        populate_grid() 
        v2['kanji1'].begin_editing()

   
    def clear_action(sender):
        for i in range(1,7):
            v2['kanji'+str(i)].text = ""
            v2['kana'+str(i)].text = ""
            v2['eng'+str(i)].text = ""
            v2['pos'+str(i)].text = ""
            v2['jpn'+str(i)].text = ""
    
        v2['kanji1'].begin_editing()
        
      
    def exit_action(sender):
        v2.close()

  
    # build gui #
    v2 = ui.load_view_str(a2d_pyui.decode('utf-8'))
    
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
    
    v2.right_button_items = [save_button, clear_button]
    v2.left_button_items = [exit_button]
    
    v2.present('fullscreen', hide_close_button=True)
    
    # initialise grid #
    orphans_list =[]
    
    with open("data/orphans.ksv", encoding='utf-8', newline='\n') as csvtext:
        input = csv.reader(csvtext)
        orphans_list = [row[0] for row in input]
    
    populate_grid()

    v2['kanji1'].begin_editing()
    print(" terms added:")
    v.wait_modal()
    
    # on exit show user list contents #
    con = sqlite3.connect("data/dict.db")
    cur = con.cursor()
    print("\n\n user dictionary entries: \n")
    for row in cur.execute(
        "SELECT rowid, kanji, kana, eng, pos, jp FROM user ORDER by rowid"):
        print(row)
    con.commit()
    con.close()


# --------------------------------------------------------------- kanji sieve #

def sieve():
    
    v['textbox'].text = ""
    html_text =""
    html_convert_display(html_text)
    
    print("prefs:`" + str(PREFS) + "`")

    # ------------------------------------------------- first run unzip dict.db
    if (os.path.isfile('data/dict.zip') is True
        and os.path.isfile('data/dict.db') is False):
        print("unzipping 'data.zip'...")
        try:
            with zipfile.ZipFile('data/dict.zip', 'r') as zip:
                zip.extractall('data/')
                # cleanup
                if os.path.isfile('data/dict.zip'):
                    os.remove('data/dict.zip')
                if os.path.isdir('data/__MACOSX'):
                    os.remove('data/__MACOSX')
        except:
            pass

    spinner.bring_to_front()
    spinner.start()
    
    # ---------------------------------------------------- select file to sieve
    filepath = dialogs.pick_document(
        types=["public.utf8-plain-text", "public.text"])
    if filepath is None:
        spinner.stop()
        echo("user cancelled")
        #dialogs.alert("⚠️ Alert",
        #             "No file found, script cancelled",
        #             "OK",
        #             hide_cancel_button=True)
        sys.exit("user cancelled")
    file = open(filepath, "r", encoding="utf-8")
    text = file.read()
    file.close()

    
    # -------------------------------- extract kanji - count kanji - sort count
    text2 = re.findall(KANJI, text)

    if text2 is []:
        spinner.stop()
        dialogs.alert("⚠️ Alert",
                      "This file contains no kanji, script cancelled",
                      "OK",
                      hide_cancel_button=True)
        echo("file contains no kanji")
        sys.exit("file contains no kanji")
        
    kanji_count = (list(map(lambda kanji_character:
                  (kanji_character, text2.count(kanji_character)), set(text2))))
    kanji_count.sort(key=lambda a: a[1], reverse=True)
    kanji_list = list(map(lambda kanji_character: kanji_character, set(text2)))

    # ------------------------------------------ show kanji count at each level
    tk1 = []
    tk2 = []
    tk3 = []
    tk4 = []
    tk5 = []
    tk6 = []
    tk0 = []

    # --------------------------------------- sieve and seperate kanji by level
    for i in kanji_count:
        if i[0] in K1:
            tk1 = tk1 + [i]
        elif i[0] in K2:
            tk2 = tk2 + [i]
        elif i[0] in K3:
            tk3 = tk3 + [i]
        elif i[0] in K4:
            tk4 = tk4 + [i]
        elif i[0] in K5:
            tk5 = tk5 + [i]
        elif i[0] in K6:
            tk6 = tk6 + [i]
        else:
            tk0 = tk0 + [i]

    # ----------------------------------------------------- choose a dictionary

    choice = PREFS["dict"]

    url_scheme_postfix = ""

    if choice == "weblio":
        url_scheme = "https://ejje.weblio.jp/content/"
    elif choice == "eijiro":
        url_scheme = "https://eow.alc.co.jp/search?q="
    elif choice == "jisho":
        url_scheme = "https://jisho.org/search/"
    elif choice == "reikoku":
        url_scheme = "mkreikoku:///search?text="
    elif choice == "wik-eng":
        url_scheme = "https://en.m.wiktionary.org/wiki/"
        url_scheme_postfix = "#Japanese"
    elif choice == "wik-jpn":
        url_scheme = "https://ja.m.wiktionary.org/wiki/"
        
    echo(choice + " dictionary chosen for links...")

    # word list --  segment text then discard all but kanji groups #
    segmenter = tinysegmenter.TinySegmenter()
    text_tokenized = ' | '.join(segmenter.tokenize(text))
    word_list = text_tokenized.split(" | ")

    # -------------------------------------------------- filter for kanji words
    kanji_word_list = []
    for segment in word_list:
        for i in kanji_list:
            if i in segment:
                kanji_word_list.append(segment)

    kanji_word_list = list(set(kanji_word_list))
    kanji_word_list.sort()
    # ------------------------------------------- build dictionary from sub.ksv
    # fragile ?
    with open("data/sub.ksv", encoding='utf-8', newline='\n') as csvtext:
        input = csv.reader(csvtext)
        subdict = {}
        for row in input:
            if re.search(r"//", str(row)) is None:
                try: subdict.update( {str(row[0]):str(row[1])} )
                except: pass  # ignore index out of range for blank lines
    # substitute values in kanji_word_list
    sublist =  [subdict.get(item,item) for item in kanji_word_list]
    sublist = set(sublist)
    try: sublist.remove("x")
    except: pass
    kanji_word_list = list(sublist)

    # --------------------------------------------------- filter for kana words
    # filter segments beginning or ending with ッ or っ as non-words
    temp_word_list = []
    for x in word_list:
        if re.search(r"^っ.|.っ$|^ッ.|.ッ$", x) is None:
            temp_word_list += [x]
    word_list = temp_word_list
    kana_word_list = []
    for x in word_list:
        if (len(x) >= 3
            and re.search(KANJI, x) is None
            and re.search(ASCII_CHAR, x) is None):
            kana_word_list += [x]
    kana_word_list = list(set(kana_word_list))
    kana_word_list.sort()
    # substitute values in kana_word_list
    sublist =  [subdict.get(item, item) for item in kana_word_list]
    sublist = set(sublist)
    try: sublist.remove("x")
    except: pass
    kana_word_list = list(sublist)

    # note : change variable name ?
    kanji_word_list += kana_word_list

    kanji_word_listp = ", ".join(map(str, kanji_word_list))  # pretty

    # --------------------------------------------------------------- omit list
    # fragile ?
    omitwordlist = []
    omitted_words = []
    with open("data/omit.ksv", encoding='utf-8', newline='\n') as text3:
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


    connection = sqlite3.connect("data/dict.db")  
    cursor = connection.cursor()
     
    flashcards = ""
    
    # --------------------------------------------------------- search corelist
    if PREFS["core"] == "1":
        echo("searching corelist...")
        core_output = ""
        core_remaining_words = []
    
        for target in kanji_word_list:
            definition = cursor.execute(
                """SELECT core.kanji, core.kana, core.pos, core.eng
                   FROM core WHERE core.kanji = ? """,
                (target,), ).fetchone()
            if definition is not None:
                core_output += ("[" + str(definition[0]) + "]"
                                + "(" + url_scheme + str(definition[0])
                                + url_scheme_postfix + ") : "
                                + "【" + str(definition[1]) + "】"
                                + " (" + str(definition[2]) + ") "
                                + str(definition[3]) + "  \n")
                flashcards += (str(definition[0]) + "\t" + str(definition[1])
                               + "\t" + str(definition[3]) + "\n")
            else:
                core_remaining_words += [target]

    else:
        core_remaining_words = kanji_word_list
        
    # ------------------------------------------------------- search user table
    if PREFS["user"] == "1":
        echo("searching user list...")
        sieve_output = ""
        sieve_remaining_words = []
        # search for kanji & kana
        for target in core_remaining_words:
            definition = cursor.execute(
                """SELECT user.kanji, user.kana, user.pos, user.eng, user.jp
                   FROM user WHERE user.kanji = ? """,
                (target,),).fetchone()
            if definition is not None:
                sieve_output += ("[" + str(definition[0]) + "]"
                                 + "(" + url_scheme + str(definition[0])
                                 + url_scheme_postfix + ") :"
                                 + "【" + str(definition[1]) + "】"
                                 + " (" + str(definition[2]) + ") "
                                 + str(definition[3]) + ", "
                                 + str(definition[4]) + "  \n")
                flashcards += (str(definition[0]) + "\t" + str(definition[1])
                               + "\t" + str(definition[3]) + "\n")
            else:
                sieve_remaining_words += [target]

    else:
        sieve_remaining_words = core_remaining_words

    # ----------------------------------------------------------- search jmdict
    if PREFS["jmdict"] == "1":
        echo("searching jmdict for kanji...")
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
                                  + "【" + str(definition[1]) + "】"
                                  + " (" + str(definition[2]) + ") "
                                  + str(definition[3]) + "  \n")
                flashcards += (str(definition[0]) + "\t" + str(definition[1])
                               + "\t" + str(definition[3]) + "\n")
            else:
                jm_remaining_words += [target]
    
        # ----------------------------------------- search jmdict for kana only
        echo("searching jmdict for kana...")
        
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
                                  + "【" + str(definition[1]) + "】"
                                  + " (" + str(definition[2]) + ") "
                                  + str(definition[3]) + "  \n")
                flashcards += (str(definition[0]) + "\t" + str(definition[1])
                               + "\t" + str(definition[3]) + "\n")
            else:
                jm_remaining_kana += [target]
        
    else:
        jm_remaining_kana = []
        jm_remaining_kanji = sieve_remaining_words
    
    connection.commit()
    connection.close()    

    remaining_words = jm_remaining_kana + jm_remaining_kanji
    
    orphan = ""
    for word in remaining_words: 
        orphan = (orphan + "[" + word + "]"
                  + "(" + url_scheme + word + ") :  \n")
    echo("formatting ... \n\n")

    # ----------------------------------------------------------- prettify text
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

    # ------------------------------------------------------- output to console
    echo(text)
    echo("\ncharacters in text: " + str(len(text)))
    echo(_LINE_)
    echo("kanji in text: " + str(len(text2)))
    echo("discrete kanji in text: " + str(len(kanji_count)) + "\n")
    echo(kanji_countp)
    echo(_LINE_)
    if PREFS["kyouiku"] == "1":
        echo("    1年: " + str(len(tk1)))
        echo(tk1p)
        echo(_LINE_)
        echo("    2年: " + str(len(tk2)))
        echo(tk2p)
        echo(_LINE_)
        echo("    3年: " + str(len(tk3)))
        echo(tk3p)
        echo(_LINE_)
        echo("    4年: " + str(len(tk4)))
        echo(tk4p)
        echo(_LINE_)
        echo("    5年: " + str(len(tk5)))
        echo(tk5p)
        echo(_LINE_)
        echo("    6年: " + str(len(tk6)))
        echo(tk6p)
        echo(_LINE_)
        echo("   中学+: " + str(len(tk0)))
        echo(tk0p)
        echo(_LINE_)
    echo("words or word fragments searched in text: " 
          + str(len(kanji_word_list)) + "\n")
    echo(kanji_word_listp + "\n")
    echo("omitted from search: " + str(len(omitted_words)) + "\n")
    echo(omitted_wordsp)
    echo(_LINE_)
    if PREFS["core"] == "1":
        echo("core 6k list:  \n")
        echo(core_output)
        echo("remaining: " + str(len(core_remaining_words)) + "\n")
        echo(core_remaining_wordsp)
        echo(_LINE_)
    if PREFS["user"] == "1":
        echo("user list:  \n")
        echo(sieve_output)
        echo("remaining: " + str(len(sieve_remaining_words)) + "\n")
        echo(sieve_remaining_wordsp)
        echo(_LINE_)
    if PREFS["jmdict"] == "1":
        echo("jmdict:  \n")
        echo(jmdict_output)
        echo("remaining: " + str(len(remaining_words)) + "\n")
        echo(remaining_wordsp)
        echo(_LINE_)
    if PREFS["orphan"] == "1":
        echo(orphan)
    echo("\n\nSaving to file ... \n\n")

    # --------------------------------------------------------- text for output
    sieved_text = (f'''
{text} \n
__characters in text:__ {len(text)}
{_LINE_}
__kanji in text:__ {len(text2)}  \n
__discrete kanji in text:__ {len(kanji_count)} \n
{kanji_countp}
{_LINE_}''')
    if PREFS["kyouiku"] == "1":
        sieved_text += (f'''
1.  __第一学年:__ {len(tk1)}  \n
  {tk1p}  \n
2.  __第二学年:__ {len(tk2)}  \n
  {tk2p}  \n
3.  __第三学年:__ {len(tk3)}  \n
  {tk3p}  \n
4.  __第四学年:__ {len(tk4)}  \n
  {tk4p}  \n
5.  __第五学年:__ {len(tk5)}  \n
  {tk5p}  \n
6.  __第六学年:__ {len(tk6)}  \n
  {tk6p}  \n
7.  __中学以上:__ {len(tk0)}  \n
  {tk0p}  \n
{_LINE_}''')
    sieved_text += (f'''
__words or word fragments searched in text:__ {len(kanji_word_list)} \n
{kanji_word_listp} \n
__omitted from search:__ {len(omitted_words)} \n
{omitted_wordsp} \n
{_LINE_}
## Glossary  \n
''')
    if PREFS["core"] == "1":
        sieved_text += (f'''
### Core 6k list  \n
{core_output} \n
__remaining words:__ {len(core_remaining_words)}  \n
{core_remaining_wordsp}
{_LINE_}''')
    if PREFS["user"] == "1":
        sieved_text += (f'''
### user list  \n
{sieve_output} \n
__remaining words:__ {len(sieve_remaining_words)}  \n
{sieve_remaining_wordsp}
{_LINE_}''')
    if PREFS["jmdict"] == "1":
        sieved_text += (f'''
### jmdict list  \n
{jmdict_output} \n
__remaining words:__  {len(remaining_words)}  \n
{remaining_wordsp}  \n
{_LINE_}''')
    if PREFS["orphan"] == "1":
        sieved_text += (f'''
{orphan}  \n
''')
    sieved_text += (f'''
_generated with [Kanji Sieve {VERSION}](https://github.com/takarabune/kanji_sieve)_
    ''')
    
    # ---------------------------------------------- output to html for display
    md_text = ("# " + Path(filepath).stem
               + "\n\n" + sieved_text)
               
    html_convert_display(md_text)
    v['webview1'].delegate = HTMLviewer()
    
    # ------------------------------------------------------------- save output
    newdir = "kanji sieve output/"
    newfile = Path(newdir)
    if not newfile.is_dir():
        os.mkdir(newdir)
    newname = Path(filepath).stem + "_" + choice + "_笊.md"
    newpath = "kanji sieve output/" + newname
    newfile = Path(newdir + newname)
    newpath = add_unique_postfix(newfile)
    newtext = ("# " + Path(filepath).stem
               + "  \n_" + time.ctime()
               + "_  \n\n" + sieved_text)
    newfile = open(newpath, "w", encoding="utf-8")
    newfile.write(newtext)
    newfile.close()

    # --------------------------------------------------------- save flashcards
    if PREFS["tsv_out"] == "1":
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

    # append to orphans log file
    newfile = open("kanji sieve output/orphans_log.md", "a", encoding="utf-8")
    newfile.write("\n\n" + Path(filepath).stem + "  \n"
                 + time.ctime() + "  \n" + orphan)
    newfile.close()

    # ------------------------------------------------------------- orphans csv
    if PREFS["orphan_out"] == "1":
        if len(remaining_words) > 0:
            newfile = open("kanji sieve output/" + Path(filepath).stem
                         + "_orphans.csv", "w", encoding="utf-8")
            newfile.write("\n".join(map(str, remaining_words)))
            newfile.close()
            
    # ------------------------------------------------------------ last orphans
    newfile = open("data/orphans.ksv", "w", encoding="utf-8")
    newfile.write("\n".join(map(str, remaining_words)))
    newfile.close()

    spinner.stop()
    
    echo("saved \n")
    dialogs.hud_alert("saved")
    
# --------------------------------------------------------------------- main #
# ------------------------------------------------------------------ build GUI
v = ui.load_view_str(ks_pyui.decode('utf-8'))

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

spinner = ui.ActivityIndicator()
spinner.style = ui.ACTIVITY_INDICATOR_STYLE_WHITE_LARGE
spinner.hides_when_stopped = True
spinner.x = (v.width / 2.0) - 75
spinner.y = (v.height / 2.0) - 140
spinner.flex = "LRTB"
spinner.background_color = "#000000"
spinner.alpha = 0.8
spinner.height = 150
spinner.width = 150
spinner.corner_radius = 10
v.add_subview(spinner)

v.update_interval = 1

PREFS = load_prefs("data/kanji_sieve.pref")
dict_pref = PREFS["dict"]

v.present('fullscreen', hide_close_button=True)


# -----------------------------------------------------------  initialise prefs
init_dict_pref(dict_pref)
for pref, value in PREFS.items():
    init_bool_pref(pref, value)
v.wait_modal()

# -------------------------------------------------------  on close write prefs
write_prefs(PREFS, "data/kanji_sieve.pref")
print("kanji sieve closed")
print("prefs:`" + str(PREFS) + "`")




