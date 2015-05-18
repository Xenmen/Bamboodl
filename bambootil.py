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
from bamboovar import domains_imageboards
from bamboovar import key_regex, key_reg_replace
from bamboovar import config_default, subscribe_default, upgrade_config, threads
from bamboovar import total_json, skipped, new_watch, new_dead
from bamboovar import subscribe_threadlock, downoader_semaphore, checked_threads_threadlock


#	#	#

##
#USER SETTINGS
##

def init_user_settings():
	global paths, config, config_default

	debug("This is the first time you're running bamboodl, or your bamboodl settings have been deleted.", critical=True)
	debug("bamboodl is creating your settings for you, you can find them in: <user_dir>/.python/bamboodl", critical=True)

	confirm_path(paths['dir_settings'])

	config = config_default

	j_save(paths['path_conf'], config)

def load_user_settings():
	global paths, config, subscribe

	#If the user has a configuration file,
	if paths['path_conf'].exists():

		#Load it,
		config = j_load(paths['path_conf'])

		#But if it's outdated,
		#TODO: Move all this 'config' loading/saving stuff into bamboovar, same with handling old versions of the config standard.
		if config["bamboodl"]["database_version_date"] == "2015.4.1":

			#Upgrade the user's config file,
			upgrade_config( config["bamboodl"]["download_dir"], config["bamboodl"]["complete_dir"] )

			#And save the new config!
			j_save(paths['path_conf'], config)

	#If there is no config file,
	else:
		#Initialize it.
		init_user_settings()

	#Fix the missing 'dead' record that early users of Bamboodl suffered.
	#TODO: Remove this in a month or two when everybody's upgraded.
	if 'dead' not in subscribe:
		subscribe['dead'] = []

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

def save_subscribe_object():
	global paths, subscribe

	debug("\n\n\nSAVING SUBSCRIPTIONS OBJECT")
	debug_v(subscribe)
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

class Post(object):
	"""docstring for Post"""
	def __init__(self,
			post_no='no',
			poster_name='name',
			timestamp='time',
			comment='com',
			filename_internal='tim',
			md5='md5',

			segregated_op=False,
			op_id='op',

			multifile='extra_files',

			thumb_path='https://media.8ch.net/<board>/thumb/<filename>.jpg',
			media_path='https://media.8ch.net/<board>/src/<filename><ext>'
		):
		super(Post, self).__init__()
		self.post_no = post_no
		self.poster_name = poster_name
		self.timestamp = timestamp
		self.comment = comment
		self.filename_internal=filename_internal
		self.md5 = md5

		self.segregated_op = segregated_op
		self.op_id = op_id

		self.multifile = multifile

		self.thumb_path=thumb_path
		self.media_path=media_path

