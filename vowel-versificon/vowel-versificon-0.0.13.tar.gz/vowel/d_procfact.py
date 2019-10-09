Ans="""
declare

i number(S);

f number(S);

procedure fact(no number)
is

begin

i:=1;

i:=1;

loop

f:=f*i;

i:=i+1;

exit when i>no;

end loop;
dbms_output.put_line('factorial isz'llf);
end fact;

begin

fact(5);

end;
"""