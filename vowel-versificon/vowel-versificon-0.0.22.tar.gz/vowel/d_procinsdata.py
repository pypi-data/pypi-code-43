Ans="""
create table userl
(id number primary key,
name varchar(30));

create or replace procedure num
(id in number,name in varchar)

as

begin

insert into userl values(id,name);
end;

exec num(1,'Sandy');
"""