post_styles = {
	dom_4chan:Post(
		thumb_path="http://i.4cdn.org/<board>/<filename>s.jpg",
		media_path="http://i.4cdn.org/<board>/<filename><ext>"),
	dom_8chan:Post(),
	dom_wizchan:Post(
		thumb_path="http://wizchan.org/<board>/thumb/<filename>.gif",
		media_path="http://wizchan.org/<board>/src/<filename><ext>")
}

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

		#imageboard data
		self.post_standard = {}

	def run(self):
		global subscribe_threadlock, checked_threads_threadlock
		global domains_imageboards, dom_tumblr, dom_newgrounds
		global post_styles, total_json, new_watch, new_dead

		self.dead = False

		if self.early_end: return

		done = False

		while not done:
			domain = self.subscription['domain']
			debug_v("Now on: " + self.subscription['url'])

			if domain in domains_imageboards:
				self.post_standard = post_styles[domain]
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
		global downoader_semaphore, config

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
			data = download_text(url)
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
				if self.post_standard.post_no not in cur_thread['posts'][-1]:
					print("\tSorry, this 4chan thread has fucked up json.")
					print("\tThread is: " + self.subscription['url'])	
					self.dead = True
					return

				#Calculate the timestamp of the most recent post
				new_update_time = float(cur_thread['posts'][-1][self.post_standard.timestamp])

				#If it's the same as the last time we checked...
				if new_update_time == self.subscription['last_updated']:

					#And we aren't already over the max wait time for that domain...
					if self.subscription['wait_time'] <= config['domains'][domain]['default']['wait_time'][1]:

						#Increase the wait time until checking again...
						temp = int(self.subscription['wait_time'] * 1.5)

						#and assign.
						if temp > max_wait[domain]:
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
				#print("The latest post is #: " + str(cur_thread['posts'][-1][self.post_standard.post_no]))

				#raise e

		#TODO: update old_thread with cur_thread
		thread = cur_thread

		#Now save the json
		debug_v(self.path)
		
		j_save(self.path / 'thread.json', thread)

		#Now parse media
		self.dl_thread_media(thread)

	def dlfile(self, url, path, filename, overwrite=False):
		if not confirm_path(path):
			debug("\tDL Path unaccessible!\n\tPath is: " + str(path))
			return False
		
		# Open our local file for writing
		#with open(os.path.basename(url), "wb") as local_file:
		
		#Parse local filename
		if filename==None:
			filename=os.path.basename(url)
		#filepath=os.path.join(path, filename + os.path.splitext(url)[1])
		filepath=os.path.join(str(path), filename)
		
		#Skip downloading if the file exists
		if os.path.isfile(filepath) and not overwrite:
			#debug("File exists:" + filename)
			return True
		
		#print filepath
		
		# Open the url
		try:
			
			#Create a temporary version, so that when we save the file to disk we have no risk of a partially downloaded file
			#TODO: Consider not doing this for webms, since they may be of a much larger size than images
			temp_storage=download_raw(url)

			if temp_storage == None:
				print("File is blank/invalid.")
				return False
			
			#Save the file to disk
			with open(filepath, "wb") as local_file:
				local_file.write(temp_storage)
			return True
		
		#handle errors ()
		except HTTPError as e:
				print("HTTP Error:" + str(e.code) + url)
				return False
		except URLError as e:
				print("URL Error:" + url)
				print(e)
				return False
		except Exception as e:
				print("Unhandled Error for: " + url)
				print(e)
				#print(e.reason)
				return False

	def dl_thread_media(self, thread):
		global downoader_semaphore, dom_8chan

		thumbs = []
		media = []

		if self.post_standard.segregated_op:
			op = thread[self.post_standard.op_id]
			debug_v("Handling OP file(s)!")

			#self.path

		debug_v("Getting media for: " + self.subscription['url'])
		if 'posts' not in thread:
			print("\n\n\nOH NOOOOO")
			print(self.subscription['url'])
			print(thread)

		#Prepare the template media path
		media_temp_path = self.post_standard.media_path

		#8/b/ media links are weird, they're not on the media.8ch.net subdomain, but right on 8ch.net...
		if self.subscription['domain'] == dom_8chan and self.subscription['board'] in ['b', 'sp', 'v', 'pol']:
			#print("8/b/ thread detected")
			media_temp_path = media_temp_path.replace('media.', '')

		for post in thread['posts']:
			if self.post_standard.filename_internal in post:

				#If the file's been deleted, we can't download it! Otherwise, download.
				if post['ext'] != 'deleted':

					#8chan does not create thumbs for GIF images
					#if post['ext'] != '.gif' or self.subscription['domain'] != dom_8chan:
					#Correction, 8ch has a strange means of generating thumbs; under some circumstances (OP only if the full image is png?) the thumb will be png, so just forget thumbs for 8ch for now.
					if self.subscription['domain'] != dom_8chan:

						#Parse thumb link
						thumbs.append(self.post_standard.thumb_path.replace('<board>', self.subscription['board']).replace('<filename>', str(post[self.post_standard.filename_internal])).replace('<ext>', post['ext']))

					#Parse media link
					media.append(media_temp_path.replace('<board>', self.subscription['board']).replace('<filename>', str(post[self.post_standard.filename_internal])).replace('<ext>', post['ext']))

				if self.post_standard.multifile in post:
					debug_v("There's more than one file in this post!")
					for item in post[self.post_standard.multifile]:

						#If the file's been deleted, we can't download it! Otherwise, download.
						if item['ext'] == 'deleted': continue

						#8chan does not create thumbs for GIF images
						#if item['ext'] != '.gif' or self.subscription['domain'] != dom_8chan:
						#Correction, 8ch has a strange means of generating thumbs; under some circumstances (OP only if the full image is png?) the thumb will be png, so just forget thumbs for 8ch for now.
						if self.subscription['domain'] != dom_8chan:

							#Parse thumb link
							thumbs.append(self.post_standard.thumb_path.replace('<board>', self.subscription['board']).replace('<filename>', str(item[self.post_standard.filename_internal])).replace('<ext>', '.jpg'))

						#Parse media link
						media.append(media_temp_path.replace('<board>', self.subscription['board']).replace('<filename>', str(item[self.post_standard.filename_internal])).replace('<ext>', item['ext']))
			else:
				pass
				debug_v("\t'no files'")
	
		#
		#DOWNLOAD MEDIA
		#
		
		with downoader_semaphore:
			#dl all thumbs
			for link in thumbs:
				debug_v("getting thumbnail: " + link)
				patience = 5
				while not self.dlfile(link, self.path / "thumb", None, overwrite=False) and patience > 0:
					patience -= 1
					debug("Failed to download thumb image: " + link)
					#print("Current url is: " + self.subscription['url'])
					#break
			
			#Download all the media
			for link in media:
				debug_v("getting image: " + link)
				patience = 5
				while not self.dlfile(link, self.path, None, overwrite=False) and patience > 0:
					patience -= 1
					debug("Failed to download image: " + link)
		#

	def failure_connection(self):
		pass

def seconds_since_last_checked(subscription):

	return int(current_time() - subscription['last_checked'])

def time_to_update(subscription):

	if seconds_since_last_checked(subscription) > subscription['wait_time']:
		return True
	else:
		return False

def watch_subscription_or_dont(subscription):
	global total_json, skipped
	
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
	
	one_layer = ['tumblr.com', 'newgrounds.com', 'deviantart.com']
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
	global subscribe, threads, skipped, new_watch, new_dead
	
	one_layer = ['tumblr.com', 'newgrounds.com', 'deviantart.com']
	two_layer = ['4chan.org', '8ch.net']

	for item in threads:
		#print("Joining: " + item.subscription['url'])
		item.join()
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









