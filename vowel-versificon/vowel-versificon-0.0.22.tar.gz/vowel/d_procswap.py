Ans="""
create or replace procedure swap(a in out number,b in out number)
as t number;

begin

dbms_output.put_line('Before swapping a: 'IIaII'and b 'IIb);
t:=a;

a:=b;

b:=t;

dbms_output.put_line('Before swapping a: 'IIaII'and b 'IIb);

end;
"""