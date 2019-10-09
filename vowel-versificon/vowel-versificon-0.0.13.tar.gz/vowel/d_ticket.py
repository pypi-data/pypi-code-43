Ans="""
create table ticket
(ticketno number(15),
amount number(15),
status number(15));

insert into ticket values(1001,2500,1);

Select * from ticket;

declare

sts number(S);

no number(S);

begin

no:=&no;

Select status into sts from ticket where ticketno=no;
if (sts=0) then

update ticket

set status=1 where ticketno=no;
dbms_output.put_line('Ticket is available now');
dbms_output.put_line('Ticket has been committed');
commit;

else

rollback;

dbms_output.put_line('Ticket is already booked.');
dbms_output.put_line('Ticket has been rolled');
end if;

end;

select * from ticket;


"""