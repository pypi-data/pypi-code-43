Ans="""

create table emp
(empno number,
ename varchar(20),
sal number);

insert into emp values(1,'Taheer',10000);

select * from emp;

declare

empnov number:=&empnov;

salv number;

b number(7,2);

begin

select sal into salv from emp where empno=empnov;
if salv between 500 and 3500 then
b:=salv*10/100;

elsif salv between 3500 and 10000 then
b:=salv*12/100;

elsif sa1v>10000 then

b:=salv*13.5/100;

end if;

dbms_output.put_line('Empno 'IIempnov);
dbms_output.put_line('Salary 'Ilsalv);
dbms_output.put_line('Bonus 'IIb);

end;



"""