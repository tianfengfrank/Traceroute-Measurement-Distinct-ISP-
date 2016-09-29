# -*- coding: utf-8 -*-
import os
import sys
import fileinput
import sqlite3
import subprocess
import commands
import os.path
import json,urllib
import urllib2
import re
import time
from urllib import urlencode
from ipip import IP
from ipip import IPX
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


def hosttogeo_online_ipip(dst):
	errorresult=["",""]
	if len(re.findall(r"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+",dst))<=0:#判断ip或url
		dst=dst.replace("http://",'')
		print dst
		process = subprocess.Popen(["nslookup", dst], stdout=subprocess.PIPE)
		output = process.communicate()[0].split('\n')
		print output
		ip_arr = []
		for data in output:
			if 'Address' in data:
				ip_arr.append(data.replace('Address: ',''))
		if len(ip_arr)<=1:
			return errorresult
	 	pass
		ip_arr.pop(0)#待验证，如果这个函数出错，很有可能是这里
		ip=ip_arr[0]
		pass
	else:
		ip=dst
	
	print ip
	success = False
	attempts = 0
	req = urllib2.Request("http://ipapi.ipip.net/find?addr=%s" % ip)
	req.add_header("Token","826d2ebfc79dc1ccfac3a6f2c1ea6a6b7bafd423")
	#qq：9a8bc1a059db4a14b4feb0f38db38bbf4d5353ab   #163：f4f24f5817d67448fd6c7137fdf5bbc0cec7b4ec #sina：826d2ebfc79dc1ccfac3a6f2c1ea6a6b7bafd423
	while attempts < 3 and not success:
			try:
				f = urllib2.urlopen(req)
				success = True 
			except:
				attempts += 1
				if attempts==3:
					print "IOerror"
	if success:
		the_page = f.read()
		res = json.loads(the_page)
		print res
		return res
	else:
		return errorresult
	pass


def hosttogeo_local(dst):#需要完善ISP信息
	errorresult={"ret":"fault"}
	if len(re.findall(r"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+",dst))<=0:#判断ip或url
		dst=dst.replace("http://",'')
		print dst
		process = subprocess.Popen(["nslookup", dst], stdout=subprocess.PIPE)
		output = process.communicate()[0].split('\n')
		print output
		ip_arr = []
		for data in output:
			if 'Address' in data:
				ip_arr.append(data.replace('Address: ',''))
		if len(ip_arr)<=1:
			return errorresult
	 	pass
		ip_arr.pop(0)#待验证，如果这个函数出错，很有可能是这里
		ip=ip_arr[0]
		pass
	else:
		ip=dst
	
	print ip
	IP.load(os.path.abspath("GeoIP.dat"))
	res=IP.find(ip)

	if res=='N/A':
		return errorresult
		pass
	else:
		res=res.split("	")
		obj = {'ret': 'ok','data':res}
		return obj


def traceroute(file_name,dir):
	
	print "Into Traceroute Function"
	error_file=open(file_name,'r')
	line = error_file.readline().strip('\n')
	time_counter=0
	
	url_list=[]
	while line!='':
		if line.find("http")!=0:
			if line in url_list:
				print "Domin Exist"
				line = error_file.readline().strip('\n')
			else:
				url_list.append(line)
				#print line
				file_name_trace = dir+line.replace('/','')+".log"
				trace_file=open(file_name_trace,'wt')
				command = 'traceroute -m 20 '+line#设置num
				print command
				time_counter=0
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
						print "into hosttogeo"
						temp_json = hosttogeo_online_ipip(ip)#离线

						temp_json["ip"] = ip
						count = 1
						for t in time:
							temp_json["time_"+str(count)] = t
							count+=1
						
						temp_write = json.dumps(temp_json,ensure_ascii=False)
					else:
						time_counter+=1
						temp_write ='***'
					print temp_write
					trace_file.write(temp_write+'\n')
				


				line = error_file.readline().strip('\n')
				trace_file.write(str(time_counter)+'\n')		
				trace_file.close
		else:
			line = line.replace('http://','')
			print line	
	#print file_name
	#print url_list
	error_file.close()


def pagecatch(file_name_url):
	url_file=open(file_name_url)
	url_line = url_file.readline()

	while url_line!='':
		file_name = url_line.strip('\n')+'.log'
		file_name_log = './transportlogs/'+file_name.replace('/','.')
		file_name_error = './errorlogs/'+file_name.replace('/','.')
		file_name_snap = './snapshots/'+file_name.replace('/','.')
		print file_name
		if (os.path.exists('./transportlogs')) == False:
			os.makedirs('./transportlogs')
		if (os.path.exists('./errorlogs')) == False:
			os.makedirs('./errorlogs')
		if (os.path.exists('./snapshots')) == False:
			os.makedirs('./snapshots')
		
		command='./phantomjs-2.1.1-macosx/bin/phantomjs '+'./netlog.js '+'http://www.'+url_line.strip('\n')+' '+file_name_log+' '+file_name_error+' '+file_name_snap
		print command
		temp_process=os.system(command)
		url_line = url_file.readline()
	url_file.close()

def traceall(errordir):
	if (os.path.exists('./tracelogs')) == False:
		os.makedirs('./tracelogs')
	for parent,dirnames,filenames in os.walk(errordir):  
    		for filename in filenames:
    			if re.match("\..*",filename)!=None:
    				#print filename
    				continue
    			else:
					#print filename
					dirname='./tracelogs/'+filename
					print dirname
					os.makedirs(dirname)
					traceroute(os.path.join(parent,filename),dirname+'/')

def traceall_db(filename,dirname,ISP):
	os.makedirs(dirname)
	error_file=open('./'+filename,'w')
	db = sqlite3.connect("./geo_gov.db")
	db_handle = db.cursor()
	db.text_factory = str
	query="select Url,CityId from beacon where ISP not like '%"+ISP+"%'"
	db_handle.execute(query)
	temp=db_handle.fetchall()
	citylist=[]
	for x in temp:
		#if x[1] not in citylist:
		citylist.append(x[1])
		error_file.write(str(x[0])+'\n')
		#	pass
		#pass
	print citylist
	error_file.close()
	traceroute(filename,dirname+'/')







if __name__ == '__main__':
	start_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	#pagecatch(sys.argv[1])
	traceall_db('tracefile/123','./tracelogs/123',sys.argv[1])
	#traceall(sys.argv[1])
	#temp_json=hosttogeo_local("234.235.120.106")
	#temp_json["ip"] = '100.66.4.1'
	#print(temp_json)
	print start_time
	print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))