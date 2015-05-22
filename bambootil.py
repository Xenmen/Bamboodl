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

#

#from bamboovar import debug_log, debug_print, debug_verbose
from bamboovar import paths, opener
from bamboovar import config, subscribe
from bamboovar import dom_4chan, dom_8chan, dom_wizchan, dom_tumblr, dom_newgrounds, dom_deviantart, dom_furaffinity, dom_inkbunny
from bamboovar import domains_imageboards, domains_imageboards_html_scrape
from bamboovar import key_regex, key_reg_replace
from bamboovar import config_default, subscribe_default, upgrade_config, threads
from bamboovar import total_json, skipped, new_watch, new_dead
from bamboovar import subscribe_threadlock, downoader_semaphore, checked_threads_threadlock


#	#	#

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

	debug("\n\n\t###\t#\t#\t#\n\tLOADING SUBSCRIPTIONS OBJECT\n\t#\t#\t#\t###\n")
	if paths['path_subscribe'].exists():
		#print("\n\n\nLOADINGGGGG")
		subscribe = j_load(paths['path_subscribe'])
	else:
		init_user_subscribe_list()

	#Fix the missing 'dead' record that early users of Bamboodl suffered.
	#TODO: Remove this in a month or two when everybody's upgraded.
	if 'dead' not in subscribe:
		subscribe['dead'] = []

def save_subscribe_object():
	global paths, subscribe

	debug("\n\n\t###\t#\t#\t#\n\tSAVING SUBSCRIPTIONS OBJECT\n\t#\t#\t#\t###\n")
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
#THREADS
##

