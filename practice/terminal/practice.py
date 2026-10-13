#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
猫师自然码并击 交互式终端练习系统
- 真实物理阶梯全键盘布局 (标准 QWERTY 阶梯错位排列，高亮当前应按键)
- 并击时序判定时间窗扩充至 180ms，完美捕捉双手物理并击
- 真实打字上屏效果：击中后在【屏幕输出】实时累加输出字词/码元，呈现真实打字结果
- 100% 真正无限随机出题循环，显示当前及后续 5 个目标；Tab 开关提示、ESC 退出
"""
import sys
import os
import tty
import termios
import select
import random
import time
import json
from pathlib import Path

# ------------------ 键位与并击码表 ------------------
LOWER_CHORDS = {
    'a': {'left': 'a',       'right': ';',       'desc': '单键 a / ;',       'keys': [{'a'}, {';'}]},
    'b': {'left': 'b',       'right': 'n',       'desc': '单键 b / n',       'keys': [{'b'}, {'n'}]},
    'c': {'left': 'c',       'right': ',',       'desc': '单键 c / ,',       'keys': [{'c'}, {','}]},
    'd': {'left': 'd',       'right': 'k',       'desc': '单键 d / k',       'keys': [{'d'}, {'k'}]},
    'e': {'left': 'e',       'right': 'i',       'desc': '单键 e / i',       'keys': [{'e'}, {'i'}]},
    'f': {'left': 'f',       'right': 'j',       'desc': '单键 f / j',       'keys': [{'f'}, {'j'}]},
    'g': {'left': 'g',       'right': 'h',       'desc': '单键 g / h',       'keys': [{'g'}, {'h'}]},
    'h': {'left': 'w + f',   'right': 'o + j',   'desc': '并击 w+f / o+j',   'keys': [{'w', 'f'}, {'o', 'j'}]},
    'i': {'left': 'w + e',   'right': 'o + i',   'desc': '并击 w+e / o+i',   'keys': [{'w', 'e'}, {'o', 'i'}]},
    'j': {'left': 'd + f',   'right': 'k + j',   'desc': '并击 d+f / k+j',   'keys': [{'d', 'f'}, {'k', 'j'}]},
    'k': {'left': 's + d',   'right': 'l + k',   'desc': '并击 s+d / l+k',   'keys': [{'s', 'd'}, {'l', 'k'}]},
    'l': {'left': 's + f',   'right': 'l + j',   'desc': '并击 s+f / l+j',   'keys': [{'s', 'f'}, {'l', 'j'}]},
    'm': {'left': 'c + v',   'right': ', + m',   'desc': '并击 c+v / ,+m',   'keys': [{'c', 'v'}, {',', 'm'}]},
    'n': {'left': 's + c',   'right': 'l + m',   'desc': '并击 s+c / l+m',   'keys': [{'s', 'c'}, {'l', 'm'}]},
    'o': {'left': 'w + r',   'right': 'o + u',   'desc': '并击 w+r / o+u',   'keys': [{'w', 'r'}, {'o', 'u'}]},
    'p': {'left': 'q + r',   'right': 'p + u',   'desc': '并击 q+r / p+u',   'keys': [{'q', 'r'}, {'p', 'u'}]},
    'q': {'left': 'q',       'right': 'p',       'desc': '单键 q / p',       'keys': [{'q'}, {'p'}]},
    'r': {'left': 'r',       'right': 'u',       'desc': '单键 r / u',       'keys': [{'r'}, {'u'}]},
    's': {'left': 's',       'right': 'l',       'desc': '单键 s / l',       'keys': [{'s'}, {'l'}]},
    't': {'left': 't',       'right': 'y',       'desc': '单键 t / y',       'keys': [{'t'}, {'y'}]},
    'u': {'left': 'e + r',   'right': 'i + u',   'desc': '并击 e+r / i+u',   'keys': [{'e', 'r'}, {'i', 'u'}]},
    'v': {'left': 'v',       'right': 'm',       'desc': '单键 v / m',       'keys': [{'v'}, {'m'}]},
    'w': {'left': 'w',       'right': 'o',       'desc': '单键 w / o',       'keys': [{'w'}, {'o'}]},
    'x': {'left': 'x',       'right': '.',       'desc': '单键 x / .',       'keys': [{'x'}, {'.'}]},
    'y': {'left': 'e + f',   'right': 'i + j',   'desc': '并击 e+f / i+j',   'keys': [{'e', 'f'}, {'i', 'j'}]},
    'z': {'left': 'z',       'right': '/',       'desc': '单键 z / /',       'keys': [{'z'}, {'/'}]},
}

UPPER_CHORDS = {
    'A': {'left': 'a + v', 'right': '; + n', 'desc': '大写标调/形码', 'keys': [{'a', 'v'}, {';', 'n'}]},
    'B': {'left': 'q + w', 'right': 'p + o', 'desc': '大写标调/形码', 'keys': [{'q', 'w'}, {'p', 'o'}]},
    'C': {'left': 'x + b', 'right': '. + n', 'desc': '大写标调/形码', 'keys': [{'x', 'b'}, {'.', 'n'}]},
    'D': {'left': 'd + v', 'right': 'k + n', 'desc': '大写标调/形码', 'keys': [{'d', 'v'}, {'k', 'n'}]},
    'E': {'left': 'e + v', 'right': 'i + n', 'desc': '大写标调/形码', 'keys': [{'e', 'v'}, {'i', 'n'}]},
    'F': {'left': 's + g', 'right': 'l + h', 'desc': '大写标调/形码', 'keys': [{'s', 'g'}, {'l', 'h'}]},
    'G': {'left': 'd + g', 'right': 'k + h', 'desc': '大写标调/形码', 'keys': [{'d', 'g'}, {'k', 'h'}]},
    'H': {'left': 'a + r', 'right': '; + u', 'desc': '大写标调/形码', 'keys': [{'a', 'r'}, {';', 'u'}]},
    'I': {'left': 'x + v', 'right': '. + m', 'desc': '大写标调/形码', 'keys': [{'x', 'v'}, {'.', 'm'}]},
    'J': {'left': 'x + f', 'right': '. + j', 'desc': '大写标调/形码', 'keys': [{'x', 'f'}, {'.', 'j'}]},
    'K': {'left': 'x + c', 'right': '. + ,', 'desc': '大写标调/形码', 'keys': [{'x', 'c'}, {'.', ','}]},
    'L': {'left': 's + r', 'right': 'l + u', 'desc': '大写标调/形码', 'keys': [{'s', 'r'}, {'l', 'u'}]},
    'M': {'left': 'w + d', 'right': 'o + k', 'desc': '大写标调/形码', 'keys': [{'w', 'd'}, {'o', 'k'}]},
    'N': {'left': 's + e', 'right': 'l + i', 'desc': '大写标调/形码', 'keys': [{'s', 'e'}, {'l', 'i'}]},
    'O': {'left': 'a + w', 'right': '; + o', 'desc': '大写标调/形码', 'keys': [{'a', 'w'}, {';', 'o'}]},
    'P': {'left': 'q + f', 'right': 'p + j', 'desc': '大写标调/形码', 'keys': [{'q', 'f'}, {'p', 'j'}]},
    'Q': {'left': 'z + v', 'right': '/ + m', 'desc': '大写标调/形码', 'keys': [{'z', 'v'}, {'/', 'm'}]},
    'R': {'left': 'e + t', 'right': 'i + y', 'desc': '大写标调/形码', 'keys': [{'e', 't'}, {'i', 'y'}]},
    'S': {'left': 's + v', 'right': 'l + n', 'desc': '大写标调/形码', 'keys': [{'s', 'v'}, {'l', 'n'}]},
    'T': {'left': 'q + t', 'right': 'p + y', 'desc': '大写标调/形码', 'keys': [{'q', 't'}, {'p', 'y'}]},
    'U': {'left': 'a + f', 'right': '; + j', 'desc': '大写标调/形码', 'keys': [{'a', 'f'}, {';', 'j'}]},
    'V': {'left': 'z + s', 'right': '/ + l', 'desc': '大写标调/形码', 'keys': [{'z', 's'}, {'/', 'l'}]},
    'W': {'left': 'w + v', 'right': 'o + n', 'desc': '大写标调/形码', 'keys': [{'w', 'v'}, {'o', 'n'}]},
    'X': {'left': 'x + d', 'right': '. + k', 'desc': '大写标调/形码', 'keys': [{'x', 'd'}, {'.', 'k'}]},
    'Y': {'left': 'w + t', 'right': 'o + y', 'desc': '大写标调/形码', 'keys': [{'w', 't'}, {'o', 'y'}]},
    'Z': {'left': 'z + f', 'right': '/ + j', 'desc': '大写标调/形码', 'keys': [{'z', 'f'}, {'/', 'j'}]},
}

SYMBOL_CHORDS = {
    ',': {'left': 's + d + f', 'right': 'l + k + j', 'desc': '逗号', 'keys': [{'s', 'd', 'f'}, {'l', 'k', 'j'}]},
    '.': {'left': 'a + g',     'right': '; + h',     'desc': '句号', 'keys': [{'a', 'g'}, {';', 'h'}]},
    '!': {'left': 'w + e + f', 'right': 'o + i + j', 'desc': '感叹号', 'keys': [{'w', 'e', 'f'}, {'o', 'i', 'j'}]},
    '?': {'left': 's + e + f', 'right': 'l + i + j', 'desc': '问号', 'keys': [{'s', 'e', 'f'}, {'l', 'i', 'j'}]},
    ':': {'left': 'a + s',     'right': '; + l',     'desc': '冒号', 'keys': [{'a', 's'}, {';', 'l'}]},
    ';': {'left': 'a + d',     'right': '; + k',     'desc': '分号', 'keys': [{'a', 'd'}, {';', 'k'}]},
    '1': {'left': '1',         'right': '0',         'desc': '数字 1', 'keys': [{'1'}, {'0'}]},
    '2': {'left': '2',         'right': '9',         'desc': '数字 2', 'keys': [{'2'}, {'9'}]},
    '3': {'left': '3',         'right': '8',         'desc': '数字 3', 'keys': [{'3'}, {'8'}]},
    '4': {'left': '4',         'right': '7',         'desc': '数字 4', 'keys': [{'4'}, {'7'}]},
    '5': {'left': '5',         'right': '6',         'desc': '数字 5', 'keys': [{'5'}, {'6'}]},
    '6': {'left': '3 + 5',     'right': '8 + 6',     'desc': '数字 6', 'keys': [{'3', '5'}, {'8', '6'}]},
    '7': {'left': '3 + 4',     'right': '8 + 7',     'desc': '数字 7', 'keys': [{'3', '4'}, {'8', '7'}]},
    '8': {'left': '2 + 3',     'right': '9 + 8',     'desc': '数字 8', 'keys': [{'2', '3'}, {'9', '8'}]},
    '9': {'left': '2 + 4',     'right': '9 + 7',     'desc': '数字 9', 'keys': [{'2', '4'}, {'9', '7'}]},
    '0': {'left': '1 + 4',     'right': '0 + 7',     'desc': '数字 0', 'keys': [{'1', '4'}, {'0', '7'}]},
}

CHORD_MAP = {}
for ch, info in LOWER_CHORDS.items():
    for kset in info['keys']:
        CHORD_MAP[frozenset(kset)] = ch
for ch, info in UPPER_CHORDS.items():
    for kset in info['keys']:
        CHORD_MAP[frozenset(kset)] = ch
for ch, info in SYMBOL_CHORDS.items():
    for kset in info['keys']:
        CHORD_MAP[frozenset(kset)] = ch

CHAR_DB = [
    ('的', 'de;HDDDDA', 'de', '轻声/一声', 'de'),
    ('一', 'yi;FIIIAA', 'yi', '一声', 'yi'),
    ('是', 'uI;RJLLSS', 'uI', '四声', 'shi'),
    ('在', 'zA;VLDDSS', 'zA', '四声', 'zai'),
    ('不', 'bU;DXXFRR', 'bU', '四声', 'bu'),
    ('了', 'le;NEEEAA', 'le', '轻声/一声', 'le'),
    ('有', 'yB;DEEEAA', 'yB', '三声', 'you'),
    ('和', 'hE;TXDDSS', 'hE', '二声', 'he'),
    ('人', 'rF;JRRRRR', 'rF', '二声', 'ren'),
    ('这', 've;WLDDSS', 've', '四声', 'zhe'),
    ('中', 'vS;QLLLLR', 'vS', '一声', 'zhong'),
    ('大', 'Da;MDDDDR', 'Da', '四声', 'da'),
    ('为', 'wE;JNNNDD', 'wE', '二/四声', 'wei'),
    ('上', 'Uh;YFIIHA', 'Uh', '四声', 'shang'),
    ('个', 'gE;JLLLDD', 'gE', '四声', 'ge'),
    ('国', 'gO;VEEERR', 'gO', '二声', 'guo'),
    ('我', 'wO;TDEERR', 'wO', '三声', 'wo'),
    ('以', 'yI;VNNNLL', 'yI', '三声', 'yi'),
    ('要', 'yC;SEEEAA', 'yC', '四声', 'yao'),
    ('他', 'tA;JLDDSS', 'tA', '一声', 'ta'),
    ('时', 'uI;RDSSAA', 'uI', '二声', 'shi'),
    ('来', 'lF;TDDDAA', 'lF', '二声', 'lai'),
    ('用', 'yS;QNEEAA', 'yS', '四声', 'yong'),
    ('们', 'mF;JNEERR', 'mF', '轻声', 'men'),
    ('生', 'uG;TIIIAA', 'uG', '一声', 'sheng'),
    ('到', 'dC;UXXRRR', 'dC', '四声', 'dao'),
    ('作', 'zO;JTEESS', 'zO', '四声', 'zuo'),
    ('地', 'dI;FNEEAA', 'dI', '四声', 'di'),
    ('出', 'vU;VBBBSS', 'vU', '一声', 'chu'),
    ('就', 'jU;YVFFDD', 'jU', '四声', 'jiu')
]

# 自然码双拼音码：左手输入声母，右手输入韵母。
INITIAL_LABELS = {
    'a': '零声母（a 开头）', 'b': 'b', 'c': 'c', 'd': 'd',
    'e': '零声母（e 开头）', 'f': 'f', 'g': 'g', 'h': 'h',
    'i': 'ch', 'j': 'j', 'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n',
    'o': '零声母（o 开头）', 'p': 'p', 'q': 'q', 'r': 'r',
    's': 's', 't': 't', 'u': 'sh', 'v': 'zh', 'w': 'w', 'x': 'x',
    'y': 'y', 'z': 'z',
}

FINAL_LABELS = {
    'a': 'a', 'b': 'ou', 'c': 'iao', 'd': 'iang / uang',
    'e': 'e', 'f': 'en', 'g': 'eng', 'h': 'ang', 'i': 'i',
    'j': 'an', 'k': 'ao', 'l': 'ai', 'm': 'ian', 'n': 'in',
    'o': 'o / uo', 'p': 'un', 'q': 'iu', 'r': 'er / uan',
    's': 'ong / iong', 't': 'ue', 'u': 'u', 'v': 'ui / ü',
    'w': 'ia / ua', 'x': 'ie', 'y': 'ing / uai', 'z': 'ei',
}

# 大写码元按官方 keyMap 的字母区段拆分，避免一次混练全部 A-Z。
UPPER_ZONES = [
    ('1', 'A-G 区', 'abcdefg'),
    ('2', 'H-N 区', 'hijklmn'),
    ('3', 'O-T 区', 'opqrst'),
    ('4', 'U-Z 区', 'uvwxyz'),
    ('5', 'A-Z 综合区', 'abcdefghijklmnopqrstuvwxyz'),
]

TONE_DIFFICULTY_NAMES = {
    2: '入门（2 个物理键）',
    3: '进阶（3 个物理键）',
    4: '挑战（4 个物理键）',
}

TONE_DATA_PATH = Path(__file__).with_name('data_chars.json')
try:
    TONE_SYLLABLES = json.loads(TONE_DATA_PATH.read_text(encoding='utf-8'))
except (OSError, json.JSONDecodeError):
    TONE_SYLLABLES = []

def move_cursor(r, c):
    sys.stdout.write(f'\033[{r};{c}H')

def clear_screen():
    sys.stdout.write('\033[2J\033[H')
    sys.stdout.flush()

def get_chord_info(ch):
    if ch in LOWER_CHORDS:
        return LOWER_CHORDS[ch]
    if ch in UPPER_CHORDS:
        return UPPER_CHORDS[ch]
    if ch in SYMBOL_CHORDS:
        return SYMBOL_CHORDS[ch]
    return {'left': ch, 'right': ch, 'desc': '直接击键', 'keys': [{ch}]}

# ------------------ 并击检测：窗口扩至 180ms ------------------
def read_chord_burst(timeout_ms=180):
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    chars = []
    try:
        tty.setraw(fd)
        first_char = sys.stdin.read(1)
        chars.append(first_char)
        if first_char in ('\x1b', '\t'):
            return {first_char}, first_char
        end_time = time.time() + (timeout_ms / 1000.0)
        while True:
            rem = end_time - time.time()
            if rem <= 0:
                break
            r, _, _ = select.select([sys.stdin], [], [], rem)
            if r:
                nxt = sys.stdin.read(1)
                chars.append(nxt)
            else:
                break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    raw_set = set(chars)
    frozen = frozenset(raw_set)
    if frozen in CHORD_MAP:
        return raw_set, CHORD_MAP[frozen]
    return raw_set, chars[0]

def getch_simple():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch

# ------------------ 阶梯式真实全键盘渲染 ------------------
def format_key(k_char, display_lbl, active_set):
    is_active = k_char.lower() in active_set
    if is_active:
        return f'\033[1;30;42m[{display_lbl}]\033[0m'
    return f'[{display_lbl}]'

def render_physical_keyboard(active_keys):
    row1_spec = [('`', '`'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
                 ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('0', '0'), ('-', '-'), ('=', '=')]
    row2_spec = [('q', 'Q'), ('w', 'W'), ('e', 'E'), ('r', 'R'), ('t', 'T'),
                 ('y', 'Y'), ('u', 'U'), ('i', 'I'), ('o', 'O'), ('p', 'P'), ('[', '['), (']', ']')]
    row3_spec = [('a', 'A'), ('s', 'S'), ('d', 'D'), ('f', 'F'), ('g', 'G'),
                 ('h', 'H'), ('j', 'J'), ('k', 'K'), ('l', 'L'), (';', ';'), ("'", "'")]
    row4_spec = [('z', 'Z'), ('x', 'X'), ('c', 'C'), ('v', 'V'), ('b', 'B'),
                 ('n', 'N'), ('m', 'M'), (',', ','), ('.', '.'), ('/', '/')]

    line1 = '  ' + ' '.join(format_key(k, l, active_keys) for k, l in row1_spec)
    line2 = '   ' + ' '.join(format_key(k, l, active_keys) for k, l in row2_spec)
    line3 = '    ' + ' '.join(format_key(k, l, active_keys) for k, l in row3_spec)
    line4 = '     ' + ' '.join(format_key(k, l, active_keys) for k, l in row4_spec)
    return [line1, line2, line3, line4]

def draw_layout(target_char, effect_text, extra_hint, feedback_msg, level_title, stage_desc, idx, correct_count, screen_buffer, hints_enabled, upcoming_items, chord):
    active_keys = set()
    if hints_enabled:
        for kset in chord.get('keys', []):
            for k in kset:
                active_keys.add(k.lower())

    clear_screen()
    move_cursor(1, 2)
    sys.stdout.write(f'\033[1;36m=== 猫师并击练习系统 · {level_title} ===\033[0m')
    move_cursor(2, 2)
    hint_state = '\033[1;32m开启\033[0;2m' if hints_enabled else '\033[1;31m关闭\033[0;2m'
    sys.stdout.write(f'\033[2m进度: \033[1;35m【无限练习模式】\033[0;2m   已练题数: {idx}   命中: {correct_count}   提示: {hint_state} [Tab切换]   退出: [ESC]\033[0m')
    move_cursor(3, 2)

    # 关闭提示时，双拼题只显示带声调读音，不显示双拼码或物理键位。
    def format_item_preview(item):
        token = item.get('char_token')
        target = item.get('target_char')
        prompt = item.get('prompt_token')
        if not hints_enabled and token and token != target:
            return prompt or token
        return target

    preview_labels = [format_item_preview(item) for item in upcoming_items]
    current_preview = f'\033[1;33m[{preview_labels[0]}\033[0m\033[1;33m]\033[0m'
    future_preview = '  →  '.join(preview_labels[1:])
    sys.stdout.write(f'【练习序列】: {current_preview}  →  \033[2m{future_preview}\033[0m')

    # 上屏显示区域
    disp_buffer = screen_buffer[-48:] if len(screen_buffer) > 48 else screen_buffer
    move_cursor(4, 2)
    sys.stdout.write('┌───────────────────────────── 实际屏幕打字与上屏效果 ─────────────────────────────┐')
    move_cursor(5, 2)
    sys.stdout.write(f'│  【屏幕输出】: \033[1;32m{disp_buffer}\033[0m\033[5m_\033[0m')
    move_cursor(5, 84)
    sys.stdout.write('│')
    move_cursor(6, 2)

    current_target_display = preview_labels[0]
    shown_extra = extra_hint if hints_enabled else '提示已关闭'
    sys.stdout.write(f'│  【当前目标】: \033[1;33m{current_target_display}\033[0m  ({shown_extra})')
    move_cursor(6, 84)
    sys.stdout.write('│')
    move_cursor(7, 2)
    # 当关闭提示且为双拼汉字时，目标效果不泄露双拼按键或难度键数
    curr_item = upcoming_items[0]
    token = curr_item.get('char_token')
    target = curr_item.get('target_char')
    is_shuangpin_char = token and token != target
    if not hints_enabled and is_shuangpin_char:
        prompt = curr_item.get('prompt_token') or token
        shown_effect = f'读音练习：{prompt}（示例字：{token}）'
    else:
        shown_effect = effect_text
    sys.stdout.write(f'│  【目标效果】: \033[1;35m{shown_effect}\033[0m')
    move_cursor(7, 84)
    sys.stdout.write('│')
    move_cursor(8, 2)
    sys.stdout.write(f'│  【即时判定】: {feedback_msg}')
    move_cursor(8, 84)
    sys.stdout.write('│')
    move_cursor(9, 2)
    sys.stdout.write('└──────────────────────────────────────────────────────────────────────────────────┘')

    # 真实错位阶梯键盘；关闭提示时保留参考图，但不高亮答案。
    move_cursor(10, 2)
    sys.stdout.write('┌──────────────────────── 猫师并击 · 物理阶梯标准全键盘图 ─────────────────────────┐')
    kb_lines = render_physical_keyboard(active_keys)
    for i, line in enumerate(kb_lines):
        move_cursor(11 + i, 2)
        sys.stdout.write(f'│ {line}')
        move_cursor(11 + i, 84)
        sys.stdout.write('│')
    move_cursor(15, 2)
    sys.stdout.write('├──────────────────────────────────────────────────────────────────────────────────┤')
    move_cursor(16, 2)
    if hints_enabled:
        sys.stdout.write(f'│  左手并击: \033[1;32m[ {chord["left"]} ]\033[0m   |   右手对称: \033[1;32m[ {chord["right"]} ]\033[0m   ({chord["desc"]})')
    else:
        sys.stdout.write('│  \033[2m并击键位提示已隐藏；按 [Tab] 可随时重新开启。\033[0m')
    move_cursor(16, 84)
    sys.stdout.write('│')
    move_cursor(17, 2)
    sys.stdout.write('└──────────────────────────────────────────────────────────────────────────────────┘')

    move_cursor(19, 2)
    if hints_enabled:
        sys.stdout.write('\033[2m【提示已开启】绿色高亮为目标按键；按 [Tab] 关闭提示。\033[0m')
    else:
        sys.stdout.write('\033[2m【提示已关闭】不显示目标键位和并击组合；按 [Tab] 开启提示。\033[0m')
    move_cursor(20, 2)
    sys.stdout.write('请直接敲击/并击键位 -> ')
    sys.stdout.flush()

def make_initial_item(code, uppercase=False):
    display_code = code.upper() if uppercase else code
    info = get_chord_info(display_code)
    left_keys = set(info['keys'][0])
    case_name = '纯大写' if uppercase else '纯小写'
    return {
        'target_char': display_code,
        'char_token': display_code,
        'effect': f"左手{case_name}声母 {display_code} → {INITIAL_LABELS[code]}",
        'extra': f'只使用左手完成；26 个{case_name}声母码元循环覆盖',
        'valid_key_sets': [left_keys],
        'strict_keys': True,
        'chord_info': {
            'left': info['left'], 'right': '—',
            'desc': f"左手{case_name}声母 {INITIAL_LABELS[code]}", 'keys': [left_keys],
        },
    }

def make_final_item(code, uppercase=False):
    display_code = code.upper() if uppercase else code
    info = get_chord_info(display_code)
    right_keys = set(info['keys'][1])
    case_name = '纯大写' if uppercase else '纯小写'
    return {
        'target_char': display_code,
        'char_token': display_code,
        'effect': f"右手{case_name}韵母 {display_code} → {FINAL_LABELS[code]}",
        'extra': f'只使用右手完成；26 个{case_name}韵母码元循环覆盖',
        'valid_key_sets': [right_keys],
        'strict_keys': True,
        'chord_info': {
            'left': '—', 'right': info['right'],
            'desc': f"右手{case_name}韵母 {FINAL_LABELS[code]}", 'keys': [right_keys],
        },
    }

def make_tone_item(entry, toneless=False):
    raw_code = entry['code']
    code = raw_code.lower() if toneless else raw_code
    left_code, right_code = code[0], code[1]
    left_info = get_chord_info(left_code)
    right_info = get_chord_info(right_code)
    left_keys = set(left_info['keys'][0])
    right_keys = set(right_info['keys'][1])
    combined_keys = left_keys | right_keys
    key_count = len(combined_keys)
    difficulty = TONE_DIFFICULTY_NAMES[key_count]
    tone_desc = '无声调' if toneless else entry['tone_group']
    extra_desc = f'左手纯小写声母 + 右手纯小写韵母；无声调；难度按 {key_count} 个物理键划分' if toneless else f'左手声母 + 右手韵母同时并击；大小写表示声调；难度按 {key_count} 个物理键划分'
    return {
        'target_char': code,
        'char_token': entry['char'],
        'prompt_token': entry['pinyin'],
        'effect': f"{entry['char']} · {entry['pinyin']} · {tone_desc} · {difficulty}",
        'extra': extra_desc,
        'difficulty_key_count': key_count,
        'valid_key_sets': [combined_keys],
        'strict_keys': True,
        'chord_info': {
            'left': left_info['left'], 'right': right_info['right'],
            'desc': f"音码 {code}（{tone_desc}）", 'keys': [combined_keys],
        },
    }

def make_toneless_group_item(entries):
    """同一无声调双拼码只出一道读音题，避免把同音不同调误当成唯一汉字。"""
    code = entries[0]['code'].lower()
    left_code, right_code = code[0], code[1]
    left_info = get_chord_info(left_code)
    right_info = get_chord_info(right_code)
    combined_keys = set(left_info['keys'][0]) | set(right_info['keys'][1])
    key_count = len(combined_keys)
    difficulty = TONE_DIFFICULTY_NAMES[key_count]

    tone_marks = {
        1: 'āēīōūǖ',
        2: 'áéíóúǘ',
        3: 'ǎěǐǒǔǚ',
        4: 'àèìòùǜ',
    }
    def tone_rank(entry):
        pinyin = entry['pinyin']
        for rank, marks in tone_marks.items():
            if any(mark in pinyin for mark in marks):
                return rank
        return 5

    readings = []
    chars = []
    reading_examples = []
    for entry in sorted(entries, key=tone_rank):
        if entry['pinyin'] not in readings:
            readings.append(entry['pinyin'])
        if entry['char'] not in chars:
            chars.append(entry['char'])
        example = f"{entry['pinyin']}（{entry['char']}）"
        if example not in reading_examples:
            reading_examples.append(example)

    reading_prompt = ' / '.join(readings)
    char_group = '/'.join(chars)
    return {
        'target_char': code,
        'char_token': char_group,
        'prompt_token': reading_prompt,
        'effect': f"读音：{' / '.join(reading_examples)} · 共用无声调音码 · {difficulty}",
        'extra': f'根据读音输入纯小写双拼；同音节不同声调共用 {code}',
        'difficulty_key_count': key_count,
        'valid_key_sets': [combined_keys],
        'strict_keys': True,
        'chord_info': {
            'left': left_info['left'], 'right': right_info['right'],
            'desc': f"无声调音码 {code}", 'keys': [combined_keys],
        },
    }

def upper_zone_item_stream(side, codes):
    maker = make_initial_item if side == 'left' else make_final_item
    while True:
        shuffled_codes = list(codes)
        random.shuffle(shuffled_codes)
        for code in shuffled_codes:
            yield maker(code, uppercase=True)

def tone_difficulty_item_stream(key_count=None, toneless=False):
    if toneless:
        grouped = {}
        for entry in TONE_SYLLABLES:
            code = entry['code'].lower()
            if code == 'er':
                continue  # er 保留为“包裹当前候选并上屏”的功能码，不作为无声调音节题。
            grouped.setdefault(code, []).append(entry)
        items = [make_toneless_group_item(entries) for entries in grouped.values()]
        items = [item for item in items if key_count is None or item['difficulty_key_count'] == key_count]
        while True:
            shuffled_items = list(items)
            random.shuffle(shuffled_items)
            yield from shuffled_items
    else:
        entries = []
        for entry in TONE_SYLLABLES:
            item = make_tone_item(entry)
            if key_count is None or item['difficulty_key_count'] == key_count:
                entries.append(entry)
        while True:
            shuffled_entries = list(entries)
            random.shuffle(shuffled_entries)
            for entry in shuffled_entries:
                yield make_tone_item(entry)

def level_item_stream(level_id):
    if level_id in (3, 4):
        while True:
            codes = list(INITIAL_LABELS)
            random.shuffle(codes)
            for code in codes:
                yield make_initial_item(code, uppercase=(level_id == 4))
    elif level_id in (5, 6):
        while True:
            codes = list(FINAL_LABELS)
            random.shuffle(codes)
            for code in codes:
                yield make_final_item(code, uppercase=(level_id == 6))
    elif level_id == 7 and TONE_SYLLABLES:
        while True:
            entries = list(TONE_SYLLABLES)
            random.shuffle(entries)
            for entry in entries:
                yield make_tone_item(entry)
    else:
        while True:
            yield get_level_item(level_id)

def get_level_item(level_id):
    if level_id == 1:
        keys = [k for k in LOWER_CHORDS if '+' not in LOWER_CHORDS[k]['left']]
        k = random.choice(keys)
        return {'target_char': k, 'char_token': k, 'effect': f"基础码元 '{k}'", 'extra': '原位单键'}
    elif level_id == 2:
        combos = [k for k in LOWER_CHORDS if '+' in LOWER_CHORDS[k]['left']]
        k = random.choice(combos)
        return {'target_char': k, 'char_token': k, 'effect': f"复合并击码元 '{k}'", 'extra': '双手并击'}
    elif level_id == 3:
        return make_initial_item(random.choice(list(INITIAL_LABELS)))
    elif level_id == 4:
        return make_initial_item(random.choice(list(INITIAL_LABELS)), uppercase=True)
    elif level_id == 5:
        return make_final_item(random.choice(list(FINAL_LABELS)))
    elif level_id == 6:
        return make_final_item(random.choice(list(FINAL_LABELS)), uppercase=True)
    elif level_id == 7:
        if TONE_SYLLABLES:
            return make_tone_item(random.choice(TONE_SYLLABLES))
        ch, full, code2, tone, py = random.choice(CHAR_DB)
        return {'target_char': code2, 'char_token': ch, 'effect': f"汉字【{ch}】({py}, {tone})", 'extra': f"双拼音码: {code2}"}
    elif level_id == 8:
        symbols = [',', '.', '!', '?', ':', ';']
        s = random.choice(symbols)
        return {'target_char': s, 'char_token': s, 'effect': f"并击符号: {SYMBOL_CHORDS[s]['desc']}", 'extra': '高频符号'}
    elif level_id == 9:
        nums = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        n = random.choice(nums)
        return {'target_char': n, 'char_token': n, 'effect': f"并击数字 '{n}'", 'extra': '并击数字'}
    elif level_id == 10:
        shapes = ['H', 'D', 'F', 'I', 'R', 'J', 'L', 'S', 'V', 'T', 'X']
        sp = random.choice(shapes)
        return {'target_char': sp, 'char_token': sp, 'effect': f"字根码元 '{sp}' (虎码/二笔盲打)", 'extra': '形码字根'}
    else:
        pool_type = random.choice(['combo', 'tone', 'symbol', 'number', 'upper_initial', 'upper_final'])
        if pool_type == 'combo':
            combos = [k for k in LOWER_CHORDS if '+' in LOWER_CHORDS[k]['left']]
            k = random.choice(combos)
            return {'target_char': k, 'char_token': k, 'effect': f"复合并击 '{k}'", 'extra': '综合·复合码元'}
        if pool_type == 'tone' and TONE_SYLLABLES:
            return make_tone_item(random.choice(TONE_SYLLABLES))
        if pool_type == 'upper_initial':
            return make_initial_item(random.choice(list(INITIAL_LABELS)), uppercase=True)
        if pool_type == 'upper_final':
            return make_final_item(random.choice(list(FINAL_LABELS)), uppercase=True)
        if pool_type == 'number':
            n = random.choice(list('1234567890'))
            return {'target_char': n, 'char_token': n, 'effect': f"并击数字 '{n}'", 'extra': '综合·数字'}
        s = random.choice([',', '.', '!', '?', ':', ';'])
        return {'target_char': s, 'char_token': s, 'effect': f"并击符号: {SYMBOL_CHORDS[s]['desc']}", 'extra': '综合·符号'}

def run_exercise(level_title, stage_desc, level_id, item_source=None):
    idx = 0
    correct_count = 0
    screen_buffer = ""
    hints_enabled = True
    feedback = '\033[2m等待输入...\033[0m'
    preview_count = 5
    if item_source is None:
        item_source = level_item_stream(level_id)
    item_queue = [next(item_source) for _ in range(preview_count + 1)]

    while True:
        current_item = item_queue[0]
        upcoming_chars = [item['target_char'] for item in item_queue]
        target_char = current_item['target_char']
        effect_text = current_item['effect']
        extra_hint = current_item.get('extra', '')
        chord = current_item.get('chord_info') or get_chord_info(target_char)

        draw_layout(target_char, effect_text, extra_hint, feedback, level_title, stage_desc, idx, correct_count, screen_buffer, hints_enabled, item_queue, chord)
        raw_keys, decoded = read_chord_burst(timeout_ms=180)

        if '\x1b' in raw_keys:
            break
        if '\t' in raw_keys:
            hints_enabled = not hints_enabled
            state = '开启' if hints_enabled else '关闭'
            feedback = f'\033[1;36m提示已{state}；当前题目保持不变。\033[0m'
            continue

        valid_key_sets = current_item.get('valid_key_sets', chord.get('keys', []))
        if current_item.get('strict_keys'):
            is_matched = any(raw_keys == valid_kset for valid_kset in valid_key_sets)
        else:
            is_matched = decoded == target_char
            if not is_matched:
                is_matched = any(valid_kset.issubset(raw_keys) for valid_kset in valid_key_sets)

        if is_matched:
            token = current_item.get('char_token', target_char)
            screen_buffer += token
            if hints_enabled:
                feedback = f'\033[1;32m【{"/".join(raw_keys)} -> {target_char}】并击命中上屏！\033[0m'
            else:
                feedback = '\033[1;32m【读音编码正确】并击命中上屏！\033[0m'
            correct_count += 1
            idx += 1
            item_queue.pop(0)
            item_queue.append(next(item_source))
        else:
            input_repr = "+".join(sorted(raw_keys)) if len(raw_keys) > 1 else list(raw_keys)[0]
            if hints_enabled:
                feedback = f'\033[1;31m【{input_repr}】并击不符！目标: [{target_char}] ({chord["left"]} / {chord["right"]})\033[0m'
            else:
                feedback = f'\033[1;31m【{input_repr}】并击不符，请根据读音重试。\033[0m'

    clear_screen()
    move_cursor(5, 5)
    sys.stdout.write(f'\033[1m=== {level_title} 练习结束 ===\033[0m\n')
    move_cursor(7, 5)
    sys.stdout.write(f'练习题数: {idx}   命中数: {correct_count}   命中率: {correct_count/max(idx, 1)*100:.1f}%\n')
    move_cursor(9, 5)
    sys.stdout.write(f'屏幕已上屏内容: {screen_buffer}\n\n')
    move_cursor(11, 5)
    sys.stdout.write('按任意键返回主菜单...')
    sys.stdout.flush()
    getch_simple()

def choose_upper_zone(side):
    hand_name = '左手纯大写声母' if side == 'left' else '右手纯大写韵母'
    level_id = 4 if side == 'left' else 6
    while True:
        clear_screen()
        move_cursor(1, 3)
        sys.stdout.write(f'\033[1;36m=== {hand_name} · 分区选择 ===\033[0m')
        move_cursor(3, 3)
        sys.stdout.write('大写码元按 A-G、H-N、O-T、U-Z 四区训练；综合区覆盖全部 A-Z。')
        for index, (shortcut, zone_name, codes) in enumerate(UPPER_ZONES):
            move_cursor(5 + index * 2, 3)
            shown_codes = ' '.join(code.upper() for code in codes)
            sys.stdout.write(f'\033[1;33m[{shortcut}] {zone_name}\033[0m  {shown_codes}')
        move_cursor(16, 3)
        sys.stdout.write('[0/Q/ESC] 返回主菜单')
        move_cursor(18, 3)
        sys.stdout.write('请选择分区: ')
        sys.stdout.flush()

        key = getch_simple().lower()
        if key in ('0', 'q', '\x1b'):
            return
        zone_by_key = {shortcut: (zone_name, codes) for shortcut, zone_name, codes in UPPER_ZONES}
        if key in zone_by_key:
            zone_name, codes = zone_by_key[key]
            title = f'{hand_name} · {zone_name}'
            desc = f'本区循环覆盖：{" ".join(code.upper() for code in codes)}'
            run_exercise(title, desc, level_id, upper_zone_item_stream(side, codes))

def choose_tone_difficulty(toneless=False):
    mode_title = '单字无声调（纯小写双拼）' if toneless else '单字声韵调完整并击'
    level_id = 12 if toneless else 7
    difficulty_options = [
        ('1', 2, '入门', '每个单字只需同时按下 2 个物理键'),
        ('2', 3, '进阶', '每个单字需要同时按下 3 个物理键'),
        ('3', 4, '挑战', '每个单字需要同时按下 4 个物理键'),
        ('4', None, '综合', '混合全部 2/3/4 键单字'),
    ]
    counts = {2: 0, 3: 0, 4: 0}
    if toneless:
        grouped = {}
        for entry in TONE_SYLLABLES:
            code = entry['code'].lower()
            if code == 'er':
                continue  # er 保留为“包裹当前候选并上屏”的功能码，不作为无声调音节题。
            grouped.setdefault(code, []).append(entry)
        count_items = [make_toneless_group_item(entries) for entries in grouped.values()]
    else:
        count_items = [make_tone_item(entry) for entry in TONE_SYLLABLES]
    for item in count_items:
        counts[item['difficulty_key_count']] += 1
    total_count = len(count_items)

    while True:
        clear_screen()
        move_cursor(1, 3)
        sys.stdout.write(f'\033[1;36m=== {mode_title} · 难度选择 ===\033[0m')
        move_cursor(3, 3)
        sys.stdout.write('难度按一次并击实际需要按下的物理键数量划分。')
        for index, (shortcut, key_count, name, desc) in enumerate(difficulty_options):
            count = total_count if key_count is None else counts[key_count]
            move_cursor(5 + index * 2, 3)
            sys.stdout.write(f'\033[1;33m[{shortcut}] {name}\033[0m  {desc}（{count} 个单字题）')
        move_cursor(14, 3)
        sys.stdout.write('[0/Q/ESC] 返回主菜单')
        move_cursor(16, 3)
        sys.stdout.write('请选择难度: ')
        sys.stdout.flush()

        key = getch_simple().lower()
        if key in ('0', 'q', '\x1b'):
            return
        option_by_key = {shortcut: (key_count, name, desc) for shortcut, key_count, name, desc in difficulty_options}
        if key in option_by_key:
            key_count, name, desc = option_by_key[key]
            tag = '无声调' if toneless else '带调'
            title = f'{mode_title} · {name}'
            run_exercise(title, desc, level_id, tone_difficulty_item_stream(key_count, toneless=toneless))

MENU_ITEMS = [
    ('1', "第 1 关: 猫师并击 · 单键码元手位", 1, "单手原位直接击键，无限题库随机循环。"),
    ('2', "第 2 关: 猫师并击 · 复合并击码元", 2, "练习 h、i、j、k、l、m、n 等复合码元。"),
    ('3', "第 3 关: 左手纯小写声母 · 26 个码元", 3, "只使用左手；每轮完整覆盖 a-z。"),
    ('4', "第 4 关: 左手纯大写声母 · 分区训练", 4, "进入后选择 A-G、H-N、O-T、U-Z 或 A-Z 综合区。"),
    ('5', "第 5 关: 右手纯小写韵母 · 26 个码元", 5, "只使用右手；每轮完整覆盖 a-z 对应韵母。"),
    ('6', "第 6 关: 右手纯大写韵母 · 分区训练", 6, "进入后选择 A-G、H-N、O-T、U-Z 或 A-Z 综合区。"),
    ('7', "第 7 关: 单字并击 · 无声调纯小写模式", 12, "不带声调！只打纯小写双拼，支持 2/3/4 键分级练习。"),
    ('8', "第 8 关: 单字并击 · 声母+韵母+声调", 7, "官方完整带调双拼，按 2/3/4 个物理键选择难度。"),
    ('9', "第 9 关: 猫师并击 · 常用高频符号", 8, "双手同时敲击特定组合输出标点。"),
    ('a', "第 10 关: 猫师并击 · 0-9 数字", 9, "数字行与复合键位并击数字。"),
    ('b', "第 11 关: 猫师并击 · 虎码与二笔辅助字根", 10, "练习全码中的大写辅助字根码元。"),
    ('c', "【∞】 猫师并击 · 全题型综合无限练习", 11, "大小写声韵、带调音码、复合码元、符号和数字随机混编。"),
]

def main():
    while True:
        clear_screen()
        move_cursor(1, 3)
        sys.stdout.write('┌─────────────────────────── 猫师自然码并击 · 交互式练习系统 ───────────────────────────┐\n')
        move_cursor(2, 3)
        sys.stdout.write('│  【特点】：无限出题、180ms并击检测、Tab提示开关、阶梯键盘、真实打字上屏效果     │\n')

        for i, (shortcut, title, lid, desc) in enumerate(MENU_ITEMS):
            tag = f'[{shortcut.upper()}]'
            move_cursor(4 + i * 2, 3)
            sys.stdout.write(f'│   \033[1;36m{tag}\033[0m {title}')
            move_cursor(4 + i * 2, 84)
            sys.stdout.write('│\n')
            move_cursor(5 + i * 2, 3)
            sys.stdout.write(f'│       \033[2m说明: {desc}\033[0m')
            move_cursor(5 + i * 2, 84)
            sys.stdout.write('│\n')

        exit_row = 4 + len(MENU_ITEMS) * 2
        move_cursor(exit_row, 3)
        sys.stdout.write('│  \033[1m[0]\033[0m 退出程序                                                                             │\n')
        move_cursor(exit_row + 1, 3)
        sys.stdout.write('└──────────────────────────────────────────────────────────────────────────────────┘\n')
        move_cursor(exit_row + 2, 3)
        sys.stdout.write('请按 [1-9/A/B/C] 选择关卡，或按 [0/Q/ESC] 退出: ')
        sys.stdout.flush()

        key = getch_simple()
        normalized_key = key.lower()
        if normalized_key in ('0', 'q', '\x1b'):
            clear_screen()
            print('感谢使用，祝练习愉快！')
            break
        menu_by_key = {shortcut: (title, lid, desc) for shortcut, title, lid, desc in MENU_ITEMS}
        if normalized_key in menu_by_key:
            title, lid, desc = menu_by_key[normalized_key]
            if lid == 4:
                choose_upper_zone('left')
            elif lid == 6:
                choose_upper_zone('right')
            elif lid == 12:
                choose_tone_difficulty(toneless=True)
            elif lid == 7:
                choose_tone_difficulty(toneless=False)
            else:
                run_exercise(title, desc, lid)

if __name__ == '__main__':
    main()
