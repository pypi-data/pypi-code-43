Ans="""

create table emp
(empno number,
ename varchar(20),
sal number,
hiredate date);

insert into emp values(1,'Sarvesh',20000,'17-feb-2001');

Declare

Empnov number:=&empnov;

Enamev emp.ename%type;

Salv emp.sal%type;

Hiredatev emp.hiredate%type;

Exp number(7,2);

Ta number(7,2);

Da number(7,2);

Hra number(7,2);

Lic number(7,2);

Gross number(7,2);

S number:=0;

Begin

Select ename,sal,hiredate into enamev,salv,hiredatev from emp where empno=empnov;
Exp:=round(months_between(sysdate,hiredatev)/12,3);
Ta:=salv*30/100;

Da:=salv*20/100;

Hra:=salv*15/100;

Lic:=salv*5/100;
Gross:=sa1v+ta+da+hra-1ic;
Dbms_output.put_line('empno 'IIempnov);
Dbms_output.put_line('ename 'IIenamev);
Dbms_output.put_line('salary 'IIsalv);
Dbms_output.put_line('experience '[Iexp);
Dbms_output.put_line('ta 'IIta);
Dbms_output.put_line('da 'Ilda);
Dbms_output.put_line('hra 'Ilhra);
Dbms_output.put_line('lic 'Illic);
Dbms_output.put_line('gross 'Ilgross);

end;


"""