class Downloader(threading.Thread):
	"""docstring for Downloader"""
	def __init__(self, subscription):
		super(Downloader, self).__init__(group=None, target=None, name=None, args=(), kwargs={}, daemon=None)
		#self.local = threading.local()
		#self.local.subscription = subscription
		self.subscription = subscription
		self.early_end = False
		self.dead = False
		self.path = ""

	def run(self):
		global subscribe_threadlock, checked_threads_threadlock
		global domains_imageboards, dom_tumblr, dom_newgrounds
		global post_styles, total_json, new_watch, new_dead

		self.dead = False

		if self.early_end: return

		done = False

		while not done:
			domain = self.subscription['domain']
			debug("Now on: " + self.subscription['url'])

			if domain in domains_imageboards:
				self.dl_imageboard()

			elif domain == dom_tumblr:
				#Check RSS
				#soup = download_soup(self.subscription['url'])
				#print("Oh hey a tumblr")
				#print(self.subscription)
				pass

			elif domain == dom_deviantart:
				#Check RSS
				#soup = download_soup(self.subscription['url'])
				#print("Oh hey deviantart")
				#print(self.subscription)
				pass

			elif domain == dom_newgrounds:
				#soup = download_soup(self.subscription['url'])
				#print("Oh hey newgrounds")
				#print(self.subscription)
				pass

			elif domain == dom_furaffinity:
				#soup = download_soup(self.subscription['url'])
				#print("Oh hey furaffinity")
				#print(self.subscription)
				pass

			elif domain == dom_inkbunny:
				#soup = download_soup(self.subscription['url'])
				#print("Oh hey inkbunny")
				#print(self.subscription)
				pass

			with checked_threads_threadlock:
				if not self.dead:
					new_watch.append(self.subscription)
				else:
					new_dead.append(self.subscription)

			#Immediately reset 'dead' flag
			self.dead = False

			with subscribe_threadlock:
				if len(total_json) > 0:
					self.subscription = total_json.pop()
				else:
					done = True

	def dl_imageboard(self):
		global downoader_semaphore, config, domains_imageboards_html_scrape

		url = self.subscription['url']

		domain = self.subscription['domain']

		thread_data = {}

		#And change the path so that all data for this thread will be saved in a subdirectory matching the board and thread id
		self.path = Path(config['domains'][domain]['default']['download_wip']) / self.subscription['board'] / str(self.subscription['thread'])
		confirm_path(self.path)

		#Record current time
		temp_time = current_time()

		#Fetch current thread
		data = None
		cur_thread = {}
		with downoader_semaphore:
			#print(url)
			data = download_html(url)
			#debug_v(data)
			#sleep_for(0.2)


		#Check if there was a problem
		if data in [None, '']:
			debug("\tThread is dead: " + url)
			self.dead = True
			#TODO
			#return
		else:
			cur_thread = json.loads(data)
			#Successfully checked, record that
			#TODO: make a proper catch for 404'd threads
			self.subscription['last_checked'] = temp_time

		if cur_thread=={}:
			#Maybe the thread is dead, maybe it isn't, lets assume there's an unrelated issue
			return

		#Load old thread if we already have it
		thread = {}
		if self.subscription['last_updated'] != 0 and False:
			thread = j_load(self.path / 'thread.json')
		#Otherwise, save the thread JSON before continuing
		else:
			j_save(self.path / 'thread.json', cur_thread)

		#If the thread's current json is different from the old...
		if not thread == cur_thread:
			try:

				#See if it's a fucked up 4chan thread and do an early exit
				if 'no' not in cur_thread['posts'][-1]:
					print("\tSorry, this 4chan thread has fucked up json.")
					print("\tThread is: " + self.subscription['url'])	
					self.dead = True
					return

				#Calculate the timestamp of the most recent post
				new_update_time = float(cur_thread['posts'][-1]['time'])

				#If it's the same as the last time we checked...
				if new_update_time == self.subscription['last_updated']:

					#And we aren't already over the max wait time for that domain...
					if self.subscription['wait_time'] <= config['domains'][domain]['default']['wait_time'][1]:

						#Increase the wait time until checking again...
						temp = int(self.subscription['wait_time'] * 1.5)

						#and assign.
						#TODO: Prepare for allowing board-specific wait times.
						if temp > config['domains'][domain]['default']['wait_time'][1]:
							self.subscription['wait_time'] = config['domains'][domain]['default']['wait_time'][1]
						else:
							self.subscription['wait_time'] = temp

					#Otherwise, we don't adjust the wait time
					else: pass

				#If there's a new post since the last time we checked...
				else:

					#Reset wait_time to the minimum value...
					#TODO: Check the timestamps of other posts in the thread, get the average time between them, use that to generate a more accurate wait_time
					#TODO: Implement board-specific wait times, and only fall back to the domain default if there's no board specific time on record.
					self.subscription['wait_time'] = config['domains'][self.subscription['domain']]['default']['wait_time'][0]

				#Finally, update last_updated to reflect the latest post's timestamp.
				self.subscription['last_updated'] = new_update_time

			except Exception as e:
				print("HOLY SHIT SOMETHING WENT WRONG")

				#Report the post on
				print("Latest post has no timestamp!\nThread is: " + self.subscription['url'])
				#print("The latest post is #: " + str(cur_thread['posts'][-1]['no']))

				#raise e

		#TODO: update old_thread with cur_thread
		thread = cur_thread

		#Now save the json
		debug_v(self.path)
		
		j_save(self.path / 'thread.json', thread)

		#Now parse media
		self.dl_thread_media(thread)

	def dl_thread_media(self, thread):
		global downoader_semaphore, dom_8chan

		thumbs = []
		media = []

		debug_v("Getting media for: " + self.subscription['url'])
		if 'posts' not in thread:
			print("\n\n\nOH NOOOOO")
			print(self.subscription['url'])
			print(thread)

		domain = self.subscription['domain']

		#Prepare the template media thumbnail path
		urls_thumb = {
			dom_4chan:"https://i.4cdn.org/<board>/",
			dom_8chan:"https://media.8ch.net/<board>/thumb/",
			dom_wizchan:"https://wizchan.org/<board>/thumb/"
		}[domain].replace('<board>', self.subscription['board'])

		file_ext_thumb = {
			dom_4chan:"s.jpg",
			dom_8chan:".jpg",
			dom_wizchan:".gif"
		}[domain]

		#Prepare the template media path
		media_temp_path = {
			dom_4chan:"https://i.4cdn.org/<board>/",
			dom_8chan:'https://media.8ch.net/<board>/src/',
			dom_wizchan:'https://wizchan.org/<board>/src/'
		}[domain].replace('<board>', self.subscription['board'])

		#8/b/ media links are weird, they're not on the media.8ch.net subdomain, but right on 8ch.net...
		if domain == dom_8chan and self.subscription['board'] in ['b', 'sp', 'v', 'pol']:
			#print("8/b/ thread detected")
			media_temp_path = media_temp_path.replace('media.', '')

		for post in thread['posts']:
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
					dlfile(urls_thumb + filename, str(self.path / "thumb" / filename))

				#Parse media link
				filename = str(post['tim']) + post['ext']
				#print("Accessing",filename)
				dlfile(media_temp_path + filename, str(self.path / filename))

				if 'extra_files' in post:
					debug_v("There's more than one file in this post!")
					for item in post['extra_files']:

						#If the file's been deleted, we can't download it! Otherwise, download.
						if item['ext'] == 'deleted': continue

						#Parse media link
						filename = str(item['tim']) + item['ext']
						#print("Accessing",filename)
						dlfile(media_temp_path + filename, str(self.path / filename))

