#import os
#try:
#  from SimpleHTTPServer import SimpleHTTPRequestHandler as Handler
#  from SocketServer import TCPServer as Server
#except ImportError:
#  from http.server import SimpleHTTPRequestHandler as Handler
#  from http.server import HTTPServer as Server
#
# Read port selected by the cloud for our application
#PORT = int(os.getenv('PORT', 8000))
# Change current directory to avoid exposure of control files
#os.chdir('static')
#
#httpd = Server(("", PORT), Handler)
#try:
#  print("Start serving at port %i" % PORT)
#  httpd.serve_forever()
#except KeyboardInterrupt:
#  pass
#httpd.server_close()

import os,MySQLdb
import swiftclient
import keystoneclient
import pyDes
from flask import Flask, request, render_template
global u_id

app = Flask(__name__)
k = pyDes.des(b"AVENGERS", pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
#IBM bluemix app Environment variables of the app
auth_url = "https://identity.open.softlayer.com/v3"
password = "*****"
project_id = "b67b8a1adc4147868ed7fbe0e559e8fa"
user_id = "******************"
region_name = 'dallas'
conn = 	swiftclient.Connection (key=password, 
        authurl=auth_url,
        auth_version='3',
        os_options={"project_id" : project_id,
                    "user_id" : user_id,
                    "region_name" : region_name})

db=MySQLdb.connect(host="us-cdbr-iron-east-04.cleardb.net",user="****",passwd="******",port=3306,db="ad_c94e6f9126828d8")
cur=db.cursor()

#Creating a storage container to the datastore (similar to a directory)
conn.put_container("test_container")
print "Container created successsfully"

@app.route('/',methods=['GET'])
def run():
	return render_template("index.html")

#Basic home page for user name and user password validation
@app.route('/index',methods=['POST'])
def index():
	lp=request.form['login']
	pp=request.form['passwd']
	sql=("Select User_ID from user_details where User_name=%s and User_password=%s")
	query_parameters=(lp,pp)
	cur.execute(sql,query_parameters)
	result=cur.fetchall()
	global u_id
	for row in result:
		u_id=row[0]
	print "%s" %u_id
	return render_template("upload.html")


#Upload the file to bluemix storage
@app.route('/upload',methods=['GET','POST'])
def Upload():
	if request.method=='POST':
		file= request.files['file_upload']
	filenames=file.filename
	icontents = file.read()
	d = k.encrypt(icontents)

	conn.put_object("Tom",
		filenames,
		contents = d,
		content_type="text")
	return render_template("upload.html")

#List of the filesin that container for the particular user
@app.route('/list',methods=['GET','POST'])
def List():
  listOfFilesincloud = ""
  for container in conn.get_account()[1]:
    for data in conn.get_container(container['name'])[1]:
      if not data:
        listOfFilesincloud = listOfFilesincloud + "<i> No files are currently present on Cloud.</i>"
      else:
        listOfFilesincloud = listOfFilesincloud + "<li>" + 'File: {0}\t Size: {1}\t Date: {2}'.format(data['name'], data['bytes'], data['last_modified']) + "</li><br>"
  return render_template("download.html")	

@app.route('/download',methods=['GET','POST'])
def Download():
    if request.method=='POST':
      filenames = request.form['file_download']
      file = conn.get_object("test_container",filenames)
      fileContentsBytes = file[1]#str(file)
      fileContents = k.decrypt(fileContentsBytes).decode('UTF-8')
      return render_template("download.html")

#delete the file from the container
@app.route('/delete',methods=['GET','POST'])
def Delete():
    if request.method=='POST':
      filename = request.form['file_delete']
      file = conn.delete_object("test_container",filename)

    return render_template("index.html")
	  
port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=int(port),debug=True)


