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
import logging
import os
import concurrent.futures
import re
import threading
from pathlib import Path
from urllib import request
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse

##
#pip3 install
##
from bs4 import BeautifulSoup

##
#Bamboodl
##

from xenutils import *
from bamboovar import *


#	#	#

force_check_all = False

##
#SUBSCRIPTIONS
##

def init_user_subscribe_list():
	global paths, subscribe, subscribe_default

	debug("No subscribe file found! Reinitializing...", critical=True)
	subscribe = subscribe_default
	j_save(paths['path_subscribe'], subscribe)

def load_subscribe_object():
	global paths, subscribe

	if paths['path_subscribe'].exists():
		#print("\n\n\nLOADINGGGGG")
		subscribe = j_load(paths['path_subscribe'])
	else:
		init_user_subscribe_list()

	#Fix the missing 'dead' record that early users of Bamboodl suffered.
	#TODO: Remove this in a month or two when everybody's upgraded.
	if 'dead' not in subscribe:
		subscribe['dead'] = []

	debug("\n\n\t###\t\t\t###\n\tSubscriptions Object Loaded\n\t###\t\t\t###\n")

def save_subscribe_object():
	global paths, subscribe

	debug("\n\n\t###\t\t\t###\n\tSubscriptions Object Saved\n\t###\t\t\t###\n")
	j_save(paths['path_subscribe'], subscribe)

def add_json_to_subscribe(new_json):
	global subscribe, domains_imageboards

	domain = new_json['domain']
	if domain not in subscribe:
		subscribe[domain] = {}
	if domain in domains_imageboards:
		board=new_json['board']
		thread=new_json['thread']
		if board not in subscribe[domain]:
			subscribe[domain][board] = {}
		if thread not in subscribe[domain][board]:
			subscribe[domain][board][thread] = new_json
			return("Now subscribed to: " + new_json['url'])
		else:
			return("URL already watched...")
	#TODO
	#elif domain == dom_tumblr or domain == dom_deviantart or domain == dom_newgrounds or domain == dom_furaffinity or domain == dom_inkbunny:
	else:
		account = new_json['account']
		if account not in subscribe[domain]:
			if 'tags' in new_json and new_json['tags'][0] == '':
				new_json['tags'] = []
			subscribe[domain][account] = new_json
			return("Now subscribed to: " + new_json['url'])
		else:
			if 'tags' in new_json and new_json['tags'][0] not in subscribe[domain][account]['tags']:
				subscribe[domain][account]['tags'].append(new_json['tags'][0])
				return("URL already watched, but new tag added...")
			else:
				return("URL and tags already watched...")

def load_newsubs():
	global subscribe, paths, key_regex, key_reg_replace

	new_newfile=""
	if paths['path_newsubs'].exists():
		with paths['path_newsubs'].open('r') as newsubs:
			for line in newsubs:
				debug_v("New URL: "+line)

				if line == "\n":
					new_newfile = new_newfile + line
					continue

				elif line.isspace():
					debug("INVALID URL:" + line)
					#new_newfile.extend(line)
					new_newfile = new_newfile + line
				else:
					json_test=""
					domain = extract_root_domain_from_url(line.replace('\n',''))
					debug_v("\nDOMAIN IS:" + domain)
					if domain in key_regex:
						myregex = re.compile(key_regex[domain])
						debug_v("REGEX USED IS:" + key_regex[domain])
						line_parsed = myregex.sub(key_reg_replace[domain], line)
						debug_v("PARSED LINE IS:" + line_parsed)
						try:
							json_test = json.loads(line_parsed)
						except Exception as e:
							debug("\nInvalid URL:" + line.replace('\n',''), critical=True)
							#raise e
							new_newfile = new_newfile + line
							#print("WHOOPS there was an error!")
							continue
							#raise e
							#new_newsubs
						debug(add_json_to_subscribe(json_test))
						#print(json_test)
					else:
						debug("Domain '" + domain + "' not yet handled: " + line.replace('\n',''))
						new_newfile = new_newfile + line

	with paths['path_newsubs'].open('w') as newsubs:
		newsubs.write(new_newfile)

	#print("\n\n\nNEW SUBS LOADED")
	#print(subscribe)
	save_subscribe_object()

def reprocess_the_dead():
	global subscribe

	while len(subscribe['dead']) > 0:
		debug( add_json_to_subscribe(subscribe['dead'].pop()) )

	save_subscribe_object()

##
#THREADS & ACTIVE DOWNLOADS
##

def seconds_since_last_checked(last_checked):

	return int(current_time() - last_checked)

def time_to_update(subscription):

	return seconds_since_last_checked(subscription['last_checked']) > subscription['wait_time']

def watch_subscription_or_dont(subscription):
	global total_json, subscribe_threadlock, force_check_all

	with subscribe_threadlock:
	
		if force_check_all or time_to_update(subscription):
			total_json.append(subscription)

