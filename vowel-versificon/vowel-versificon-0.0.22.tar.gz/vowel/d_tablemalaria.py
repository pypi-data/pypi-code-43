Ans="""

create table patient
(pno int,

pname varchar(20),
ptype varchar(20));

insert into patient(pno,pname,ptype)
values(1,'Rohan','Malaria');

select * from patient;

declare

a_pno patient.pno % type;

a_pname patient.pname % type;

a_ptype patient.ptype % type;

begin

select pno,pname,ptype into a_pno,a_pname,a_ptype from patient where ptype in 'Malaria';
dbms_output.put_line('Patient no is 'IIa_pno);

dbms_output.put_line('Patient name is 'IIa_pname);

dbms_output.put_line('Patient suffering from disease 'IIa_ptype);

end;

"""