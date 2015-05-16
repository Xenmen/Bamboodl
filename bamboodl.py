#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#Bamboodl - a cultural archival tool
#Copyright Daniel Tadeuszow
#2015-05-15
#License: AGPL3+

##
#Python STD
##
import json
import time, datetime
from urllib.parse import urlparse
from urllib import request

##
#bamboodl
##

from xenutils import *

#

from bambootil import subscribe,  Downloader
from bambootil import load_user_settings, load_subscribe_object, save_subscribe_object, load_newsubs, reprocess_the_dead
from bambootil import check_everything, spawn_downloaders, join_downloaders

#

from bamboovar import dom_4chan, dom_8chan, dom_tumblr, dom_newgrounds, dom_deviantart, dom_furaffinity
from bamboovar import key_regex, key_reg_replace
#from bambootil import extract_root_domain_from_url


#	#	#


"""
Dependencies:
	Beautiful Soup : >4
Setup:
	"pip3 install beautifulsoup4"
Desc:
	This application uses a local file with a list of urls
"""


#	#	#


###
#Imageboard Threads have a minimum wait time of 30 seconds, tumblr accounts of 1hr, newgrounds accounts of 1 day
###

def bamboodl_run():

	debug_enable()

	#1 Load new urls list, delete list, put new URLs into watched.json under 'new', save watched.json
	load_user_settings()
	print("Settings loaded...")
	load_subscribe_object()
	print("Current Subscriptions loaded...")
	load_newsubs()
	print("New subscriptions loaded...")
	#reprocess_the_dead()
	#print("Dead items reprocessed...")


	#2 Spawn Fetch threads for everything, run through regular link list by date, seeing if wait time has been reached, and if so spawn a Fetch thread
	from bambootil import subscribe
	print("Preparing to check...")
	check_everything()
	print("Prepared to check...")
	spawn_downloaders()
	print("Downloaders spawned...")

	#3 Wait for those threads to join again~
	print("Running downloaders...")
	join_downloaders()
	print("Downloaders have exited...")

	print("Saving updated subscription data...")
	save_subscribe_object()
	print("Complete.")


#	#	#

if __name__ == '__main__':
	bamboodl_run()
	#deadthread_url = "https://8ch.net/4chon/res/13475.json"
	#deadthread = download_text(deadthread_url)
	#print(deadthread)

	exit()
	##
	import re
	##
	line="https://boards.4chan.org/t/thread/651652\n"
	line="http://mcsweezy.tumblr.com/\n"
	json_test=""
	domain = extract_root_domain_from_url(line)
	print("DOMAIN IS:" + domain)
	if domain in key_regex:
		myregex = re.compile(key_regex[domain])
		print("REGEX USED IS:" + key_regex[domain])
		line_parsed = myregex.sub(key_reg_replace[domain], line)
		print("PARSED LINE IS:" + line_parsed)
		try:
			json_test = json.loads(line_parsed)
		except Exception as e:
			print("WHOOPS there was an error!")
			#raise e
			#new_newsubs
		
	print("DONE")
	print(json_test)
	##
	exit()
	
	# http://boards.4chan.org/t/thread/653630/studio-fow
	# http://8ch.net/gamergatehq/res/31467.json
	# http://8ch.net/th/res/273.html
	#url="http://a.4cdn.org/t/thread/653630.json"
	#url="http://8ch.net/gamergatehq/res/31467.json"
	url="http://8ch.net/th/res/273.json"
	resp=download_text(url)
	#print(resp)
	j_save("threadtest.json", json.loads(resp))

	timestamp = time.time()
	timestamp_header = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(timestamp))
	headers={"If-Modified-Since": timestamp_header}
	print(timestamp)

	request.install_opener(request.build_opener(request.HTTPHandler))

	parsed = ""
	while parsed == "":
		time.sleep(10)
		print("Polling...")

		mlrequest = request.Request(url, data=None, headers=headers, origin_req_host=None, unverifiable=False, method=None)
		response = request.urlopen(mlrequest)

		parsed = response.read().decode('utf-8')
		print("Response is:")
		#print(parsed)

	#jthread = json.loads(download_text())
	j_save("threadtest_updated.json", json.loads(parsed))

	"""
	myjson = bambootil.j_load("8ch_example.json")

	post_standard = bambootil.post_8ch

	for post in myjson['posts']:
		#print(post[post_standard.poster_name] + " says:")
		if post_standard.comment in post:
			pass
			#print("\t" + post[post_standard.comment])
		else:
			pass
			#print("\t'no comment'")

	#j_save("8out.json", myjson)
	"""







