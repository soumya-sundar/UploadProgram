import logging
import os, cgi
import csv, codecs, cStringIO
import cloudstorage as gcs
import webapp2
import string
from models import *
from os import path
from os.path import exists
from google.appengine.api import app_identity

# Retry can help overcome transient urlfetch or GCS issues, such as timeouts.
my_default_retry_params = gcs.RetryParams(initial_delay=0.2,
                                          max_delay=5.0,
                                          backoff_factor=2,
                                          max_retry_period=15)
gcs.set_default_retry_params(my_default_retry_params)

MAIN_PAGE_HTML = """\
<html>
  <body>
    <form action="/submit" method="post">
	  <h2>Upload Tool </h2>
	  <div>The tool provides a facility to upload data( in csv files) into the GCS cloud storage in a format compatible to the following data models for "Local Amenities Map".</div>
	  <ol>
		<li> Postcode </li>
		<li> Outcode </li>
		<li> General Practitioner (GP) </li>
		<li> Supermarket </li>
		<li> Train Station </li>
		<li> School </li>
	  </ol>
	  <div>Enter a model number : <input type="text" name="model"></div>
	  <br/>
      <div><input type="submit" value="Submit"></div>
    </form>
  </body>
</html>
"""

POSTCODE_HTML = """\
<html>
  <body>
    <form action="/uploadPostcode" method="post">
		<h2>Postcode upload form </h2>
		<div>Enter the file name (with extension): <input type="text" name="filename"></div><br/>
		<div>Enter the column name to be considered for postcode : <input type="text" name="postcode"></div><br/>
		<div>Enter the column name to be considered for latitude : <input type="text" name="latitude"></div><br/>
		<div>Enter the column name to be considered for longitude : <input type="text" name="longitude"></div><br/>
		<div><input type="submit" value="Upload">
			<br/><br/>
			<a href="/">Back to menu</a>
		</div>
    </form>
  </body>
</html>
"""

OUTCODE_HTML = """\
<html>
  <body>
    <form action="/uploadOutcode" method="post">
		<h2>Outcode upload form </h2>
		<div>Enter the file name (with extension) : <input type="text" name="filename"></div><br/>
		<div>Enter the column name to be considered for outcode : <input type="text" name="outcode"></div><br/>
		<div>Enter the column name to be considered for latitude : <input type="text" name="latitude"></div><br/>
		<div>Enter the column name to be considered for longitude : <input type="text" name="longitude"></div><br/>
		<div><input type="submit" value="Upload">
			<br/><br/>
			<a href="/">Back to menu</a>
		</div>
    </form>
  </body>
</html>
"""

TRAIN_STATION_HTML = """\
<html>
  <body>
    <form action="/uploadTrainStation" method="post">
		<h2>Train station upload form </h2>
		<div>Enter the file name (with extension): <input type="text" name="filename"></div><br/>
		<div>Enter the column name to be considered for Train station name : <input type="text" name="name"></div><br/>
		<div>Enter the column name to be considered for latitude : <input type="text" name="latitude"></div><br/>
		<div>Enter the column name to be considered for longitude : <input type="text" name="longitude"></div><br/>
		<div><input type="submit" value="Upload">
			<br/><br/>
			<a href="/">Back to menu</a>
		</div>
    </form>
  </body>
</html>
"""

GP_HTML = """\
<html>
  <body>
    <form action="/uploadData" method="post">
		<h2>General Practioner(GP) upload form </h2>
		<div>Enter the file name (with extension): <input type="text" name="filename"></div><br/>
		<div>Enter the column name to be considered for GP name : <input type="text" name="name"><div><br/>
		<div>Enter the column names (separated by comma) to be considered for address : <textarea name="address" rows="2" cols="60"></textarea><div><br/>
		<div>Enter the column name to be considered for postcode : <input type="text" name="postcode"></div><br/>
		<div>Enter the column name to be considered for latitude : <input type="text" name="latitude"></div><br/>
		<div>Enter the column name to be considered for longitude : <input type="text" name="longitude"></div><br/>
		<div><input type="submit" value="Upload">
			<br/><br/>
			<a href="/">Back to menu</a>
		</div>
    </form>
  </body>
</html>
"""

