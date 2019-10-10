Ans="""
declare

great varchar(30):='Menon college';
begin
dbms_output.put_line(Lower(great));
dbms_output.put_line(Upper(great));
dbms_output.put_line(Initcap(great));
dbms_output.put_line(substr(great,1,1));
dbms_output.put_line(substr(great,-1,1));
dbms_output.put_line(substr(great,7,5));
dbms_output.put_line(Substr(great,2));
dbms_output.put_line(instr(great,'e'));
end;
"""