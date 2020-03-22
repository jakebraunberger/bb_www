class Table(object):

	def __init__(self):
		self.html_id = ''
		self.column_names = []
		self.data = []
		self.html = ''
		self.html_loc = ''
	def __init__(self, html_id='', column_names=[],
		data=[],
		html_loc=''):
		self.html_id = html_id
		self.column_names = column_names
		self.data = data
		self.html = ''
		self.html_loc = html_loc
		self.generateHTML()

	def generateHTML(self):
		txt = """
			<table id="__html_id__" class="table">
			<tr>
			__columns__
			</tr>
			__rows__
			</table>
			"""
		columns = ''

		# generate column names
		for column_name in self.column_names:
			columns += '\n'
			columns += '<th>' + column_name + '</th>'

		# replace the __columns__ in txt
		txt = txt.replace('__columns__', columns)


		# generate the row data
		rows = ''
		for row in data:
			rows += '\n<tr>'
			for col in row:
				rows += '<td>' + col + '</td>\n'
			rows += '</tr>'

		txt = txt.replace('__rows__', rows)
		self.html = txt