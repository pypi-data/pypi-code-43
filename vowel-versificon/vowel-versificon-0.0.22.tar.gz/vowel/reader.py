Ans="""


package controller;


class Controller {
    int areader=0,awriter=0,wwriter=0,wreader=0;
    public int allowreader()
    {
        int res=0;
        if(wreader==0 && awriter==0)
        {
            res=1;
        }
        return res;
    }
    public int allowwriter()
    {
        int res=0;
        if(areader==0 && awriter==0)
        {
            res=1;
        }
        return res;
    }
synchronized void beforeread()
{
    wreader++;
    while(allowreader()!=0)
    {
        try
        {
            wait();
        }
        catch(InterruptedException e)
        {
            
        }
        wreader--;
        areader++;
    }
    
}
synchronized void beforewrite()
{
    wwriter++;
    while(allowwriter()!=0)
    {
        try
        {
            wait();
        }
        catch(InterruptedException e)
        {
            
        }
        wwriter--;
        awriter++;
        
    }
}
synchronized void afterread()
{
    areader--;
    notifyAll();
}
synchronized void afterwrite()
{
    awriter--;
    notifyAll();
}
}
public class reader
{
    static Controller ctl;
   
    
    public static void main(String[] args) {
       ctl=new Controller();
       new reader1(ctl).start();
       new reader2(ctl).start();
       new writer1(ctl).start();
       new writer2(ctl).start();
       
    }
    
}
class reader1 extends Thread
{
    Controller ctl;
    public reader1(Controller c)
    {
        ctl=c;
    }
    public void run()
    {
        int a=0;
        while(true&&a<2)
        {
            a++;
            ctl.beforeread();
            System.out.println("reader1 reading");
            System.out.println("done reading ");
            ctl.afterread();
            System.out.println("after read");
        }
    }
}
class reader2 extends Thread
{
    Controller ctl;
    public reader2(Controller c)
    {
        ctl=c;
    }
    public void run()
    {
        int b=0;
        while(true&&b<2)
        {
            b++;
            ctl.beforeread();
            System.out.println("reader2 reading");
            System.out.println("done reading ");
            ctl.afterread();
            System.out.println("after read");
        }
    }
}
class writer1 extends Thread
{
    Controller ctl;
    public writer1(Controller c)
    {
        ctl=c;
    }
    public void run()
    {
        int c=0;
        while(true&&c<2)
        {
            c++;
            ctl.beforewrite();
            System.out.println("writer1 writing");
            System.out.println("Done writing ");
            ctl.afterwrite();
            System.out.println("after write");
        }
    }
}
class writer2 extends Thread
{
    Controller ctl;
    public writer2(Controller c)
    {
        ctl=c;
    }
    public void run()
    {
        int d=0;
        while(true&&d<2)
        {
            d++;
            ctl.beforewrite();
            System.out.println("writer2 writing");
            System.out.println("Done writing ");
            ctl.afterwrite();
            System.out.println("after write");
        }
    }
}


"""