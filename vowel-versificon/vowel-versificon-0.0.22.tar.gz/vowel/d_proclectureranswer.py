Ans="""
create table lecture
(id number(10),
lect_name varchar(lS),

subject varchar(10));

insert into lecture values(1,'Tanmey','OS');

create or replace procedure lect(i in number,s in varchar)
as

begin

update lecture set subject=s

where id=i;

end;

/
declare

i number(2);

n varchar(10);
s varchar(S);
begin

i:=&i;

s:=&s;
lect(i,s);
end;

/


"""