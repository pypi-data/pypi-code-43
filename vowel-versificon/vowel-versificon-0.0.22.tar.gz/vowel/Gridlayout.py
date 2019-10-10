Ans="""

import java.awt.*;
class GridLayoutExample extends Frame
{
    GridLayoutExample()
    {
         Button[] button =new Button[12];
         setLayout(new  GridLayout(4,3));
         for(int i=0; i<button.length;i++)
            {
               button[i]=new Button("Button "+(i+i));
               add(button[i]);
            }
     }
}
  class GridLayoutJavaExample
  {
      public static void main(String args[])
      {
          GridLayoutExample frame = new GridLayoutExample();
          frame.setTitle("GridLayout in Java Example");
          frame.setSize(400,150);
          frame.setVisible(true);
      }
  }
"""