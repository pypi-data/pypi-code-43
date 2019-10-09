Ans="""
declare

name varchar(20);

company varchar2(30);

introduction clob;

choice char(1);

begin

namezz'John Smith';
companyzz'Infotech';
introduction:='Hello!I"m Tohn Smith from infotech';
choice:='y';

if choice='y' then
dbms_output.put_line(name);
dbms_output.put_line(company);
dbms_output.put_line(introduction);
end if;

end;
"""