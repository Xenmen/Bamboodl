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
import socket
import sys
import re
import time
import datetime
import logging
from os import path
from pathlib import Path
from urllib import request
from pathlib import Path
from urllib import request

from urllib.error import *
from urllib.parse import urlparse
from urllib.request import Request
from urllib.request import urlopen

##
#pip3 install
##
from bs4 import BeautifulSoup

##
#
##

from AsciiDammit import asciiDammit

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

def current_time(): return time.time()

def sleep_for(wait_time): time.sleep(wait_time)

##
#UNICODE HANDLING
##

unicode_stripper = re.compile(r"\&\#(?:[0-9]+);")

def strip_unicode_east_asia(string_old):
	global unicode_stripper
	
	return unicode_stripper.sub('EAST_ASIA_CHAR', string_old)

def strip_unicode(string_old):

	return asciiDammit(string_old)

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

	try:
		urlbits = extract_domain_from_url(url).split('.')
		return urlbits[-2] + '.' + urlbits[-1]
	except Exception as e:
		print("Unable to parse domain")
		return None
		#raise e

def download_html(src):
	#if-modified-since header seems to be ignored

	try:
		#Download the webpage and parse it nicely
		with urlopen(Request(src,headers={"User-Agent": "Mozilla 5.0"}),timeout=10) as resp:
			debug_v("Downloading " + src)
			html = resp.read().decode('utf-8')
			return html
	except (IOError,OSError) as error:
		print("File Error:",error)
		#debug("URL was: " + src)
		#debug("Path was: " + filename)
	except socket.timeout:
		print("File",src,"timed out")
	return None

def download_soup(src):

	parsed_text=download_html(src)
	
	if parsed_text == None: return None
	
	return BeautifulSoup(strip_unicode_east_asia(parsed_text))

def dlfile(src,filename):
	try:
		if os.path.isfile(str(filename)): return
		#confirm_path(filename)
		with urlopen(Request(src,headers={"User-Agent": "Mozilla 5.0"}),timeout=10) as resp, open(filename,"wb") as f:
			debug_v("Downloading " + src)
			f.write(resp.read())
			debug_v("Finished " + src)
	except (IOError,OSError) as error:
		print("File Error:",error)
		#debug("URL was: " + src)
		#debug("Path was: " + filename)
	except socket.timeout:
		print("File",src,"timed out")

##
#BEAUTIFUL SOUP HANDLING
##

def extract_article(page_soup, target_tag, targed_id):
	for node in page_soup.findChildren(name=target_tag, attrs={'id':targed_id}):
		return node
	return None

##
#MISC UTILITY
##

def save_pretty_json(url, filepath): j_save(filepath, json.loads(download_html(url)))

#	#	#

