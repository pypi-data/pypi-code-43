import py3toolbox as tb
import os, sys
import time

text_str1 = '  {0:>4} - {1:<12} : {2:>11} : {3:<10}'.format('*', '[ Manager ]', 123456, 234)
text_str2 = '  {0:>4} - {1:<12} : {2:>11} : {3:<10}'.format('*', '[ Manager ]', 456,    234)
text_str3 = '  {0:>4} - {1:<12} : {2:>11} : {3:<10}'.format('*', '[ Tester  ]', tb.render('[%LGREEN:123456%]',align='>',width=11), 234) 
text_str4 = tb.render('  {0:>4} - {1:<12} : {2:>11} : {3:<10}'.format('*', '[ Tester  ]', '[%LGREEN:123456%]', 234)) 
print (len(text_str1), text_str1)
print (len(text_str2), text_str2)
print (len(text_str3), text_str3)
print (len(text_str4), text_str4)
print (len(tb.render('[%LGREEN:123456%]')))
exit(1)

print (           '  {0:>4} - {1:<12} : {2:>11}'.format('*', '[ Manager ]', 123456                ))
print (           '  {0:>4} - {1:<12} : {2:>11}'.format('*', '[ Manager ]', 12345678901          ))
print ( '  {0:>4} - {1:<12} : {2:>11}'.format('*', '[ Tester  ]', tb.render('[%LGREEN:123456%]',align='R',width=11 ) ))
print ( '  {0:>4} - {1:<12} : {2:>11}'.format('*', '[ Tester  ]', tb.render('123456',align='<',width=11 ) ))
print (           '  {0:>4} - {1:<12} : {2:>11}'.format('*', '[ Manager ]', 234567                ))
exit (1)


tb.pause()
#print(tb.render('[BRIGHT|LYELLOW_BG|BLUE|UNDERLINE:[Test]] asdasdasd [LBLUE|LYELLOW_BG:Pattern] ddd'))
for i in range(101):
  tb.keep_print (tb.get_progress_bar(i,100))
  time.sleep(0.1)