SUPERMARKET_HTML = """\
<html>
  <body>
    <form action="/uploadData" method="post">
		<h2>Supermarket upload form </h2>
		<div>Enter the file name (with extension): <input type="text" name="filename"></div><br/>
		<div>Enter the column name to be considered for Supermarket name : <input type="text" name="name"></div><br/>
		<div>Enter the column names (separated by comma) to be considered for address : <textarea name="address" rows="2" cols="60"></textarea></div><br/>
		<div>Enter the column name to be considered for postcode : <input type="text" name="postcode"></div><br/>
		<div>Enter the column name to be considered for latitude : <input type="text" name="latitude"></div><br/>
		<div>Enter the column name to be considered for longitude : <input type="text" name="longitude"></div><br/>
		<div><input type="submit" value="Upload">
			<br/><br/>
			<a href="/">Back to menu</a>
		</div>
    </form>
  </body>
</html>
"""

SCHOOL_HTML = """\
<html>
  <body>
    <form action="/uploadData" method="post">
		<h2>School upload form </h2>
		<div>Enter the file name (with extension): <input type="text" name="filename"></div><br/>
		<div>Enter the column name to be considered for School name : <input type="text" name="name"></div><br/>
		<div>Enter the column names (separated by comma) to be considered for address : <textarea name="address" rows="2" cols="60"></textarea></div><br/>
		<div>Enter the column name to be considered for postcode : <input type="text" name="postcode"></div><br/>
		<div>Enter the column name to be considered for latitude : <input type="text" name="latitude"></div><br/>
		<div>Enter the column name to be considered for longitude : <input type="text" name="longitude"></div><br/>
		<div><input type="submit" value="Upload">
			<br/><br/>
			<a href="/">Back to menu</a>
		</div>
    </form>
  </body>
</html>
"""

class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.write(MAIN_PAGE_HTML)
		
class AdditionalDetails(webapp2.RequestHandler):
	def post(self):
		modelNumber = cgi.escape(self.request.get('model'))
		if modelNumber == '1':
			self.response.write(POSTCODE_HTML)
		elif modelNumber == '2':
			self.response.write(OUTCODE_HTML)
		elif modelNumber == '3':
			self.response.write(GP_HTML)
		elif modelNumber == '4':
			self.response.write(SUPERMARKET_HTML)
		elif modelNumber == '5':
			self.response.write(TRAIN_STATION_HTML)
		elif modelNumber == '6':
			self.response.write(SCHOOL_HTML)
		else:
			self.response.write("Model number is not provided")

def CheckColumnExists(filename, columnName):
	found = False
	f=open(filename)
	reader=csv.reader(f)
	for row in reader:  
		for col in row:
			if col == columnName:
				found = True
		break
	return found
	
