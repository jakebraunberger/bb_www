import csv
import sqlite3
import uuid
from os import listdir
import os
import glob
import numpy as np
import time
from datetime import datetime


def parse_time(t):
	t = datetime.fromtimestamp(t)
	l = t.strftime('%H:%M:%S')
	return l

def parse_time_and_day(t):
	t = datetime.fromtimestamp(t)
	l = t.strftime('%m/%d %H:%M:%S')
	return l

def create_connection(db_file):
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

def select_all_from_table(conn, table):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM " + table + " ORDER BY time ASC")
    except:
        cur.execute("SELECT * FROM " + table)
    rows = cur.fetchall()
    
 
    return rows

def select_cols_from_table(conn, table, cols='*'):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    try:
        cur.execute("SELECT %s FROM %s ORDER BY time ASC" % (cols, table))
    except:
        print('Could not get the requested data.')
    rows = cur.fetchall()
 
    return rows

def get_status_desc(val):
	return 'Some description.'



def update_current_charts(txt):
	# two different current charts
	conn = create_connection('../databases/display.db')

	# need to query the columns and time
	# cc3:charge_current,cc4:load_current
	rows = np.array(select_cols_from_table(conn, 'display', 'time,cc3,cc4'))
	
	t = v_format_time(rows[:,0])
	t = t.tolist()
	t = str(t)
	charge_current_data = str(rows[:,1].tolist())
	load_current_data = str(rows[:,2].tolist())

	# need to replace the html text
	txt = txt.replace('__current_time__', t)
	txt = txt.replace('__charge_current_data__', charge_current_data)
	txt = txt.replace('__load_current_data__', load_current_data)

	return txt

def update_errors(txt):
	conn = create_connection('../databases/errorlogs.db')

	# need to query the columns and time
	# cc3:charge_current,cc4:load_current
	rows = np.array(select_cols_from_table(conn, 'errorlogs', '*'))
	t = v_parse_time_and_day(np.array(rows[:,0], dtype=float))
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
	txt = txt.replace('__error_log_data__', html)	
	return txt

def update_voltage_charts(txt):
	# three different current charts
	conn = create_connection('../databases/display.db')

	# need to query the columns and time
	# cc0:battery_voltage, cc1:array_voltage, cc2:load_voltage
	rows = np.array(select_cols_from_table(conn, 'display', 'time,cc0,cc1,cc2'))
	
	t = v_format_time(rows[:,0])
	t = t.tolist()
	t = str(t)
	battery_voltage_data = str(rows[:,1].tolist())
	array_voltage_data = str(rows[:,2].tolist())
	load_voltage_data = str(rows[:,3].tolist())

	# need to replace the html text
	txt = txt.replace('__voltage_time__', t)
	txt = txt.replace('__battery_voltage_data__', battery_voltage_data)
	txt = txt.replace('__array_voltage_data__', array_voltage_data)
	txt = txt.replace('__load_voltage_data__', load_voltage_data)

	return txt

def read_template_and_write_html(data_to_input):
	# get the file to delete after generating the new
	#.  html file
	file = glob.glob('../*html')
	if (len(file) != 0):
		file = file[0]
	fi = open('../template/index.html', 'r')
	template_txt = fi.read()
	fi.close()


	# data to input
	status = str(data_to_input[2])
	battery_voltage = str(data_to_input[3])
	array_voltage = str(data_to_input[4])
	load_voltage = str(data_to_input[5])
	charge_current = str(data_to_input[6])
	load_current = str(data_to_input[7])
	charge = str(data_to_input[8])
	status_desc = str(get_status_desc(status))
	daily_ahc = str(data_to_input[9])
	daily_ahl = str(data_to_input[10])
	charge_kwh = str(data_to_input[11])
	vb_min = str(data_to_input[12])
	charge_state = str(data_to_input[13])
	led_state = str(data_to_input[14])

	load_state = str('')

	mcc_firmware = str(data_to_input[15])
	mcc_sn = str(data_to_input[16])
	drive_rpm = str(data_to_input[18])
	drive_state = str(data_to_input[19])
	drive_v = str(data_to_input[20])
	drive_curr = str(data_to_input[21])
	drive_temp = str(data_to_input[22]*9/5.0+32) #convert to fahrenheit


	# replace the fields that need replacing
	#  [[field1,replace1], [field2, replace2], ...]
	out_text = template_txt
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



	# need to update the voltage charts
	out_text = update_voltage_charts(out_text)

	# need to update the current charts
	out_text = update_current_charts(out_text)

	# need to update the error log
	out_text = update_errors(out_text)






	# write the data to a new html file
	fo_name = str(uuid.uuid4()) # get random filename
	fo = open('../%s.html' % fo_name, 'w')
	fo.write(out_text)
	fo.close()


	# delete the previous html file
	if (file):
		os.remove(file)

	#

file = glob.glob('../*html')
if (len(file) > 1):
	os.remove(file[1])
	file = file[0]

v_format_time = np.vectorize(parse_time)
v_parse_time_and_day = np.vectorize(parse_time_and_day)

# need to get the data
# first open the database
conn = create_connection('../databases/display.db')

# then get the current status, etc.
rows = select_cols_from_table(conn, 'display', '*')
last_row = rows[-1]
# write the data in the template
read_template_and_write_html(last_row)


# 

