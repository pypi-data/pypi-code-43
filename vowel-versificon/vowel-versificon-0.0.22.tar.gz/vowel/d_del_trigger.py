Ans="""
create trigger student_Delete_Trigger

After DELETE

on student

begin

if deleting then

dbms_output.put_line('After deletion trigger fired');
end if;

end;


delete from student where Sno=101;
"""