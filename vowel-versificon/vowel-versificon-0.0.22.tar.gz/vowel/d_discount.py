Ans="""
declare

product varchar(30):=&product;
qty number(5):=&qty;

price number(6,2):=&price;

dis number(6,2):=0;

tamt number(10,2);

bill number(10,2);

begin

bill:=qty*price;

if bill > 1000 then
dis:=bill*20/1000;

end if;

tamtzzbill-dis;
dbms_output.put_line('The total amount is 'IItamt);
end;
"""