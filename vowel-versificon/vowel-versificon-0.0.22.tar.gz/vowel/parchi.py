Ans="""

public class Parent
{
    public void p1()
    {
    System.out.println("Parent");
    }}
    class Child extends Parent
    {
    public void c1()
    {
    System.out.println("Child");
    }
    
    public static void main(String[] args) {
        Child t=new Child();
        t.p1();
        t.c1();
    }} 
"""