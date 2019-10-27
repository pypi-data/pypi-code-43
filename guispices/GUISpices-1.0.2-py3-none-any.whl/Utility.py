import subprocess
import sys
import os


def decode_utf8_fixed(string: bytes) -> str:
    """Recursive function to replace invalid (non UTF-8) chars.
    Recommended for parsing non-english output from subprocess.Popen.
    The maximum recursion depth is 64, if all chars are present."""

    try:
        string = string.decode("UTF-8")  # if it doesn't contain invalid chars
        return string.replace("\r\n", "\n")
    except UnicodeDecodeError as e:  # else, replace invalid char and repeat
        char = str(e).split("can't decode byte ")[1].split(" in position")[0][1:]

        if char == 'xa8':
            string = string.replace(b'\xa8', b'\xc2\xbf')  # ¿
            return decode_utf8_fixed(string)
        if char == 'xb7':
            string = string.replace(b'\xb7', b'\xc3\x80')  # À
            return decode_utf8_fixed(string)
        if char == 'xb5':
            string = string.replace(b'\xb5', b'\xc3\x81')  # Á
            return decode_utf8_fixed(string)
        if char == 'xb6':
            string = string.replace(b'\xb6', b'\xc3\x82')  # Â
            return decode_utf8_fixed(string)
        if char == 'xc7':
            string = string.replace(b'\xc7', b'\xc3\x83')  # Ã
            return decode_utf8_fixed(string)
        if char == 'x8e':
            string = string.replace(b'\x8e', b'\xc3\x84')  # Ä
            return decode_utf8_fixed(string)
        if char == 'x8f':
            string = string.replace(b'\x8f', b'\xc3\x85')  # Å
            return decode_utf8_fixed(string)
        if char == 'x92':
            string = string.replace(b'\x92', b'\xc3\x86')  # Æ
            return decode_utf8_fixed(string)
        if char == 'x80':
            string = string.replace(b'\x80', b'\xc3\x87')  # Ç
            return decode_utf8_fixed(string)
        if char == 'xd4':
            string = string.replace(b'\xd4', b'\xc3\x88')  # È
            return decode_utf8_fixed(string)
        if char == 'x90':
            string = string.replace(b'\x90', b'\xc3\x89')  # É
            return decode_utf8_fixed(string)
        if char == 'xd2':
            string = string.replace(b'\xd2', b'\xc3\x8a')  # Ê
            return decode_utf8_fixed(string)
        if char == 'xd3':
            string = string.replace(b'\xd3', b'\xc3\x8b')  # Ë
            return decode_utf8_fixed(string)
        if char == 'xde':
            string = string.replace(b'\xde', b'\xc3\x8c')  # Ì
            return decode_utf8_fixed(string)
        if char == 'xd6':
            string = string.replace(b'\xd6', b'\xc3\x8d')  # Í
            return decode_utf8_fixed(string)
        if char == 'xd7':
            string = string.replace(b'\xd7', b'\xc3\x8e')  # Î
            return decode_utf8_fixed(string)
        if char == 'xd8':
            string = string.replace(b'\xd8', b'\xc3\x8f')  # Ï
            return decode_utf8_fixed(string)
        if char == 'xd1':
            string = string.replace(b'\xd1', b'\xc3\x90')  # Ð
            return decode_utf8_fixed(string)
        if char == 'xa5':
            string = string.replace(b'\xa5', b'\xc3\x91')  # Ñ
            return decode_utf8_fixed(string)
        if char == 'xe3':
            string = string.replace(b'\xe3', b'\xc3\x92')  # Ò
            return decode_utf8_fixed(string)
        if char == 'xe0':
            string = string.replace(b'\xe0', b'\xc3\x93')  # Ó
            return decode_utf8_fixed(string)
        if char == 'xe2':
            string = string.replace(b'\xe2', b'\xc3\x94')  # Ô
            return decode_utf8_fixed(string)
        if char == 'xe5':
            string = string.replace(b'\xe5', b'\xc3\x95')  # Õ
            return decode_utf8_fixed(string)
        if char == 'x99':
            string = string.replace(b'\x99', b'\xc3\x96')  # Ö
            return decode_utf8_fixed(string)
        if char == 'x9e':
            string = string.replace(b'\x9e', b'\xc3\x97')  # ×
            return decode_utf8_fixed(string)
        if char == 'x9d':
            string = string.replace(b'\x9d', b'\xc3\x98')  # Ø
            return decode_utf8_fixed(string)
        if char == 'xeb':
            string = string.replace(b'\xeb', b'\xc3\x99')  # Ù
            return decode_utf8_fixed(string)
        if char == 'xe9':
            string = string.replace(b'\xe9', b'\xc3\x9a')  # Ú
            return decode_utf8_fixed(string)
        if char == 'xea':
            string = string.replace(b'\xea', b'\xc3\x9b')  # Û
            return decode_utf8_fixed(string)
        if char == 'x9a':
            string = string.replace(b'\x9a', b'\xc3\x9c')  # Ü
            return decode_utf8_fixed(string)
        if char == 'xed':
            string = string.replace(b'\xed', b'\xc3\x9d')  # Ý
            return decode_utf8_fixed(string)
        if char == 'xe8':
            string = string.replace(b'\xe8', b'\xc3\x9e')  # Þ
            return decode_utf8_fixed(string)
        if char == 'xe1':
            string = string.replace(b'\xe1', b'\xc3\x9f')  # ß
            return decode_utf8_fixed(string)
        if char == 'x85':
            string = string.replace(b'\x85', b'\xc3\xa0')  # à
            return decode_utf8_fixed(string)
        if char == 'xa0':
            string = string.replace(b'\xa0', b'\xc3\xa1')  # á
            return decode_utf8_fixed(string)
        if char == 'x83':
            string = string.replace(b'\x83', b'\xc3\xa2')  # â
            return decode_utf8_fixed(string)
        if char == 'xc6':
            string = string.replace(b'\xc6', b'\xc3\xa3')  # ã
            return decode_utf8_fixed(string)
        if char == 'x84':
            string = string.replace(b'\x84', b'\xc3\xa4')  # ä
            return decode_utf8_fixed(string)
        if char == 'x86':
            string = string.replace(b'\x86', b'\xc3\xa5')  # å
            return decode_utf8_fixed(string)
        if char == 'x91':
            string = string.replace(b'\x91', b'\xc3\xa6')  # æ
            return decode_utf8_fixed(string)
        if char == 'x87':
            string = string.replace(b'\x87', b'\xc3\xa7')  # ç
            return decode_utf8_fixed(string)
        if char == 'x8a':
            string = string.replace(b'\x8a', b'\xc3\xa8')  # è
            return decode_utf8_fixed(string)
        if char == 'x82':
            string = string.replace(b'\x82', b'\xc3\xa9')  # é
            return decode_utf8_fixed(string)
        if char == 'x88':
            string = string.replace(b'\x88', b'\xc3\xaa')  # ê
            return decode_utf8_fixed(string)
        if char == 'x89':
            string = string.replace(b'\x89', b'\xc3\xab')  # ë
            return decode_utf8_fixed(string)
        if char == 'x8d':
            string = string.replace(b'\x8d', b'\xc3\xac')  # ì
            return decode_utf8_fixed(string)
        if char == 'xa1':
            string = string.replace(b'\xa1', b'\xc3\xad')  # í
            return decode_utf8_fixed(string)
        if char == 'x8c':
            string = string.replace(b'\x8c', b'\xc3\xae')  # î
            return decode_utf8_fixed(string)
        if char == 'x8b':
            string = string.replace(b'\x8b', b'\xc3\xaf')  # ï
            return decode_utf8_fixed(string)
        if char == 'xd0':
            string = string.replace(b'\xd0', b'\xc3\xb0')  # ð
            return decode_utf8_fixed(string)
        if char == 'xa4':
            string = string.replace(b'\xa4', b'\xc3\xb1')  # ñ
            return decode_utf8_fixed(string)
        if char == 'x95':
            string = string.replace(b'\x95', b'\xc3\xb2')  # ò
            return decode_utf8_fixed(string)
        if char == 'xa2':
            string = string.replace(b'\xa2', b'\xc3\xb3')  # ó
            return decode_utf8_fixed(string)
        if char == 'x93':
            string = string.replace(b'\x93', b'\xc3\xb4')  # ô
            return decode_utf8_fixed(string)
        if char == 'xe4':
            string = string.replace(b'\xe4', b'\xc3\xb5')  # õ
            return decode_utf8_fixed(string)
        if char == 'x94':
            string = string.replace(b'\x94', b'\xc3\xb6')  # ö
            return decode_utf8_fixed(string)
        if char == 'xf6':
            string = string.replace(b'\xf6', b'\xc3\xb7')  # ÷
            return decode_utf8_fixed(string)
        if char == 'x9b':
            string = string.replace(b'\x9b', b'\xc3\xb8')  # ø
            return decode_utf8_fixed(string)
        if char == 'x97':
            string = string.replace(b'\x97', b'\xc3\xb9')  # ù
            return decode_utf8_fixed(string)
        if char == 'xa3':
            string = string.replace(b'\xa3', b'\xc3\xba')  # ú
            return decode_utf8_fixed(string)
        if char == 'x96':
            string = string.replace(b'\x96', b'\xc3\xbb')  # û
            return decode_utf8_fixed(string)
        if char == 'x81':
            string = string.replace(b'\x81', b'\xc3\xbc')  # ü
            return decode_utf8_fixed(string)
        if char == 'xec':
            string = string.replace(b'\xec', b'\xc3\xbd')  # ý
            return decode_utf8_fixed(string)
        if char == 'xe7':
            string = string.replace(b'\xe7', b'\xc3\xbe')  # þ
            return decode_utf8_fixed(string)
        if char == 'x98':
            string = string.replace(b'\x98', b'\xc3\xbf')  # ÿ
            return decode_utf8_fixed(string)


def popen(cmd: str) -> str:
    """For pyinstaller -w"""
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    process = subprocess.Popen(cmd, startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    return decode_utf8_fixed(process.stdout.read())


def resource_path(relative_path: str) -> str:
    """For pyinstaller -F"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
