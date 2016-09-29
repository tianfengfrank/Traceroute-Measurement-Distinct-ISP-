# -*- coding: utf-8 -*-
import os
import sys
import fileinput
import subprocess
import commands
import os.path
import json,urllib
import re
import time
from urllib import urlencode
reload(sys)
sys.setdefaultencoding('utf-8')
                                

def iptojson(dst, m="GET"):
	print "Into iptojson Function"
	errorresult={u'location': u'QuerryError', u'area': u'QuerryError'}
	url = "http://apis.juhe.cn/ip/ip2addr"
	params = {
		"ip" : dst,
		"key" : "444fc52fc9dc48bb8d48f7aacc17ce52",
		"dtype" : "", 
 
	}
	attempts = 0
	success = False
	params = urlencode(params)
	if m =="GET":
		while attempts < 3 and not success:
			try:
				f = urllib.urlopen("%s?%s/" % (url, params))
				success = True 
			except:
				attempts += 1
				if attempts==3:
					print "IOerror"
	else:
		while attempts < 3 and not success:
			try:
				f = urllib.urlopen(url, params)
				success = True 
			except:
				attempts += 1
				if attempts==3:
					print "IOerror"		
		
	if success:
		content = f.read()
		res = json.loads(content)
		if res:
			error_code = res["error_code"]
			if error_code == 0:
				return res["result"]
			else:
				print "%s:%s" % (res["error_code"],res["reason"])
				return errorresult
		else:
			print "request api error"
			return errorresult
	else:
		return errorresult

def traceroute(file_name):
	
	print "Into Traceroute Function"
	error_file=open(file_name,'r')
	line = error_file.readline().strip('\n')
	if (os.path.exists('../test/tracelogs')) == False:
		os.makedirs('../test/tracelogs')
	
	url_list=[]
	while line!='':
		print line
		if line.find("http")!=0:
			if line in url_list:
				print "Domin Exist"
				line = error_file.readline().strip('\n')
			else:
				url_list.append(line)
				#print line
		
				file_name_trace = '../test/tracelogs/'+line.replace('/','.')
				trace_file=open(file_name_trace,'wt')
				command = 'traceroute -m 20 '+line
				print command
				temp_out=commands.getoutput(command)
				temp_out=temp_out.split('\n')[1:]#mac下有warning，所以要另外处理
				#print temp_out
				for temp in temp_out:
					temp_line=temp.split('  ')
					if len(temp_line)<=1:
						print "Warning Message"
						print temp
						continue
					#print temp
					print temp_line

					if len(temp_line)>=3:
						ip = re.findall("\d+\.\d+\.\d+\.\d+",temp)[0]
						time = re.findall("\d+.\d* ms",temp)
						print ip
						print time
						print file_name
						temp_json = iptojson(ip)
						temp_json["ip"] = ip
						count = 1
						for t in time:
							temp_json["time_"+str(count)] = t
							count+=1
						
						temp_write = json.dumps(temp_json,ensure_ascii=False)
						#print temp_write
						trace_file.write(temp_write+'\n')

				line = error_file.readline().strip('\n')
				trace_file.write(line+'\n')		
				trace_file.close
		else:
			print "Link Information"
			print line
			line = error_file.readline().strip('\n')	
	#print file_name
	#print url_list
	error_file.close()


def pagecatch(file_name_url):
	url_file=open(file_name_url)
	url_line = url_file.readline()

	while url_line!='':
		file_name = url_line.strip('\n')+'.log'
		file_name_log = '../test/transportlogs/'+file_name.replace('/','.')
		file_name_error = '../test/errorlogs/'+file_name.replace('/','.')
		file_name_snap = '../test/snapshots/'+file_name.replace('/','.')
		print file_name
		if (os.path.exists('../test/transportlogs')) == False:
			os.makedirs('../test/transportlogs')
		if (os.path.exists('../test/errorlogs')) == False:
			os.makedirs('../test/errorlogs')
		if (os.path.exists('../test/snapshots')) == False:
			os.makedirs('../test/snapshots')
		
		command='./phantomjs-2.1.1-macosx/bin/phantomjs '+'../test/netlog.js '+'http://www.'+url_line.strip('\n')+' '+file_name_log+' '+file_name_error+' '+file_name_snap
		print command
		temp_process=os.system(command)
		url_line = url_file.readline()
	url_file.close()

def errortrace(errordir):
	for parent,dirnames,filenames in os.walk(errordir):  
    		for filename in filenames:
    			if re.match("\..*",filename)!=None:
    				#print filename
    				continue
    			else:
					print filename
					traceroute(os.path.join(parent,filename))

if __name__ == '__main__':
	start_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	pagecatch(sys.argv[1])
	errortrace("../test/errorlogs")
	print start_time
	print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))