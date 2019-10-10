Ans="""
create table emp
(eid number(15),
ename varchar(15),
doj date,

esalary number(15));

insert into emp values(l,'Raju','1-jun—2012',15000);

Select * from emp;

Create table customer
(cid number(15),
purchase number(15));

insert into customer values(1,3000);

select * from customer;

declare

empid varchar(25);

cusid number(3);

begin

empid:=&empid;
cusid:=&cusid;

update emp

set esalary=esalary+5000;
update emp

set esalary=esalary+1000
where eid=empid;
savepoint 51;

update customer

set purchase=purchase+5000
where cid=cusid;

rollback to savepoint 51;
commit;

end;

select * from customer;

select * from emp;
"""