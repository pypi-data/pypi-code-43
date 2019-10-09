Ans="""

declare

ino number:=&ino;

iname varchar2(50):='&iname';

qty number(S):=&qty;

up number(7,2):=&up;

dis number(7,2):=0;

bill number(7,2);

net number(7,2);

begin

bill:=qty*up;

if bill > 500 then

dis:= bill * 2 / 100;

end if;

net:=bill-dis;
dbms_output.put_line('Item no 'IIino);
dbms_output.put_line('Item name 'IIiname);
dbms_output.put_line('Quantity 'IIqty);
dbms_output.put_line('Unit price 'IIup);
dbms_output.put_line('Bill amt 'IIbill);
dbms_output.put_line('Discount 'IIdis);
dbms_output.put_line('Net amt 'IInet);
end;

"""