class UploadPostcode(webapp2.RequestHandler):
	def post(self):
		postcode_flag = False
		latitude_flag = False
		longitude_flag = False
		filename  = cgi.escape(self.request.get('filename'))
		if filename == "":
			self.response.write("File name is required" + '<br/><br/>')
		elif os.path.exists(filename) == True :
			postcode = cgi.escape(self.request.get('postcode'))
			if postcode == "":
				self.response.write("Postcode column name is required" + '<br/><br/>')
			else:
				if (CheckColumnExists(filename, postcode) == False):
					self.response.write("Postcode column name doesn't exist in the file" + '<br/><br/>')
				else:
					postcode_flag = True
			latitude = cgi.escape(self.request.get('latitude'))
			if latitude == "":
				self.response.write("Latitude column name is required" + '<br/><br/>')
			else:
				if (CheckColumnExists(filename, latitude) == False):
					self.response.write("Latitude column name doesn't exist in the file" + '<br/><br/>')
				else:
					latitude_flag = True
			longitude = cgi.escape(self.request.get('longitude'))	
			if longitude == "":
				self.response.write("Longitude column name is required" + '<br/><br/>')
			else:
				if (CheckColumnExists(filename, longitude) == False):
					self.response.write("Longitude column name doesn't exist in the file" + '<br/><br/>')
				else:
					longitude_flag = True
		else:
			self.response.write("File name doesn't exist in the app's directory" + '<br/><br/>')
			
		if (postcode_flag == True and latitude_flag == True and longitude_flag == True):
			bucket_name = os.environ.get('upload-gcs-data.appspot.com', app_identity.get_default_gcs_bucket_name())
			self.response.headers['Content-Type'] = 'text/plain'
			self.response.write('Demo GCS Application running from Version: '
                        + os.environ['CURRENT_VERSION_ID'] + '\n')
			self.response.write('Using bucket name: ' + bucket_name + '\n\n')
			bucket = '/' + bucket_name
			gcs_filename = bucket + '/' + filename
			self.tmp_filenames_to_clean_up = []
		
			try:
				self.response.write('Creating file %s\n' % gcs_filename)
				write_retry_params = gcs.RetryParams(backoff_factor=1.1)
				gcs_file = gcs.open(gcs_filename,
							'w',
							content_type='text/csv',
							retry_params=write_retry_params)
				f = open(filename)
				reader = csv.DictReader(f)
				fieldnames = ['postcode', 'latitude', 'longitude']
				writer = csv.DictWriter(gcs_file, fieldnames=fieldnames)
				writer.writeheader()
				for row in reader:  
					writer.writerow({'postcode': row[postcode], 'latitude': row[latitude], 'longitude': row[longitude]})
				gcs_file.close()
				self.tmp_filenames_to_clean_up.append(gcs_filename)
			
				self.response.write('\n\n')
				self.response.write(gcs_filename + " is successfully created with data in your app's default bucket")

			except Exception, e:  # pylint: disable=broad-except
				logging.exception(e)
				self.response.write('\n\nThere was an error running the program! '
								'Please check the logs for more details.\n')
								
class UploadOutcode(webapp2.RequestHandler):
	def post(self):
		outcode_flag = False
		latitude_flag = False
		longitude_flag = False
		filename  = cgi.escape(self.request.get('filename'))
		if filename == "":
			self.response.write("filename is required" + '<br/><br/>')
		elif os.path.exists(filename) == True :
			outcode = cgi.escape(self.request.get('outcode'))
			if outcode == "":
				self.response.write("Outcode column name is required" + '<br/><br/>')
			else:
				if (CheckColumnExists(filename, outcode) == False):
					self.response.write("Outcode column name doesn't exist in the file" + '<br/><br/>')
				else:
					outcode_flag = True
			latitude = cgi.escape(self.request.get('latitude'))
			if latitude == "":
				self.response.write("Latitude column name is required" + '<br/><br/>')
			else:
				if (CheckColumnExists(filename, latitude) == False):
					self.response.write("Latitude column name doesn't exist in the file" + '<br/><br/>')
				else:
					latitude_flag = True
			longitude = cgi.escape(self.request.get('longitude'))	
			if longitude == "":
				self.response.write("Longitude column name is required" + '<br/><br/>')
			else:
				if (CheckColumnExists(filename, longitude) == False):
					self.response.write("Longitude column name doesn't exist in the file" + '<br/><br/>')
				else:
					longitude_flag = True
		else:
			self.response.write("File name doesn't exist in the app's directory" + '<br/><br/>')
				
		if (outcode_flag == True and latitude_flag == True and longitude_flag == True):
			bucket_name = os.environ.get('upload-gcs-data.appspot.com', app_identity.get_default_gcs_bucket_name())
			self.response.headers['Content-Type'] = 'text/plain'
			self.response.write('Demo GCS Application running from Version: '
                        + os.environ['CURRENT_VERSION_ID'] + '\n')
			self.response.write('Using bucket name: ' + bucket_name + '\n\n')
			bucket = '/' + bucket_name
			gcs_filename = bucket + '/' + filename
			self.tmp_filenames_to_clean_up = []
		
			try:
				self.response.write('Creating file %s\n' % gcs_filename)
				write_retry_params = gcs.RetryParams(backoff_factor=1.1)
				gcs_file = gcs.open(gcs_filename,
							'w',
							content_type='text/csv',
							retry_params=write_retry_params)
				f = open(filename)
				reader = csv.DictReader(f)
				fieldnames = ['outcode', 'latitude', 'longitude']
				writer = csv.DictWriter(gcs_file, fieldnames=fieldnames)
				writer.writeheader()
				for row in reader:  
					writer.writerow({'outcode': row[outcode], 'latitude': row[latitude], 'longitude': row[longitude]})
				gcs_file.close()
				self.tmp_filenames_to_clean_up.append(gcs_filename)
			
				self.response.write('\n\n')
				self.response.write(gcs_filename + " is successfully created with data in your app's default bucket")

			except Exception, e:  # pylint: disable=broad-except
				logging.exception(e)
				self.response.write('\n\nThere was an error running the program! '
								'Please check the logs for more details.\n')

