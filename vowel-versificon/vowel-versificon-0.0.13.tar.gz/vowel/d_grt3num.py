Ans="""
declare

a number:=&a;

b number:=&b;

c number:=&c;

begin

if (a>b) and (a>c)then
dbms_output.put_line(alI' is greatest');

elsif (b>a) and (b>c) then
dbms_output.put_line(blI' is greatest');

else

dbms_output.put_line(clI' is greatest');

end if;

end;
"""