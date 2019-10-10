Ans="""
declare

numl number:=0;

begin

loop

num1:=num1+2;
dbms_output.put_line(num1);
exit when num1=20;

end loop;

end;
"""