class UploadTrainStation(webapp2.RequestHandler):
	def post(self):
		name_flag = False
		latitude_flag = False
		longitude_flag = False
		filename  = cgi.escape(self.request.get('filename'))
		if filename == "":
			self.response.write("Filename is required" + '<br/><br/>')
		elif os.path.exists(filename) == True :
			name = cgi.escape(self.request.get('name'))
			if name == "":
				self.response.write("Name column name is required" + '<br/><br/>')
			else:
				if (CheckColumnExists(filename, name) == False):
					self.response.write("Name column name doesn't exist in the file" + '<br/><br/>')
				else:
					name_flag = True
			latitude = cgi.escape(self.request.get('latitude'))
			if latitude == "":
				self.response.write("Latitude column name is required" + '<br/><br/>')
			else:
				if (CheckColumnExists(filename, latitude) == False):
					self.response.write("Latitude column name doesn't exist in the file" + '<br/><br/>')
				else:
					latitude_flag = True
			longitude = cgi.escape(self.request.get('longitude'))	
			if longitude == "":
				self.response.write("Longitude column name is required" + '<br/><br/>')
			else:
				if (CheckColumnExists(filename, longitude) == False):
					self.response.write("Longitude column name doesn't exist in the file" + '<br/><br/>')
				else:
					longitude_flag = True
		else:
			self.response.write("File name doesn't exist in the app's directory" + '<br/><br/>')
				
		if (name_flag == True and latitude_flag == True and longitude_flag == True):
			bucket_name = os.environ.get('upload-gcs-data.appspot.com', app_identity.get_default_gcs_bucket_name())
			self.response.headers['Content-Type'] = 'text/plain'
			self.response.write('Demo GCS Application running from Version: '
                        + os.environ['CURRENT_VERSION_ID'] + '\n')
			self.response.write('Using bucket name: ' + bucket_name + '\n\n')
			bucket = '/' + bucket_name
			gcs_filename = bucket + '/' + filename
			self.tmp_filenames_to_clean_up = []
		
			try:
				self.response.write('Creating file %s\n' % gcs_filename)
				write_retry_params = gcs.RetryParams(backoff_factor=1.1)
				gcs_file = gcs.open(gcs_filename,
							'w',
							content_type='text/csv',
							retry_params=write_retry_params)
				f = open(filename)
				reader = csv.DictReader(f)
				fieldnames = ['name', 'latitude', 'longitude']
				writer = csv.DictWriter(gcs_file, fieldnames=fieldnames)
				writer.writeheader()
				for row in reader:  
					writer.writerow({'name': row[name], 'latitude': row[latitude], 'longitude': row[longitude]})
				gcs_file.close()
				self.tmp_filenames_to_clean_up.append(gcs_filename)
			
				self.response.write('\n\n')
				self.response.write(gcs_filename + " is successfully created with data in your app's default bucket")

			except Exception, e:  # pylint: disable=broad-except
				logging.exception(e)
				self.response.write('\n\nThere was an error running the program! '
									'Please check the logs for more details.\n')
									
