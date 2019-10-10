Ans="""

<html>
<body>
<p>Click the button to evaluate/execute Javascript</p>
<button onclick="myFunction()">Try It</button>
<p id="demo"></p>
<script>
function myFunction()
{
var x=10;
var y=20;
var a=eval("x*y")+"<br>";
var b=eval("2+12")+"<br>";
var c=eval("x+17")+"<br>";
var res=a+b+c;
document.getElementById("demo").innerHTML=res;
}
</script>
</body>
</html>


"""