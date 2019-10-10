Ans="""

<html>
<body>
<form action="welcome.php" method="post">
Name:<input type="text" name="name"/><br>
<input type="submit" value="visit"/>
</form>
</body>
</html>

<?php
$ame=$_POST["name"];
echo "welcome $name";
?>

"""