Ans="""

import java.io.*;
public class Copyfile{
    public static void main(String agrs[]) throws IOException{
        FileInputStream in=null;
        FileOutputStream out=null;
        try{
            in=new FileInputStream("Input.txt");
            out=new FileOutputStream("Output.txt");
            int c;
            while((c=in.read())!=-1){
                out.write(c);
        }}finally{
            if(in!=null){
                in.close();
            }
            if(out!=null){
                out.close();
            }
        }
    }
}

"""