def fetch_l1_json(domain):
	global subscribe

	for account in subscribe[domain]:
		watch_subscription_or_dont(subscribe[domain][account])

def fetch_l2_json(domain, board):
	global subscribe

	for item in subscribe[domain][board]:
		watch_subscription_or_dont(subscribe[domain][board][item])

def check_imageboards():
	global subscribe, total_json, domains_imageboards

	for key in domains_imageboards:
		if key in subscribe:
			for board in subscribe[key]:
				fetch_l2_json(key, board)

def check_everything():
	global subscribe, total_json, domains_imageboards

	one_layer = ['tumblr.com', 'newgrounds.com', 'deviantart.com']
	two_layer = domains_imageboards

	for key in one_layer:
		if key in subscribe:
			fetch_l1_json(key)

	for key in two_layer:
		if key in subscribe:
			for board in subscribe[key]:
				fetch_l2_json(key, board)

def query_download_queue_empty():
	global total_json

	return len(total_json) == 0

##
#Downloader - Imageboards
##

def chandl_html(subscription, data):

	pass

def chandl(subscription):
	global subscribe_threadlock, checked_threads_threadlock
	global domains_imageboards_json_capable
	global subscribe, total_json
	global dom_8chan

	domain = subscription['domain']
	debug("Now on: " + subscription['url'])



	global config

	url = subscription['url']

	domain = subscription['domain']

	#And change the path so that all data for this thread will be saved in a subdirectory matching the board and thread id
	path = Path(config['domains'][domain]['default']['download_wip']) / subscription['board'] / str(subscription['thread'])
	confirm_path(path)

	#Record current time
	temp_time = current_time()

	#Fetch current thread
	data = download_html(url)

	#Check if there was a problem
	#TODO: make a proper catch for 404'd threads
	if data in [None, '']:
		debug("\tThread is dead: " + url)

		#If dead, add it to the newly dead thread list,
		with checked_threads_threadlock:
			if str(subscription['thread']) in subscribe[domain][subscription['board']]:
				print("\tDead thread: " + domain + ", board " + subscription['board'] + ":" + str(subscription['thread']) + ".")
				scratch = subscribe[domain][subscription['board']].pop(str(subscription['thread']))
				if item['thread'] in subscribe[domain][subscription['board']]:
					print("Something is TERRIBLY WRONG")

		#And return the worker to the pool
		return

	#
	if domain not in domains_imageboards_json_capable:
		cur_thread = chandl_html(data)
	else:
		cur_thread = json.loads(data)

	if cur_thread=={}:
		#Maybe the thread is dead, maybe it isn't, lets assume there's an unrelated issue
		return

	#Load old thread if we already have it
	thread_data = {}
	if subscription['last_updated'] != 0 and False:
		thread_data = j_load(path / 'thread.json')
	#Otherwise, save the thread JSON before continuing
	else:
		j_save(path / 'thread.json', cur_thread)

	#If the thread's current json is different from the old...
	if not thread_data == cur_thread:
		try:

			#See if it's a fucked up 4chan thread and do an early exit
			if 'no' not in cur_thread['posts'][-1]:
				print("\tSorry, this 4chan thread has fucked up json.")
				print("\tThread is: " + subscription['url'])

				#If dead, add it to the newly dead thread list,
				with checked_threads_threadlock:
					if str(subscription['thread']) in subscribe[domain][subscription['board']]:
						print("\tDead thread: " + domain + ", board " + subscription['board'] + ":" + str(subscription['thread']) + ".")
						scratch = subscribe[domain][subscription['board']].pop(str(subscription['thread']))
						if item['thread'] in subscribe[domain][subscription['board']]:
							print("Something is TERRIBLY WRONG")
				return

			#Calculate the timestamp of the most recent post
			new_update_time = float(cur_thread['posts'][-1]['time'])

			#If it's the same as the last time we checked...
			if new_update_time == subscription['last_updated']:

				#And we aren't already over the max wait time for that domain...
				if subscription['wait_time'] <= config['domains'][domain]['default']['wait_time'][1]:

					#Increase the wait time until checking again...
					temp = int(subscription['wait_time'] * 1.5)

					#and assign.
					#TODO: Prepare for allowing board-specific wait times.
					if temp > config['domains'][domain]['default']['wait_time'][1]:
						subscription['wait_time'] = config['domains'][domain]['default']['wait_time'][1]
					else:
						subscription['wait_time'] = temp

				#Otherwise, we don't adjust the wait time
				else: pass

			#If there's a new post since the last time we checked...
			else:

				#Reset wait_time to the minimum value...
				#TODO: Check the timestamps of other posts in the thread, get the average time between them, use that to generate a more accurate wait_time
				#TODO: Implement board-specific wait times, and only fall back to the domain default if there's no board specific time on record.
				subscription['wait_time'] = config['domains'][subscription['domain']]['default']['wait_time'][0]

			#Finally, update last_updated to reflect the latest post's timestamp.
			subscription['last_updated'] = new_update_time

		except Exception as e:
			print("HOLY SHIT SOMETHING WENT WRONG")

			#Report the post on
			print("Latest post has no timestamp!\nThread is: " + subscription['url'])
			#print("The latest post is #: " + str(cur_thread['posts'][-1]['no']))

			raise e

	#TODO: update old_thread with cur_thread
	thread_data = cur_thread

	#Now save the json
	debug_v(path)
	
	j_save(path / 'thread.json', thread_data)

	#Now parse media
	thumbs = []
	media = []

	debug_v("Getting media for: " + subscription['url'])
	if 'posts' not in thread_data:
		print("\n\n\nOH NOOOOO")
		print(subscription['url'])
		print(thread_data)

	#Prepare the template media thumbnail path
	urls_thumb = {
		dom_4chan:"https://i.4cdn.org/<board>/",
		dom_8chan:"https://media.8ch.net/<board>/thumb/",
		dom_wizchan:"https://wizchan.org/<board>/thumb/",
		dom_lainchan:"https://lainchan.org/<board>/thumb/"
	}[domain].replace('<board>', subscription['board'])

	file_ext_thumb = {
		dom_4chan:"s.jpg",
		dom_8chan:".jpg",
		dom_wizchan:".gif",
		dom_lainchan:".png"
	}[domain]

	#Prepare the template media path
	media_temp_path = {
		dom_4chan:"https://i.4cdn.org/<board>/",
		dom_8chan:'https://media.8ch.net/<board>/src/',
		dom_wizchan:'https://wizchan.org/<board>/src/',
		dom_lainchan:'https://lainchan.org/<board>/src/'
	}[domain].replace('<board>', subscription['board'])

	#8/b/ media links are weird, they're not on the media.8ch.net subdomain, but right on 8ch.net...
	if domain == dom_8chan and subscription['board'] in ['b', 'sp', 'v', 'pol']:
		#print("8/b/ thread detected")
		media_temp_path = media_temp_path.replace('media.', '')

	confirm_path(str(path / "thumb"))

	for post in thread_data['posts']:
		#If the post indicates it has attached media, 
		if 'tim' in post:

			#If the file's been deleted, we can't download it! Otherwise, download.
			if post['ext'] == 'deleted': continue

			#8chan does not create thumbs for GIF images
			#if post['ext'] != '.gif' or domain != dom_8chan:
			#Correction, 8ch has a strange means of generating thumbs; under some circumstances (OP only if the full image is png?) the thumb will be png, so just forget thumbs for 8ch for now.
			if domain != dom_8chan:

				#Parse thumb link
				filename = str(post['tim']) + file_ext_thumb
				dlfile(urls_thumb + filename, str(path / "thumb" / filename))

			#Parse media link
			filename = str(post['tim']) + post['ext']
			dlfile(media_temp_path + filename, str(path / filename))

			if 'extra_files' in post:
				debug_v("There's more than one file in this post!")
				for item in post['extra_files']:

					#If the file's been deleted, we can't download it! Otherwise, download.
					if item['ext'] == 'deleted': continue

					#Parse media link
					filename = str(item['tim']) + item['ext']
					#print("Accessing",filename)
					dlfile(media_temp_path + filename, str(path / filename))

	#Thread is still live, and we're done downloading media, so record that we've just checked it,
	subscription['last_checked'] = temp_time

	#And update the main Record
	with checked_threads_threadlock:
		subscribe[domain][subscription['board']][subscription['thread']] = subscription

##
#Downloader - Tumblr
##

downloaders = {
	"4chan.org":chandl,
	"8ch.net":chandl,
	"wizchan.org":chandl,
	"lainchan.org":chandl
}

def spawn_downloaders():
	global total_json

	#Create a thread pool,
	with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:

		#and while total_json isn't empty,
		while total_json:

			#grab subscriptions from it,
			subscription = total_json.pop()

			#and 
			pool.submit(downloaders[subscription['domain']],subscription)


#	#	#


###
#Imageboard Threads have a minimum wait time of 30 seconds, tumblr accounts of 1hr, newgrounds accounts of 1 day
###

#1 Load new urls list, delete list, put new URLs into watched.json under 'new', save watched.json

#2 Spawn Fetch threads for everything under 'new', run through regular link list by date, seeing if wait time has been reached, and if so spawn a Fetch thread

	#FETCH THREADS

	#If an Imageboard:

		# fetch delta json of thread (if delta not available, download whole json and figure out what the delta is)
		# 

	#If a tumblr/blog:

		#Grab RSS and

	#If a galley account:

		# fetch homepage html, compare media links to record of media in account's local json file
		# fetch new media pages, extract media links

	#Finally, 

#3 


#	#	#









