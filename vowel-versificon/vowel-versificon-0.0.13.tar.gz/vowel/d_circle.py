Ans="""
declare
--declare constant
pi constant number:=3.14;
--other declarations
area number(6,2);
dia number(6,2);
cir number(6,2);
radius number(6,2);
begin
radius:=4;
dia:=radius*2;
cir:=2*pi*radius;
area:=pi*radius*radius;
dbms_output.put_line('Radius of the circle is 'Ilradius);
dbms_output.put_line('Diameter of the circle is 'Ildia);
dbms_output.put_line('Circumference of the circle is 'llcir);
dbms_output.put_1ine('Area of the circle is 'Ilarea);
end;
/
"""