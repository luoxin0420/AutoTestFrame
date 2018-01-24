# To change this template, choose Tools | Templates
# and open the template in the editor.

class HTML:
    def __init__(self, title, filename):
        self.title = title
        self.htmlfile = filename

    def write(self, content):
        #file = codecs.open(self.htmlfile,'a+', 'gbk')
        file = open(self.htmlfile,'a+')
        file.write(content)
        file.close()

    def insertTableHead(self):
        content = '''
<br>
<table border="1" width="1000">
<thead bgcolor="#d0d0d0">
<tr>
<th width="15%">TIME</th>
<th width="15%">TAG</th>
<th>MESSAGE</th>
</tr>
</thead>
<tbody id="wrap" bgcolor="#E0E0E0">'''
        self.write(content)

    def insertTableBody(self, content):
        if content == 'TEST_START':
            content = '<font color="Blue">' + content + '</font>'
        elif content == 'TEST_PASS':
            content = '<font color="#007500" name="pass">' + content + '</font>'
        elif content == 'TEST_FAIL':
            content = '<font color="Red" name="fail">' + content + '</font>'
        elif content == 'TEST_ERROR':
            content = '<font color="Red" name="error">' + content + '</font>'
        elif content == 'TEST_WARN':
            content = '<font color="Yellow" name="warn">' + content + '</font>'
        elif content == 'VP_FAIL':
            content = '<font color="Yellow" name="warn1">' + content + '</font>'
        elif content == 'VP_PASS':
            content = '<font color="Green" name="pass1">' + content + '</font>'
        content = '\n<td>' + str(content)  + '</td>'
        self.write(content)

    def insertTableBody_Time(self, time):
        #self.htmlcontent = self.htmlcontent + '\n<tr>\n<td>' + time + '</td>'
        content = '\n<tr>\n<td>' + time + '</td>'
        self.write(content)

    def finishTableBody(self):
        #self.htmlcontent = self.htmlcontent + '\n</tr>'
        content = '\n</tr>'
        self.write(content)

    def finishHTML(self):
        content = '''
</tbody>
</table>
</body>
</html>'''
        self.write(content)

    def insertResultTable(self, ALL, PASS, FAIL, ERROR, WARN):
        content = '''<td><font color="Black">''' + str(ALL) + '''</font></td>
<td><font color="#007500">''' + str(PASS) + '''</font></td>
<td><font color="Red">''' + str(FAIL) + '''</font></td>
<td><font color="Red">''' + str(ERROR) + '''</font></td>
<td><font color="Yellow">''' + str(WARN) + '''</font></td>
</tr>
</table>
<br>
<table border="1" width="800">
<thead bgcolor="#d0d0d0">
<tr>'''
        self.write(content)


