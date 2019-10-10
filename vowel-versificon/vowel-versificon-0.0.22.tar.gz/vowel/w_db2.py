Ans="""


<?php 
 $mysqli = new mysqli("localhost", "root", "", "newdb"); 
  
if ($mysqli == = false) { 
    die("ERROR: Could not connect. ".$mysqli->connect_error); 
} 
  
$sql = "INSERT INTO mytable (first_name, last_name, age) 
              VALUES('ram', 'singh', '25') "; 
    if ($mysqli->query($sql) == = true) 
{ 
    echo "Records inserted successfully."; 
} 
else
{ 
    echo "ERROR: Could not able to execute $sql. "
           .$mysqli->error; 
} 
  
// Close connection 
$mysqli->close(); 
? > 



"""