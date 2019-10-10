Ans="""
declare

a number(2):=10;
begin

while a<20 loop
dbms_output.put_line('Value of a: 'IIa);
a:=a+1;

if a>15 then
exit;

end if;

end loop;

end;
"""