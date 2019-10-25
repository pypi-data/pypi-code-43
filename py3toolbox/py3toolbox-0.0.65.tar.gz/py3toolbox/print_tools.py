import os,sys
import ctypes

import py3toolbox.text_tools as text_tools

if os.name=='nt' and sys.getwindowsversion().major == 10:
  kernel32 = ctypes.windll.kernel32
  kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

PATTERN = {
  "BRIGHT"      : "1",
  "UNDERLINE"   : "4",
  "DIM"         : "2",

  "WHITE"       : "97",  
  "BLACK"       : "30",
  "RED"         : "31",
  "GREEN"       : "32",
  "BLUE"        : "34",
  "YELLOW"      : "33",
  "MAGENTA"     : "35",
  "CYAN"        : "36",
  
  "LGRAY"       : "37",
  "DGRAY"       : "90",
  "LRED"        : "91",
  "LGREEN"      : "92",
  "LYELLOW"     : "93",
  "LBLUE"       : "94",
  "LMAGENTA"    : "95",
  "LCYAN"       : "96",

  "WHITE_BG"    : "107",  
  "BLACK_BG"    : "40",
  "RED_BG"      : "41",
  "GREEN_BG"    : "42",
  "YELLOW_BG"   : "43",
  "BLUE_BG"     : "44",
  "MAGENTA_BG"  : "45",
  "CYAN_BG"     : "46",

  "LGRAY_BG"    : "47",
  "DGRAY_BG"    : "100",
  "LRED_BG"     : "101",
  "LGREEN_BG"   : "102",
  "LYELLOW_BG"  : "103",
  "LBLUE_BG"    : "104",
  "LMAGENTA_BG" : "105",
  "LCYAN_BG"    : "106",
  
  "DEFAULT"     : 0

}



def cls():
  os.system('cls' if os.name=='nt' else 'clear')
  
def render(text, align=None, width=None):
  render_groups = text_tools.re_findall(r'(\[\%([\w+\|?]+)\:([^\:\|\%]+)\%\]?)', text)
  render_text   = text
  for render_section in render_groups:
    src_text, render_patterns,raw_text = (render_section[0],text_tools.re_findall(r'(\w+)',render_section[1]),render_section[2])
    term_pattern = '\033['
    for p in render_patterns:
      if p not in PATTERN.keys() : raise ValueError( 'Pattern: [' + p + '] not defined!')
      term_pattern += PATTERN[p] + ';'

    if os.name=='nt' and sys.getwindowsversion().major != 10 :
      term_pattern = raw_text
    else:
      term_pattern = term_pattern[:-1] + 'm' + raw_text + '\033[0m'
    
    if (align is not None) and (width is not None):
      if align == '>' or align == 'R' :
        term_pattern = ' ' * (width - len(raw_text)) + term_pattern
      if align == '<' or align == 'L' :
        term_pattern = term_pattern + ' ' * (width - len(raw_text)) 
        
    render_text = render_text.replace(src_text,term_pattern)
  return (render_text)
  

  
  
def pause(txt=None) :
  press_keys_info = "Confirm and press [%LGREEN_BG|BLACK:[Enter]%] to continue ... or [%LRED_BG|BLACK:[Ctrl-C]%] to exit ...\n\n"
  if txt is None : txt = "\n\n---> " 
  pause_txt = txt + press_keys_info
  input(render(pause_txt))


def keep_print(text):
  print (text, sep=' ', end='', flush=True)    
  
def get_progress_bar(current, total, scale=50):
  percent = int(current/total*100+0.5)
  if percent <0   : percent = 0
  if percent >100 : percent = 100
  arrow_pos =  int(percent * scale /100 ) 
  if arrow_pos <=1 : 
    progress_bar = '[%LYELLOW:>%]' * arrow_pos + '[%LRED:.%]' * (scale - arrow_pos)
  else:
    if percent < 100 :
      progress_bar = '[%LGREEN:=%]' * (arrow_pos -1) + '[%LYELLOW:>%]' + '[%LRED:.%]' * (scale - arrow_pos)
    else:
      progress_bar = '[%LGREEN:=%]' * scale
  progress_bar = '    [{0}] {1:<5} {2:<12} \r'.format(progress_bar, str(percent) + '%', str(current) + '/' + str(total))
  return render(progress_bar)

def format_str(fmt, *args) :
  return (fmt.format(*args))   

if __name__ == "__main__":
  #'{1} {0}'.format('one', 'two')  
  print(format_str('{1} {0}', 'One', 'Tow'))
  #print (get_progress_bar(10,23))
  pass  