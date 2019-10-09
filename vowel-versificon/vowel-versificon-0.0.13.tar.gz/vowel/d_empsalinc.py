Ans="""

create table employee
( eid int primary key,
ename varchar(20),
start_date date,
salary number(10,2));

insert into employee(eid,ename,start_date,salary)
values(1,'Einstein','2-feb-2001',50000);

select * from employee;


declare

a_eid employee.eid % type;

a_ename employee.ename % type;

a_start_date employee.start_date % type;

a_sa1ary employee.sa1ary % type;

begin

select eid,ename,start_date,salary into a_eid,a_ename,a_start_date,a_salary from employee where eid=&eid;
if (a_start_date<='17-ieb-2015')then

a_salary:=a_salary+a_sa1ary*(15/100);

dbms_output.put_1ine(a_enameIl' salary after increased by 15% is 'Ila_sa1ary);
else

a_salary::a_salary+a_salary*(5/100);

dbms_output.put_line(a_enameIl' salary after increased by 5% is 'lla_salary);
end if;

end;


"""