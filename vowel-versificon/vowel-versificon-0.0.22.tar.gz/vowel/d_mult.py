Ans="""
declare

a number(2):=&a;
b number(2):=1;
c number(3);
begin

while b <=10
loop

c:=a*b;
dbms_output.put_line(alI'*'IIbII'='IIc);
b:=b+1;

end loop;

end;
"""