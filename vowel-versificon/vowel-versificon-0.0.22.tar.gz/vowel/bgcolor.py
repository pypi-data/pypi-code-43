Ans="""import java.applet.*;
import java.awt.event.*;
import java.awt.*;
public class NewApp extends Applet implements ActionListener{
    Button b1,b2,b3;
    public void init()
    {
    b1=new Button("Red");
    b2=new Button("Blue");
    b3=new Button("Green");
    b1.addActionListener(this);
    b2.addActionListener(this);
    b3.addActionListener(this);
    add(b1);
    add(b2);
    add(b3);
    }
    public void actionPerformed(ActionEvent e)
    {
    if(e.getSource()==b1)
        setBackground(Color.red);
    else if(e.getSource()==b2)
        setBackground(Color.blue);
    else
        setBackground(Color.green);
    
    }
    public void paint(Graphics g)
    {
    showStatus("Om");
    }

    
}"""
