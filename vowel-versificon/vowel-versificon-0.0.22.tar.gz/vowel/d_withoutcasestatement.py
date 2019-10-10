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

select 1id,lname,lcourse,lclass into alid,alname,alcourse,alclass from lecturer where lid=&lid;
dbms_output put_line('Lecturer id is 'IIalid);
dbms_output.put_line(’Lecturer name is 'IIalname);
dbms_output.put_line(alnameII' takes course 'IIalcourse);
end;

"""