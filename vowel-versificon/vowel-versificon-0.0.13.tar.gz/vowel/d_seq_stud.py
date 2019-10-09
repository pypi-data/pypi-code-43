Ans="""
create sequence college
increment by 1

start with 1

maxvalue 4

nocycle;

create table student
(stud_no number(10),
stud_name varchar(20),
course varchar(20));

insert into student values(college.nextval,'Priya','Networking');

select * from student;

alter sequence college maxvalue 5;

insert into student values(college.nextval,'Shreyas','I.T');
"""