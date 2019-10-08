Ans="""

public class FirstThread implements Runnable
{
 
  //This method will be executed when this thread is executed
  public void run()
  {
 
    //Looping from 1 to 10 to display numbers from 1 to 10
    for ( int i=1; i<=10; i++)
    {
        //Displaying the numbers from this thread
        System.out.println( "Messag from First Thread : " +i);
 
       
        try
        {
           Thread.sleep (1000);
        }
        catch (InterruptedException interruptedException)
        {
           
            System.out.println( "First Thread is interrupted when it is sleeping" +interruptedException);
        }
    }
  }
}

public class SecondThread implements Runnable
{
 
   //This method will be executed when this thread is executed
   public void run()
   {
 
      //Looping from 1 to 10 to display numbers from 1 to 10
      for ( int i=1; i<=10; i++)
      {
         System.out.println( "Messag from Second Thread : " +i);
 
        
         try
         {
             Thread.sleep(1000);
         }
         catch (InterruptedException interruptedException)
         {
            
             System.out.println( "Second Thread is interrupted when it is sleeping" +interruptedException);
         }
      }
    }
}

public class ThreadDemo
{
     public static void main(String args[])
     {
        //Creating an object of the first thread
        FirstThread   firstThread = new FirstThread();
 
        //Creating an object of the Second thread
        SecondThread   secondThread = new SecondThread();
 
        //Starting the first thread
        Thread thread1 = new Thread(firstThread);
        thread1.start();
 
        //Starting the second thread
        Thread thread2 = new Thread(secondThread);
        thread2.start();
     }
}


"""