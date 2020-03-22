
class TableGenerator(object):
	def __init__(self):
		self.table_list = []
	def __init__(self, table_list):
		self.table_list = table_list

	def renderHTML(self, html_text):
		for table in self.table_list:
			html_text = html_text.replace(table.html_loc, table.html)
		return html_text