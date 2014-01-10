import serial,time,sys
from pynmea import nmea
from datetime import datetime
import requests
import json

#####Global Variables######################################
#be sure to declare the variable as 'global var' in the fxn
ser = 0
delta = 2.0
satel = 4
time_old = "0:0:0"
FMT = '%H:%M:%S'
#####FUNCTIONS#############################################
#initialize serial connection 
def init_serial():
	
	COMNUM = int(input("What's yours COM port?[number only] :")) #set you COM port # here
	global ser #must be declared in each fxn used
	ser = serial.Serial()
	ser.baudrate = 57600
	ser.port = COMNUM - 1 #starts at 0, so subtract 1
	#ser.port = '/dev/ttyUSB0' #uncomment for linux
	
	#you must specify a timeout (in seconds) so that the
	# serial port doesn't hang
	ser.timeout = 1
	ser.open() #open the serial port
	global delta
	delta = datetime.strptime('02', '%S') - datetime.strptime('00', '%S')
	
	# print port open or closed
	if ser.isOpen():
		print 'Open: ' + ser.portstr

def convert_data(line):
	if(line[4] == 'G'): # $GPGGA
		if(len(line) > 50):
			#print line
			gpgga = nmea.GPGGA()
			gpgga.parse(line)
			lats = gpgga.latitude
			longs = gpgga.longitude
			time_g = gpgga.timestamp
			num_sat = gpgga.num_sats
			hr = int(time_g[:2]) +7
			time_str = str(hr)+":"+str(int(time_g[2:4]))+":"+str(int(time_g[4:6]))
			
			#convert degrees,decimal minutes to decimal degrees 
			lat1 = (float(lats[2]+lats[3]+lats[4]+lats[5]+lats[6]+lats[7]+lats[8]))/60
			lat = (float(lats[0]+lats[1])+lat1)
			long1 = (float(longs[3]+longs[4]+longs[5]+longs[6]+longs[7]+longs[8]+longs[9]))/60
			longtitude = (float(longs[0]+longs[1]+longs[2])+long1)
			
			#calc position
			pos_y = lat
			pos_x = longtitude #longitude is negaitve			
			#shows that we are reading through this loop
			value =  " longtitude :" , pos_y ,"lattitude : ", pos_x ," time " , time_str, " sat num ",num_sat
			data = dict(lat = pos_x , long=pos_y , sat=num_sat, time =  time_str )
			return data
	
def send_json_data(data_gps):
	url = "http://158.108.16.250:22222/api/track/trackings/"
	#data_gps = {
	    #"lat": "13.842153",
	    #"long": "100.5363",
	    #"car_id": "1"
	#}
	
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	r = requests.post(url, data=json.dumps(data_gps), headers=headers)
	print(r.text)

def time_delta(new):
	time_new = datetime.strptime(new, FMT)
	time_old_str = datetime.strptime(time_old, FMT)
	time_diff = time_new - time_old_str		
	return time_diff.total_seconds()
	
count = 1		
def select_data(data):
	global time_old,  count	
	tdelta = time_delta(data['time'])
	if( tdelta >= 5 and int(data['sat']) >= satel ):
		print (count)
		time_old = data['time']
		count = count+1
		return True		

def process():
	bytes = ser.readline() #reads in bytes followed by a newline
	if(bytes[4] == 'G'):
		values = convert_data(bytes)
			
		if (str(values) != "None"):
			if (select_data(values)):
				print values
				data_json = dict(lat = str(values['lat']) , long=str(values['long']), car_id = str(1))		
				send_json_data(data_json)							
			else:
				print ".",
		else:
			print("can't get data of latitude and longtitude")			
			pass
	
			
#####SETUP################################################
#this is a good spot to run your initializations 
init_serial()

#####MAIN LOOP############################################
#for i in range(100):	
while True:
	process()
	
#hit ctr-c to close python window
