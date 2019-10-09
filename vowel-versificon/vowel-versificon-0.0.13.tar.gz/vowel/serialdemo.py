Ans="""

import java.io.*;
class employee implements java.io.Serializable
{
public String name;
public String address;
public transient int SSN;
public int number;
employee(String nm,String a,int s,int n)
{
name=nm;
address=a;
SSN=s;
number=n;
System.out.println("mailing a cheque to " +name+ " "+a);
}

}


public class SerializedDemo
{
public static void main(String args[])
{

employee e=new employee("anju","bhandup",111213,101);

try
{
File f= new File("/home/labpc-37/employee.txt");
FileOutputStream fileout=new FileOutputStream(f);
ObjectOutputStream out=new ObjectOutputStream(fileout);
out.writeObject(e);
out.close();
fileout.close();
System.out.println("Serialized data is saved in employee.txt");
}
catch(IOException i)
{
i.printStackTrace();
}
}
}

"""