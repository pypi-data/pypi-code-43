Ans="""

create table place
(room_id int,

rno int,

bno int,

nseats int primary key);

insert into place(room_id,rno,bno,nseats)
values(1,101,5,100);

select * from place;

declare

aroom_id place.room_id X type;

arno p1ace.rno X type;

abno p1ace.bno X type;

anseats p1ace.nseats X type;

begin

select room_id,rno,bno,nseats into aroom_id,arno,abno,anseats from place where nseats=&nseats;
if(anseats<100) then

dbms_output.put_line('A FAIRLY SMALL');
elsif(anseats>=100 and anseats<=250) then
dbms_output.put_line('A LITTLE BIGGER ROOM');

else

dbms_output.put_line('ROOM HAVING LOTS OF SPACE');
end if;

dbms_output.put_line('ROOM ID IS 'Ilaroom_id);
dbms_output.put_line('ROOM no IS 'Ilarno);
dbms_output.put_line('ROOM no 15 'Ilabno);

end;

"""