Ans="""
create table employee
(eno integer,

ename varchar(25),
salary integer);

create table salary_changes
(saldif int);

create trigger emp_salary_trigger
after update of salary

on employee

for each row

declare

a integer;

begin

a:=:new.salary-:old.salary;

insert into salary_changes values(a);
dbms_output.put_line('Triggered fired after insert');
end;

insert into employee values(101,'Nilam',6000);

update employee
set salary=salary+2000
where eno=101;


"""