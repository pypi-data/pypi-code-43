Ans="""
create table faculty
(fname varchar(20));

create table subject
(sname varchar(20));

create view my_view
as
select fname, sname from faculty,subject;

insert into faculty values(‘Savita');

insert into subject values(‘Chemistry');

create trigger my_trigger

instead of insert on my_view

begin

insert into faculty values(:new.fname);
insert into subject values(:new.sname);
dbms_output.put_line('Trigger fired ');
end;

Select * from my_view;

insert into my_view values(‘Deepa mam','DBMS');

Select * from my_view;


"""