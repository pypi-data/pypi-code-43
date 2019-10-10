Ans="""
declare
--GLobal variable
numl number:=95;
num2 numberz=853
begin
dbms_output.put_line('Outer variable numl: 'Ilnuml);
dbms_output.put_line('Outer variable num2: 'IInumZ);
declare
--local variable
numl number:=195;
num2 number:=185;
begin
dbms_output.put_line('Inner variable of numl: 'IInuml);
dbms_output.put_line('Inner variable of num2: 'IInumZ);
end;
end;

"""