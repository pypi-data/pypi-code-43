Ans="""
create sequence employee
increment by -1

start with 10

minvalue S

maxvalue 100

nocycle;

create table emp
(empno number(10),
empname varchar(20),
salary number(10,2));

insert into emp values(employee.nextval,'Ram',20000);

Select * from emp;

insert into emp values(employee.nextval,'Rudra',24000);

alter sequence employee minvalue 3;

insert into emp values(employee.nextval,'Mohan',54000);

select * from emp;
"""