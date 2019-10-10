Ans="""

<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
  <html>
  <body>
    <h2>Messages Sent</h2>
    <table border="1">
      <tr bgcolor="#9acd32">
        <th>To</th>
        <th>From</th>
      </tr>
      <xsl:for-each select="note">
      <tr>
        <td><xsl:value-of select="to" /></td>
        <td><xsl:value-of select="from" /></td>
      </tr>
      </xsl:for-each>
    </table>
  </body>
  </html>
</xsl:template>
</xsl:stylesheet>



"""