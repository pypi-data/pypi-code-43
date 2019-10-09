Ans="""
import java.awt.*;
class BorderLayoutExample extends Frame
{
    BorderLayoutExample()
    {
         setLayout(new BorderLayout());
         add(new Button("NORTH"),BorderLayout.NORTH);
         add(new Button("SOUTH"),BorderLayout.SOUTH);
         add(new Button("EAST"),BorderLayout.EAST);
         add(new Button("WEST"),BorderLayout.WEST);
         add(new Button("CENTER"),BorderLayout.CENTER);
     }
}
   class BorderLayoutJavaExample
   {
       public static void main(String args[])
      {
          BorderLayoutExample frame = new BorderLayoutExample();
          frame.setTitle("BorderLayout in Java Example");
          frame.setSize(400,150);
          frame.setVisible(true);
      }
  }

"""