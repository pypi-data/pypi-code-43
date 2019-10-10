Ans="""
create or replace function totalemployee
return number is total number(2):=0;
begin

Select count(*) into total

from employee;

return total;

end;

declare

c number(2);

begin

c:=totalemployee();

dbms_output.put_line('Total no of employeez'llc);
end;

/

"""