Ans="""

<!DOCTYPE html>
<html>
<body>

<button onclick="goBack()">Go Back</button>

<p>Notice that clicking on the Back button here will not result in any action, because there is no previous URL in the history list.</p>

<script>
function goBack() {
  window.history.back();
}
</script>

</body>
</html>

"""