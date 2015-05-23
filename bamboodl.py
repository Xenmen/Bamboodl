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
#Bamboodl
##

from xenutils import *

#

from bambootil import *

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
	This application uses a local file with a list of urls to download those URLS and related media
"""


#	#	#


###
#Imageboard Threads have a minimum wait time of 30 seconds, tumblr accounts of 1hr, newgrounds accounts of 1 day
###

def bamboodl_run():

	debug_enable()

	#1 Load new urls list, delete list, put new URLs into watched.json under 'new', save watched.json
	load_subscribe_object()
	load_newsubs()
	print("New subscriptions loaded...")
	#reprocess_the_dead()
	#print("Dead items reprocessed...")


	#2 Spawn Fetch threads for everything, run through regular link list by date, seeing if wait time has been reached, and if so spawn a Fetch thread
	from bambootil import subscribe
	print("Preparing to check...")
	check_imageboards()

	print("Prepared to check...")
	spawn_downloaders()
	print("Downloaders spawned...")

	#3 Wait for those threads to join again~
	print("Running downloaders...")
	from bambootil import total_json
	while total_json:
		time.sleep(1)

	#5 Save to disk
	save_subscribe_object()


#	#	#

if __name__ == '__main__':
	bamboodl_run()

	exit()





