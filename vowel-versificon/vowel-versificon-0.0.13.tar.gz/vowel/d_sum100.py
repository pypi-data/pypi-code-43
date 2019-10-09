Ans="""
declare

x number:=1;

c number;

a number:=0;
begin

while x<100 loop
a:=a+x;

x:=x+2;

end loop;
dbms_output.put_line('Sum of the 100 natural numbers are 'IIa);
end;
"""