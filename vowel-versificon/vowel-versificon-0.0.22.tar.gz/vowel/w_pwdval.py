Ans="""

<html>
<head>
</head>
<body>
<script>
function val()
{
var uname=document.myform.uname.value;
var pwd=document.myform.pwd.value;
if(uname=="Test")
{
if(pwd=="Om")
{
alert("Successfully Logged in");
}
else
{
alert("Password Wrong");
}
}
else
{
alert("Username Wrong");
}
}
</script>
<label>Enter your username</label>
<form name="myform" method="POST">
<input type="text" name="uname"></input></br>
<label>Enter your password</label></br>
<input type="text" name="pwd"></input></br>
<button onmouseover="val()" type="submit">
Login
</button>

<p>
</form>
<p id="demo"></p>
</body>
</html>


"""