Ans="""

create table emp
(empno number,
ename varchar(20),
sal number);

insert into emp values(l,'Taheer',10000);

select * from emp;

declare

empnov emp.empno%type:=&empno;

salv number(7,2):=0;

begin

select sal into salv from emp where empno=empnov;
if salv < 2600 then
salv:=salv+salv*(10/100);

end if;

update emp set salzsalv where empno=empnov;
dbms_output.put_line('Empno is 'IIempnov);
dbms_output.put_line('Salary is 'IIsalv);
end;


select * from emp;



"""