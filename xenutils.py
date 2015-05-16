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
import os
import time
import datetime
import logging
from os import path
from pathlib import Path
from urllib import request
from pathlib import Path
from urllib import request
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse

##
#VARIABLES
##

#DEBUG

debug_log = False
debug_print = False
debug_verbose = False

##
#DEBUG LOGGING
##

def debug(statement, critical=False):
	global debug_log, debug_print

	if critical or debug_print: print(statement)
	if critical or debug_log: logging.debug(statement)

def debug_v(statement):
	global debug_verbose

	if debug_verbose: debug(statement)

def print_json(data):

	print(json.dumps(data, indent="\t"))

def debug_enable():
	global debug_print

	debug_print = True

##
#FILESYSTEM
##

def wait_until_exists(path):
	
	__tick = 0
	while not os.path.exists(path):
		#Dirty, but makes sure the directory exists
		time.sleep(0.01)
		__tick+=1
		if __tick > 500:
			print("Waited 500ms and the Path is still inaccessible!\nAborting!!!")
			return False
	return True

def confirm_path(path):

	if not os.path.exists(str(path)):
		try:
			os.makedirs(str(path))
		except OSError as e:
			#TODO: Try handling in the future
			raise e
		finally:
			return wait_until_exists(str(path))
	else: return True

##
#JSON LOAD/SAVE
##

def j_load(path):

	with open(str(path), 'r') as file_in:
		mystring = file_in.read()
	return json.loads(mystring)

def j_save(path, data):

	with open(str(path), 'w') as file_out:
		file_out.write(json.dumps(data, indent="\t"))

##
#TIME
##

def current_time():
	return time.time()

def sleep_for(wait_time):
	time.sleep(wait_time)

##
#URL HANDLING
##

def extract_domain_from_url(url):

	url = urlparse(url)
	if url.netloc == '':
		url = url.path.split('/')[0]
	else:
		url = url.netloc
	url = str(url).replace("www.", "")
	return url

def extract_root_domain_from_url(url):

	urlbits = extract_domain_from_url(url).split('.')
	return urlbits[-2] + '.' + urlbits[-1]

def download_text(url):
	#if-modified-since header seems to be ignored
	
	html=None
	tries = 0
	trying = True
	while trying:
		try:
			#Download the webpage and parse it nicely
			html=request.urlopen(url, None, 5.0).read().decode('utf-8')
			trying = False
		#Check for redirect
		except Exception as e:
			debug_v("The link appears to be down, oh well!\n")
			if tries < 5:
				debug_v(e)
				tries += 1
				trying=True
			else:
				debug(str(tries) + " tries failed, no longer retrying...")
				debug(e)
				trying = False
	return html

def download_raw(url):
	#if-modified-since header seems to be ignored
	
	html=None
	tries = 0
	trying = True
	while trying:
		try:
			#Download the webpage and parse it nicely
			html=request.urlopen(url, None, 5.0).read()
			trying = False
		#Check for redirect
		except Exception as e:
			debug_v("The link appears to be down, oh well!\n")
			if tries < 5:
				debug_v(e)
				tries += 1
				trying=True
			else:
				debug(str(tries) + " tries failed, no longer retrying...")
				debug(e)
				trying = False
	return html

def download_soup(url):

	text=download_text(url)
	if text == None:
		return BeautifulSoup(text)
	else:
		return None


