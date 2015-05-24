#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#Bamboodl - a cultural archival tool
#Copyright Daniel Tadeuszow
#2015-05-15
#License: AGPL3+

##
#Python STD
##
import json, os, datetime
from urllib.parse import urlparse
from urllib import request

##
#Bamboodl
##

from xenutils import *
from bambootil import *
from bamboovar import *


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

def bamboodl_load():

	debug_enable()

	#1 Load new urls list, delete list, put new URLs into watched.json under 'new', save watched.json
	load_subscribe_object()
	load_newsubs()
	print("New subscriptions loaded...")
	#reprocess_the_dead()
	#print("Dead items reprocessed...")

def bamboodl_run():

	#
	print("Preparing to check...")
	check_imageboards()
	print("Prepared to check...")

	#Spawn Fetch threads for everything, run through regular link list by date, seeing if wait time has been reached, and if so spawn a Fetch thread
	print("Spawning worker threads...")
	spawn_downloaders()
	print("Workers spawned...")

	#Wait for those threads to join again~
	print("Waiting for workers to complete...")
	from bambootil import total_json
	while not query_download_queue_empty():
		sleep_for(1)



#	#	#

if __name__ == '__main__':

	print("Welcome", os.getlogin())
	print("\n")

	bamboodl_load()
	bamboodl_run()

	#Save to disk
	save_subscribe_object()

	exit()





