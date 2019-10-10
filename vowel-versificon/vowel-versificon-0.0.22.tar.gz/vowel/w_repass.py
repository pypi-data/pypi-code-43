Ans="""

<html>
<body>
<script>
function retype_pass()
{
var first_pwd=document.ValidatePassword.password.value;
var second_pwd=document.ValidatePassword.password2.value;
if(first_pwd==second_pwd)
{
return true;
}
else
{
alert("Password must be same");
return false;
}
}
</script>
<form name="ValidatePassword" method="POST">
Password:<input type="text" name="password"><br><br>
Retype Password:<input type="text" name="password2"><br><br>
<button type="submit" onclick="retype_pass()">Check</button>
</form>
</body>
</html>


"""