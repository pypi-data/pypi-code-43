Ans="""

create table supplier
(sno int,
sid int);

create or replace procedure insert1(sno number,sid number)
is begin

insert into supplier values(sno,sid);

end;

declare

a number;
begin

for a in 1..S
loop
insert1(a,23);
end loop;
commit;

end;

select * from supplier;

"""