Ans="""

    <?php  
    function reverse($number)  
    {  
        $num = (string) $number;  
      
        $revstr = strrev($num);  
      
        $reverse = (int) $revstr;   
         return $reverse;  
    }  
     echo reverse(23456);  
    ?>  

"""