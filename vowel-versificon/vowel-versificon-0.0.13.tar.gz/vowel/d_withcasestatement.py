Ans="""

create table lecturer
(lid int primary key,
lname varchar(20),
lcourse varchar(20),
lclass varchar(10));

insert into lecturer(lid,lname,lcourse,lclass)
values(1,'Deepa mam','PL/SQL','SYCS');

select * from lecturer;

declare

alid 1ecturer.1id % type;

alname 1ecturer.1name % type;

alcourse 1ecturer.1course % type;

alclass 1ecturer.1class % type;

begin

select lid,lname,lcourse,lclass into alid,alname,alcourse,alclass from lecturer where lid=&lid;
case alcourse

when 'PL/SQL' then dbms_output.put_line('Deepa mam id is 1 and takes course PL/SQL');
when 'OS' then dbms_output.put_line('Subha mam id is 3 and takes course PL/SQL');
when 'IOT' then dbms_output.put_line('Vandana mam id is 5 and takes course PL/SQL');
when 'TOC' then dbms_output.put_line('Rajesh sir id is 4 and takes course PL/SQL');
when 'HTML' then dbms_output.put_line('Kalpana mam id is 6 and takes course PL/SQL');
when 'CGT' then dbms_output.put_line('Nisha mam id is 7 and takes course PL/SQL');
when 'JAVA' then dbms_output.put_line('Saloni mam id is 2 and takes course PL/SQL');
else dbms_output.put_line('No course available');

end case;

end;

"""