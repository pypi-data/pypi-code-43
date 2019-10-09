Ans="""
create sequence hosp
increment by 1

cache 2

start with 1
maxvalue S0

cycle;

create table patient
(patient_no number(10),
patient_name varchar(10),
illness_type varchar(20));

insert into patient values(hosp.nextval,'Jagdish','Thyroid');

select * from patient;

alter sequence hosp cache 2 increment by 5;

insert into patient values(hosp.nextval,'Jak','Kidneystone');

Select * from patient;
"""