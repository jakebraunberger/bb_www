import csv
import sqlite3
import uuid
from os import listdir
import os
import glob
import numpy as np
import time
from datetime import datetime
from Chart import Chart
from ChartGenerator import ChartGenerator

class IndexHTML(object):
	

	def __init__(self,
	 html_template='/home/ee/bb_www/template/index.html'):
		self.html_template = ''
		self.html_generators = []
		self.html = ''
		self.v_parse_time = np.vectorize(self.parse_time)
		self.v_parse_time_and_day = np.vectorize(self.parse_time_and_day)
		self.mcc_data = {}
		self.cc_data = {}
		self.info_data = []

		# read the template
		try:
			fi = open(html_template,'r')
			self.html_template = fi.read()
			fi.close()
		except:
			self.html_template = ''

		# gather the data
		self.mcc_data = self.get_mcc_data()
		self.cc_data = self.get_cc_data()
		self.info_data = self.get_info_data()
		self.prev_html_file = self.get_prev_html_file()

		# set the html generators
		self.set_html_generators()

		# copy the template to the text to write
		self.html = self.html_template


		# update the error
		self.update_errors()
		# update the info
		self.update_info_html()
		# update the html via generators
		self.update_generate_html()


		# write the html file
		self.write_html()
		

	def update_generate_html(self):
		# generate the html for the class generators
		for gen in self.html_generators:
			self.html = gen.renderHTML(self.html)

		# generate the errors
		self.html = self.update_errors(self.html)

	def parse_time(self, t):
		t = datetime.fromtimestamp(t)
		l = t.strftime('%H:%M:%S')
		return l

	def parse_time_and_day(self, t):
		t = datetime.fromtimestamp(t)
		l = t.strftime('%m/%d %H:%M:%S')
		return l

	def create_connection(self, db_file):
		""" create a database connection to the SQLite database
			specified by the db_file
		:param db_file: database file
		:return: Connection object or None
		"""
		conn = None
		try:
			conn = sqlite3.connect(db_file)
		except:
			print('Could not open the database')
			return None       
	 
		return conn

	def select_all_from_table(self, conn, table):
		"""
		Query all rows in the tasks table
		:param conn: the Connection object
		:return:
		"""
		cur = conn.cursor()
		try:
			cur.execute("SELECT * FROM " + table + " ORDER BY time DESC")
		except:
			cur.execute("SELECT * FROM " + table)
		rows = cur.fetchall()
		
	 
		return rows

	def select_cols_from_table(self, conn, table, cols='*', limit=-1):
		"""
		Query all rows in the tasks table
		:param conn: the Connection object
		:return:
		"""
		cur = conn.cursor()
		try:
			if (limit == -1):
				cur.execute("SELECT %s FROM %s ORDER BY time DESC" % (cols, table))
			else:
				cur.execute("SELECT %s FROM %s ORDER BY time DESC LIMIT %d" % (cols, table, limit))
		except:
			print('Could not get the requested data.')
		rows = cur.fetchall()
	 
		return rows

	def get_status_desc(self, val):
		return 'Some description.'




	def update_errors(self):
		conn = self.create_connection('/home/ee/bb_www/databases/errorlogs.db')

		# need to query the columns and time
		# cc3:charge_current,cc4:load_current
		rows = np.array(self.select_cols_from_table(conn, 'errorlogs', '*'))
		t = self.v_parse_time_and_day(np.array(rows[:,0], dtype=float))
		t = t.tolist()
		# time = time

		# for each row in rows
		#. html
		html = ''
		i = 0
		for row in rows:
			html += '<tr>'
			html += '<td>' + str(t[i]) + '</td>'
			html += '<td>' + str(row[1]) + '</td>'
			html += '<td>' + str(row[2]) + '</td>'
			html += '</tr>'
			i += 1
		self.html = self.html.replace('__error_log_data__', html)	


	def get_info_data(self):
		conn = self.create_connection('/home/ee/bb_www/databases/display.db')

		# then get the current status, etc.
		rows = self.select_cols_from_table(conn, 'display', '*')
		last_row = np.array(rows[-1])
		self.info_data = last_row

	def get_mcc_data(self, poles=16):
		# three different current charts
		conn = self.create_connection('/home/ee/bb_www/databases/mccregisters.db')

		# need to query the columns and time
		# cc0:battery_voltage, cc1:array_voltage, cc2:load_voltage
		rows = np.array(self.select_cols_from_table(conn, 'mccreg', 'time,reg3', limit=100))
		

		t = self.v_parse_time(rows[:,0])
		t = t.tolist()
		t.reverse()
		t = str(t)


		try:
			rows[:,1] *= 120.0 / (256.0 * poles)
		except:
			pass

		
		# voltages
		rpm = rows[:,1]
		rpm = rpm.tolist()
		rpm.reverse()
		


		rpm_data = str(rpm).replace('None', '-1.0')

		data = {'t':t,
			'rpm': rpm_data,
		 	}
		
		return data 


	def get_cc_data(self):
		# three different current charts
		conn = self.create_connection('/home/ee/bb_www/databases/ccregisters.db')

		# need to query the columns and time
		# cc0:battery_voltage, cc1:array_voltage, cc2:load_voltage
		rows = np.array(self.select_cols_from_table(conn, 'ccreg', 'time,reg9,reg10,reg11,reg12,reg13', limit=100))
		
		t = self.v_parse_time(rows[:,0])
		t = t.tolist()
		t.reverse()
		t = str(t)

		try:
			rows[:,1] *= 100*2**-15
		except:
			pass

		try:
			rows[:,2] *= 100*2**-15
		except:
			pass

		try:
			rows[:,3] *= 100*2**-15
		except:
			pass
		try:
			ccd = rows[:,4]*79.16*2**-15
		except:
			ccd = rows[:,4]

		try:
			lcd = rows[:,5]*79.16*2**-15
		except:
			lcd = rows[:,5]

		# voltages
		bvd = rows[:,1]
		bvd = bvd.tolist()
		bvd.reverse()
		avd = rows[:,2]
		avd = avd.tolist()
		avd.reverse()
		lvd = rows[:,3]
		lvd = lvd.tolist()
		lvd.reverse()
		# currents
		ccd = ccd.tolist()
		ccd.reverse()
		lcd = lcd.tolist()
		lcd.reverse()

		charge_current_data = str(ccd).replace('None', '-1.0')
		load_current_data = str(lcd).replace('None', '-1.0')
		battery_voltage_data = str(bvd).replace('None', '-1.0')
		array_voltage_data = str(avd).replace('None', '-1.0')
		load_voltage_data = str(lvd).replace('None', '-1.0')

		data = {'t':t,
			'battery_voltage_data':battery_voltage_data,
		 	'array_voltage_data':array_voltage_data,
		 	'load_voltage_data':load_voltage_data,
		 	'charge_current_data':charge_current_data,
		 	'load_current_data':load_current_data}
		
		return data 

	def get_template(self):
		pass

	def get_prev_html_file(self):
		file = glob.glob('/home/ee/bb_www/*html')
		if (len(file) != 0):
			self.prev_html_file = file[0]
		else:
			self.prev_html_file = None

	def set_html_generators(self):
		# need to update the voltage charts
		cc_data = self.cc_data
		bvc_data = self.cc_data['battery_voltage_data']
		v_t = self.cc_data['t']
		avc_data = self.cc_data['array_voltage_data']

		battery_voltage_chart = Chart(
			js_id='bvc',
			data=cc_data['battery_voltage_data'],
			label='Battery Voltage',
			t=v_t,
			js_var_name='bvcChart',
			js_context_name='ctxBVC',
			)


		array_voltage_chart = Chart(
			js_id='avc',
			data=avc_data,
			label='Array Voltage',
			t=v_t,
			js_var_name='avcChart',
			js_context_name='ctxAVC',
			)

		load_current_chart = Chart(
			js_id='lcc',
			data=cc_data['load_current_data'],
			label='Load Current',
			t=v_t,
			js_var_name='lccChart',
			js_context_name='ctxLCC',
			)

		

		rpm_chart = Chart(
			js_id='rpmc',
			data=self.mcc_data['rpm'],
			label='RPMs',
			t=self.mcc_data['t'],
			js_var_name='rpmChart',
			js_context_name='ctxRPM',
			)


		cg = ChartGenerator([array_voltage_chart,
			battery_voltage_chart,
			load_current_chart,
			rpm_chart])

		self.html_generators.append(cg)

	def update_info_html(self):

		# round to 1 decimal place
		self.info_data = self.info_data.round(decimals=1)

		# data to input
		status = str(self.info_data[2])
		battery_voltage = str(self.info_data[3])
		array_voltage = str(self.info_data[4])
		load_voltage = str(self.info_data[5])
		charge_current = str(self.info_data[6])
		load_current = str(self.info_data[7])
		charge = str(self.info_data[8])
		status_desc = str(get_status_desc(status))
		daily_ahc = str(self.info_data[9])
		daily_ahl = str(self.info_data[10])
		charge_kwh = str(self.info_data[11])
		vb_min = str(self.info_data[12])
		charge_state = str(self.info_data[13])
		led_state = str(self.info_data[14])
		load_state = str('')
		mcc_firmware = str(self.info_data[15])
		mcc_sn = str(self.info_data[16])
		drive_rpm = str(self.info_data[18])
		drive_state = str(self.info_data[19])
		drive_v = str(self.info_data[20])
		drive_curr = str(self.info_data[21])
		drive_temp = str(self.info_data[22]*9/5.0+32) #convert to fahrenheit


		# replace the fields that need replacing
		#  [[field1,replace1], [field2, replace2], ...]
		out_text = self.html
		search_and_replace = [
							['__status__', status],
							['__battery_voltage__', battery_voltage],
							['__array_voltage__', array_voltage],
							['__load_voltage__', load_voltage],
							['__charge_current__', charge_current],
							['__load_current__', load_current],
							['__charge__', charge],
							['__status_table_value__', status],
							['__daily_ahc__', daily_ahc],
							['__daily_ahl__', daily_ahl],
							['__charge_kwh__', charge_kwh],
							['__daily_vb_min__', vb_min],
							['__charge_state__', charge_state],
							['__cc_led_state__', led_state],
							['__mcc_sn__', mcc_sn],
							['__mcc_firmware__', mcc_firmware],
							['__drive_rpm__', drive_rpm],
							['__drive_status__', drive_state],
							['__drive_v__', drive_v],
							['__drive_current__', drive_curr],
							['__drive_temp__', drive_temp]
							]

		for to_replace_list in search_and_replace:
			out_text = out_text.replace(to_replace_list[0], to_replace_list[1])

		self.html = out_text

		




		






	def write_html(self):
		# write the data to a new html file
		fo_name = str(uuid.uuid4()) # get random filename
		fo = open('/home/ee/bb_www/%s.html' % fo_name, 'w')
		fo.write(self.html)
		fo.close()


		# delete the previous html file
		if (self.prev_html_file):
			os.remove(self.prev_html_file)


# if there's more than 1 html file in the
# bb_www directory, remove one of them
file = glob.glob('/home/ee/bb_www/*html')
if (len(file) > 1):
	os.remove(file[1])


i = IndexHTML()
