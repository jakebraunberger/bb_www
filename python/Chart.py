
class Chart(object):
	def __init__(self):
		self.html = ''
		self.js_id = ''
		self.data = []
		self.label = ''
		self.time_data = []
		self.canvas = ''
	def __init__(self, js_id='', data='', 
		label='', t='', js_var_name='',
		js_context_name=''):
		self.js_id = js_id
		self.data = data
		self.label = label
		self.time_data = t
		self.js_var_name = js_var_name
		self.js_context_name = js_context_name
		self.html = ''
		self.generateHTML()
		self.generateCanvas()
	

	def generateHTML(self):
		txt = """
				var __js_context_name__ = document.getElementById('__js_id__').getContext('2d');
			    var __js_var_name__ = new Chart(__js_context_name__, {
			        type: 'line',
			        data: {
			        labels: __time__,
			        datasets: [{ 
			            data: __data__,
			            label: "__label__",
			            fill: true
			          }
			        ]
			      },
			      options: {
			      		maintainAspectRatio: false,
			      		responsive: true,
			      },

			    });
			"""
		txt = txt.replace('__time__', self.time_data)
		txt = txt.replace('__data__', self.data)
		txt = txt.replace('__js_id__', self.js_id)
		txt = txt.replace('__js_context_name__', self.js_context_name)
		txt = txt.replace('__js_var_name__', self.js_var_name)
		txt = txt.replace('__label__', self.label)
		self.html = txt
		return

	def generateCanvas(self):
		txt = """
			<canvas id="__js_id__"></canvas>
			"""
		txt = txt.replace('__js_id__', self.js_id)
		self.canvas = txt

