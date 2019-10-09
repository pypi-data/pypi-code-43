Ans="""
declare

ai number(10,2):=&annualincome;

tax number(10,3):=0;

begin

if ai between 36000 and 50000 then
tax:=ai*10/100;

elsif ai between 50000 and 100000 then
tax:=800+ai*16/100;

elsif ai > 100000 then
tax:=2500+ai*25/100;

end if;

dbms_output.put_line('Annual income: 'IIai);
dbms_output.put_line('Income tax: 'IItax);
end;
"""