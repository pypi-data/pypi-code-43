Ans="""

<!--Display prime no in given range-->
<html>
<head>
<script language="javascript">
function calprimenumber()
{
var beginnum=parseInt(document.numbers.firstnum.value);
var endnum=parseInt(document.numbers.secondnum.value);
var primenumbers=new Array();
var ctr=beginnum;
while(ctr<=endnum)
{
if(isprime(ctr)==true)
{
primenumbers[primenumbers.length]=ctr;
}
ctr=ctr+1;
}
if(primenumbers.length==0)
{
document.getElementById("output_content").innerHTML="There were no prime numbers within the range";
}
else
{
outputprimenumbers(primenumbers);
}
}
function isprime(num)
{
var flag=true;
for(var i=2;i<=Math.ceil(num/2);i++)
{
if((num%i)==0)
{
flag=false;
break;
}
}
return flag;
}
function outputprimenumbers(primes)
{
var html="<h2>Prime number</h2>";
for(i=0;i<primes.length;i++)
{
html+=primes[i]+"<br>";
}
document.getElementById("output_content").innerHTML=html;
}
</script>
</head>
<body>
<form name="numbers">
beginning number<input type="text" name="firstnum"/>
ending number<input type="text" name="secondnum"/>
<input type="button" value="Find prime numbers" onclick="calprimenumber()">
</form>
<div id="output_content">
</div>
</body>
</html>


"""