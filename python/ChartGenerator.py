from Chart import Chart

class ChartGenerator(object):
	def __init__(self):
		self.chart_list = []
	def __init__(self, chart_list):
		self.chart_list = chart_list

	def renderHTML(self, html_text):
		js_txt = ''
		canvas_txt = ''
		
		# for each chart, generate js and canvases
		for chart in self.chart_list:
			js_txt += '\n'
			js_txt += chart.html
			canvas_txt += chart.canvas

		html_text = html_text.replace('__chart_generator_scripts__', js_txt)
		html_text = html_text.replace('__chart_generator_canvases__', canvas_txt)

		
		return html_text


