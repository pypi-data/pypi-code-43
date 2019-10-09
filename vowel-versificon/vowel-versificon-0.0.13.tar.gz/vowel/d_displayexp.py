Ans="""

create table emp
(empno number,
ename varchar(20),
sal number,
hiredate date);

insert into emp values(1,'Sarvesh',20000,'17-feb-2001');

Declare

Empnov number:=&empnov;

Hiredatev date;

Expv number(10,5);

Begin

Select hiredate into hiredatev from emp where empno=empnov;
Expv:=round(months_between(sysdate,hiredatev)/12,3);
Dbms_output.put_line('experience of emp'llempnovll' is 'IIexval' years ');
End;

"""