class UploadData(webapp2.RequestHandler):
	def post(self):
		name_flag = False
		address_flag = False
		postcode_flag = False
		latitude_flag = False
		longitude_flag = False
		filename  = cgi.escape(self.request.get('filename'))
		if filename == "":
			self.response.write("Filename is required" + '<br/><br/>')
		elif os.path.exists(filename) == True :
			name = cgi.escape(self.request.get('name'))
			if name == "":
				self.response.write("Name column name is required" + '<br/><br/>')
			else:
				if (CheckColumnExists(filename, name) == False):
					self.response.write("Name column name doesn't exist in the file" + '<br/><br/>')
				else:
					name_flag = True
			address = cgi.escape(self.request.get('address'))
			if address == "":
				self.response.write("Address column name is required" + '<br/><br/>')
			else:
				address_list = address.split(",")
				for i in range(len(address_list)):	
					logging.info(address_list[i])
					if (CheckColumnExists(filename, address_list[i].strip()) == False):
						address_flag = False
						self.response.write("Address column name(s) doesn't exist in the file" + '<br/><br/>')
						break
					else:
						address_flag = True
			postcode = cgi.escape(self.request.get('postcode'))
			if postcode == "":
				self.response.write("Postcode column name is required" + '<br/><br/>')
			else:
				if (CheckColumnExists(filename, postcode) == False):
					self.response.write("Postcode column name doesn't exist in the file" + '<br/><br/>')
				else:
					postcode_flag = True						
			latitude = cgi.escape(self.request.get('latitude'))
			if latitude == "":
				self.response.write("Latitude column name is required" + '<br/><br/>')
			else:
				if (CheckColumnExists(filename, latitude) == False):
					self.response.write("Latitude column name doesn't exist in the file" + '<br/><br/>')
				else:
					latitude_flag = True
			longitude = cgi.escape(self.request.get('longitude'))	
			if longitude == "":
				self.response.write("Longitude column name is required" + '<br/><br/>')
			else:
				if (CheckColumnExists(filename, longitude) == False):
					self.response.write("Longitude column name doesn't exist in the file" + '<br/><br/>')
				else:
					longitude_flag = True
		else:
			self.response.write("File name doesn't exist in the app's directory" + '<br/><br/>')
				
		if (name_flag == True and address_flag == True and postcode_flag == True and latitude_flag == True and longitude_flag == True):
			bucket_name = os.environ.get('upload-gcs-data.appspot.com', app_identity.get_default_gcs_bucket_name())
			self.response.headers['Content-Type'] = 'text/plain'
			self.response.write('Demo GCS Application running from Version: '
                        + os.environ['CURRENT_VERSION_ID'] + '\n')
			self.response.write('Using bucket name: ' + bucket_name + '\n\n')
			bucket = '/' + bucket_name
			gcs_filename = bucket + '/' + filename
			self.tmp_filenames_to_clean_up = []
		
			try:
				self.response.write('Creating file %s\n' % gcs_filename)
				write_retry_params = gcs.RetryParams(backoff_factor=1.1)
				gcs_file = gcs.open(gcs_filename,
							'w',
							content_type='text/csv',
							retry_params=write_retry_params)
				f = open(filename)
				reader = csv.DictReader(f)
				fieldnames = ['name', 'address', 'postcode', 'latitude', 'longitude']
				writer = csv.DictWriter(gcs_file, fieldnames=fieldnames)
				writer.writeheader()
				for row in reader:  
					final_address = ""
					for i in range(len(address_list)):
						final_address += row[address_list[i].strip()] + ", "
					writer.writerow({'name': row[name], 'address': final_address, 'postcode': row[postcode], 'latitude': row[latitude], 'longitude': row[longitude]})
				gcs_file.close()
				self.tmp_filenames_to_clean_up.append(gcs_filename)
			
				self.response.write('\n\n')
				self.response.write(gcs_filename + " is successfully created with data in your app's default bucket")

			except Exception, e: 
				logging.exception(e)
				self.response.write('\n\nThere was an error running the program! '
									'Please check the logs for more details.\n')
									
app = webapp2.WSGIApplication([
('/', MainPage),
('/submit', AdditionalDetails),
('/uploadPostcode', UploadPostcode),
('/uploadOutcode', UploadOutcode),
('/uploadTrainStation', UploadTrainStation),
('/uploadData', UploadData)
], debug=True)