def seconds_since_last_checked(subscription):

	return int(current_time() - subscription['last_checked'])

def time_to_update(subscription):

	if seconds_since_last_checked(subscription) > subscription['wait_time']:
		return True
	else:
		return False

def watch_subscription_or_dont(subscription):
	global total_json, skipped, subscribe_threadlock

	with subscribe_threadlock:
	
		if time_to_update(subscription):
			#print("Adding watched: " + subscription['url'])
			total_json.append(subscription)
		else:
			#print("Skipping watched: " + subscription['url'])
			skipped.append(subscription)

def fetch_l1_json(domain):
	global subscribe, total_json, skipped

	for account in subscribe[domain]:
		subscription = subscribe[domain][account]
		if time_to_update(subscription):
			total_json.append(subscription)
		else:
			#print("Skipping watched: " + subscription['url'])
			skipped.append(subscription)

def fetch_l2_json(domain, sublevel):
	global subscribe

	for item in subscribe[domain][sublevel]:
		subscription=subscribe[domain][sublevel][item]
		watch_subscription_or_dont(subscription)

def check_everything():
	global subscribe, total_json, domains_imageboards

	#print("\n\n\nHEYO TIME TO WORKO")
	
	one_layer = []#'tumblr.com', 'newgrounds.com', 'deviantart.com']
	two_layer = domains_imageboards

	for key in one_layer:
		if key in subscribe:
			fetch_l1_json(key)

	for key in two_layer:
		if key in subscribe:
			for sublevel in subscribe[key]:
				fetch_l2_json(key, sublevel)

def spawn_downloaders():
	global total_json, threads, skipped

	max_threads = 5

	#total_json.extend(skipped)

	threads = []

	if len(total_json) < max_threads:
		for x in range(0, len(total_json)):
			threads.append(Downloader(total_json.pop()))
	else:
		for x in range(1, max_threads):
			threads.append(Downloader(total_json.pop()))

	for thread in threads:
		#print("Spawning: " + subscription.subscription['url'])
		thread.start()

def join_downloaders():
	global threads

	for item in threads:
		#print("Joining: " + item.subscription['url'])
		item.join()

def process_updated_subscriptions():
	global subscribe, skipped, new_watch, new_dead
	
	one_layer = ['tumblr.com', 'newgrounds.com', 'deviantart.com']
	two_layer = ['4chan.org', '8ch.net']

	#new_watch.extend(skipped)
	for item in new_watch:
		domain = item['domain']
		if domain in one_layer:
			subscribe[domain][item['account']] = item
		elif domain in two_layer:
			subscribe[domain][item['board']][item['thread']] = item

	subscribe['dead'].extend(new_dead)

	print("New dead are:")

	for item in new_dead:
		domain = item['domain']
		if domain in one_layer:
			scratch = subscribe[domain].pop(item['account'])
			if item['account'] in subscribe[domain]:
				print("Something is TERRIBLY WRONG")
		elif domain in two_layer:
			if str(item['thread']) in subscribe[domain][item['board']]:
				print("\tThread " + str(item['thread']) + " in list for " + domain + ", board " + item['board'] + ".")
				scratch = subscribe[domain][item['board']].pop(str(item['thread']))
				if item['thread'] in subscribe[domain][item['board']]:
					print("Something is TERRIBLY WRONG")

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









