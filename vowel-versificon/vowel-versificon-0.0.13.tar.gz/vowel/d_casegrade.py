Ans="""
declare

grade char(1):='A';

begin

case grade

when 'A' then dbms_output.put_line('Excellent');
when '8' then dbms_output.put_line('Very good');
when 'C' then dbms_output.put_line('Nell done');
when 'D' then dbms_output.put_line('You passed');
when 'F' then dbms_output.put_line('You failed');
else dbms_output.put_line('No such grades');

end case;

end;
"""