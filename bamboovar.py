#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#Bamboodl - a cultural archival tool
#Copyright Daniel Tadeuszow
#2015-05-15
#License: AGPL3+

##
#Python STD
##
from os import path
from threading import Lock
from pathlib import Path
from urllib import request
from threading import BoundedSemaphore

##
#Bamboodl
##

from xenutils import confirm_path, j_save, j_load

##
#VARIABLES
##

config={}
subscribe={}

total_json = []
skipped = []

new_watch = []
new_dead = []
threads = []

#PATHS

dir_settings=Path(path.expanduser("~/_python/bamboodl/"))
dir_downloads=Path(path.expanduser("~/bamboodl/"))
dir_downloads_wip=dir_downloads/"active"
dir_downloads_done=dir_downloads/"complete"

paths = {
	'dir_settings':dir_settings,
	'path_conf':dir_settings / "bamboodl.json",
	'path_newsubs':dir_settings / "new.txt",
	'path_subscribe':dir_settings / "subscribed.json"
}
#dir_downloads=Path(path.expanduser("~/Downloads/bamboodl/"))
#dir_downloads=Path(path.expanduser("/VOLUMES/GITSTICK/Downloads/"))

##
#URL HANDLING
##
#This is to circumvent Newgrounds' and 4Chan's anti-automated-downloads policy
##
speed_throttle = 75
opener = request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
request.install_opener(opener)

##
#ACCEPTED ROOT DOMAINS
##

dom_4chan="4chan.org"
dom_8chan="8ch.net"
dom_wizchan="wizchan.org"

dom_shanachan="shanachan.org"
dom_krautchan="krautchan.net"

dom_tumblr="tumblr.com"
dom_newgrounds="newgrounds.com"
dom_deviantart="deviantart.com"
dom_furaffinity="furaffinity.net"
dom_inkbunny="inkbunny.net"
dom_mangafox="mangafox.me"
dom_pixiv="pixiv.net"

#These domains are imageboards that have a JSON API.
domains_imageboards_json_capable=[
	dom_4chan,
	dom_8chan,
	dom_wizchan
]

#These domains are imageboards that don't have a JSON API, so their thread's HTML must be scraped manually.
domains_imageboards_html_scrape=[
	dom_shanachan,
	dom_krautchan
]

#This is a collection of all accepted imageboard domains.
domains_imageboards=domains_imageboards_json_capable + domains_imageboards_html_scrape

#This is a collection of all accepted domains, including some that aren't actually handled yet.
domains=domains_imageboards + [
	dom_tumblr,
	dom_newgrounds,
	dom_deviantart,
	dom_furaffinity,
	dom_inkbunny,
	dom_mangafox,
	dom_pixiv
]

##
#DEFAULT USER CONFIG
##

#This is the barebones config file, but it doesn't have any domain-specific information.
config_default = {
	"bamboodl":{
		"conf_version_timestamp":"1431950400",
		"download_dir":str(dir_downloads_wip),
		"complete_dir":str(dir_downloads_done)
	},
	"domains":{
	}
}

#These are the minimum and maximum wait times for each domain, dictating how quickly Bamboodl should recheck URLs on those domains.
wait_times_default={
	dom_4chan:[300,604800],					#5 minutes		- weekly
	dom_8chan:[600,1209600],				#10 minutes		- bimonthly
	dom_wizchan:[600,1209600],				#10 minutes		- bimonthly
	dom_shanachan:[600,1209600],			#10 minutes		- bimonthly
	dom_krautchan:[600,1209600],			#10 minutes		- bimonthly
	dom_tumblr:[86400,2419200],				#daily			- monthly
	dom_newgrounds:[604800,2419200],		#weekly			- monthly
	dom_deviantart:[604800,2419200],		#weekly			- monthly
	dom_furaffinity:[604800,2419200],		#weekly			- monthly
	dom_inkbunny:[604800,2419200],			#weekly			- monthly
	dom_mangafox:[2419200,14515200],		#monthly		- bi-yearly
	dom_pixiv:[2419200,2419200]				#monthly		- monthly
}

#Here we run through all the domains and give them their own download directories and min/max wait times.
#Additional data will be added in future versions.
for domain in domains:

	#We'll use the root domain name, minus the TLD (.com, .net, etc), as the name of the directory to store downloads from that domain.
	#In general, websites probably won't change their root domains.
	#8chan.co -> 8ch.net was a rare exception, but it jarred me enough to design this code in such a way that it shouldn't be a serious problem in the future.
	dom_dir=domain.split('.')[0]

	#Here we add domain-specific config data.
	config_default['domains'][domain] = {
		'default':{
			'wait_time':wait_times_default[domain],
			'download_wip':str(dir_downloads_wip/dom_dir),
			'download_done':str(dir_downloads_done/dom_dir)
		}
	}

#Upgrader from the first public release config file to the 2015-05-18 one.
def upgrade_config(dir_old_wip, dir_old_done):
	global config

	dir_wip = Path(dir_old_wip)
	dir_done = Path(dir_old_done)

	config['domains'] = {}

	del config['bamboodl']["database_version_date"]
	config['bamboodl']["conf_version_timestamp"]="1431950400"

	for domain in domains:

		dom_dir=domain.split('.')[0]

		config['domains'][domain] = {
			'default':{
				'wait_time':wait_times_default[domain],
				'download_wip':str(dir_wip/dom_dir),
				'download_done':str(dir_done/dom_dir)
			}
		}

##
#CONFIG ACCESS FUNCTIONS
##

def init_user_settings():
	global paths, config, config_default

	print("This is the first time you're running bamboodl, or your bamboodl settings have been deleted.", critical=True)
	print("bamboodl is creating your settings for you, you can find them in: <user_dir>/.python/bamboodl", critical=True)

	confirm_path(paths['dir_settings'])

	config = config_default

	j_save(paths['path_conf'], config)

def load_user_settings():
	global paths, config

	#If the user has a configuration file,
	if paths['path_conf'].exists():

		#Load it,
		config = j_load(paths['path_conf'])

		#But if it's outdated,
		#TODO: Move all this 'config' loading/saving stuff into bamboovar, same with handling old versions of the config standard.
		if config["bamboodl"]["database_version_date"] == "2015.4.1":

			#Upgrade the user's config file,
			print("Config file out of date, updating...")
			upgrade_config( config["bamboodl"]["download_dir"], config["bamboodl"]["complete_dir"] )

			#And save the new config!
			j_save(paths['path_conf'], config)

	#If there is no config file,
	else:
		#Initialize it.
		init_user_settings()

	print("Settings loaded...")

load_user_settings()

##
#REGEX MATCH
##

reg_start=r"(?:https?:\/\/)?(?:www\.)?"

key_regex = {
	dom_4chan:reg_start+r"boards\." + dom_4chan + r"/(\w+)/thread/([0-9]+)((?:\.json)|/?(?:[a-zA-Z-]*))(?:#q?[0-9]+)?",
	dom_8chan:reg_start+r"8ch.net/([a-zA-Z0-9-+]*)/res/?([0-9]+)(?:(?:.html)|(?:.json))(?:#q?[0-9]+)?",
	dom_wizchan:reg_start+r"wizchan.org/([a-zA-Z0-9-+]*)/res/?([0-9]+)(?:(?:.html)|(?:.json))(?:#q?[0-9]+)?",
	dom_tumblr:reg_start+r"([a-zA-Z0-9-]*)\." + dom_tumblr + "\/?(?:tagged\/)?([a-zA-Z0-9-_+=#]*)",
	dom_newgrounds:reg_start+r"([a-zA-Z0-9-]*)\." + dom_newgrounds + r"\/?",
	dom_deviantart:reg_start+r"([a-zA-Z0-9-]*)\." + dom_deviantart + r"\/?",
	dom_furaffinity:reg_start+ dom_furaffinity + r"\/user\/([a-zA-Z0-9-]*)\/?",
	dom_inkbunny:reg_start + dom_inkbunny + r"\/([a-zA-Z0-9-]*)\/?",
	dom_mangafox:reg_start + dom_mangafox + r"\/manga\/([a-zA-Z0-9_-]*)\/?(?:[a-zA-Z0-9_.\/])?",
	dom_pixiv:reg_start + dom_pixiv + r"\/member\.php\?id=([0-9]*)\/?(?:[a-zA-Z0-9_.\/])?"
}

##
#REGEX REPLACE
##

rep_start=r'{\n\t"last_updated":0,\n\t"last_checked":0,\n\t"domain":'
rep_stop=r'\n}'

key_reg_replace={
	dom_4chan:rep_start + r'"4chan.org",\n\t"board":"\g<1>",\n\t"thread":"\g<2>",\n\t"url":"https://boards.4chan.org/\g<1>/thread/\g<2>.json",\n\t"wait_time":' + str(config['domains'][dom_4chan]['default']['wait_time'][0]) + rep_stop,
	dom_8chan:rep_start + r'"8ch.net",\n\t"board":"\g<1>",\n\t"thread":"\g<2>",\n\t"url":"https://8ch.net/\g<1>/res/\g<2>.json",\n\t"wait_time":' + str(config['domains'][dom_8chan]['default']['wait_time'][0]) + rep_stop,
	dom_wizchan:rep_start + r'"wizchan.org",\n\t"board":"\g<1>",\n\t"thread":"\g<2>",\n\t"url":"https://wizchan.org/\g<1>/res/\g<2>.json",\n\t"wait_time":' + str(config['domains'][dom_wizchan]['default']['wait_time'][0]) + rep_stop,
	dom_tumblr:rep_start + r'"tumblr.com",\n\t"account":"\g<1>",\n\t"url":"http://\g<1>.tumblr.com/",\n\t"tags":["\g<2>"],\n\t"wait_time":' + str(config['domains'][dom_tumblr]['default']['wait_time'][0]) + rep_stop,
	dom_newgrounds:rep_start + r'"newgrounds.com",\n\t"account":"\g<1>",\n\t"url":"\g<0>",\n\t"wait_time":' + str(config['domains'][dom_newgrounds]['default']['wait_time'][0]) + rep_stop,
	dom_deviantart:rep_start + r'"deviantart.com",\n\t"account":"\g<1>",\n\t"url":"\g<0>",\n\t"wait_time":' + str(config['domains'][dom_deviantart]['default']['wait_time'][0]) + rep_stop,
	dom_furaffinity:rep_start + r'"furaffinity.com",\n\t"account":"\g<1>",\n\t"url":"\g<0>",\n\t"wait_time":' + str(config['domains'][dom_furaffinity]['default']['wait_time'][0]) + rep_stop,
	dom_inkbunny:rep_start + r'"inkbunny.net",\n\t"account":"\g<1>",\n\t"url":"\g<0>",\n\t"wait_time":' + str(config['domains'][dom_inkbunny]['default']['wait_time'][0]) + rep_stop,
	dom_mangafox:rep_start + r'"mangafox.me",\n\t"account":"\g<1>",\n\t"url":"\g<0>",\n\t"wait_time":' + str(config['domains'][dom_pixiv]['default']['wait_time'][0]) + rep_stop,
	dom_pixiv:rep_start + r'"pixiv.net",\n\t"account":"\g<1>",\n\t"url":"\g<0>",\n\t"wait_time":' + str(config['domains'][dom_pixiv]['default']['wait_time'][0]) + rep_stop
}



##
#DEFAULT SUBSCRIPTIONS
##

#'dead' is a temporary holding pen for 404'd threads.
#URLs marked as dead are stored here temporarily until they can be confirmed 404'd.
#This is a temporary measure until I implement better code for detecting Internect connectivity issues.
subscribe_default = {
	'dead':[]
}

#Now we add a placeholder record for all accepted domains.
for domain in domains:
	subscribe_default[domain]={}

#These are multithreading related variables; multithreading in Bamboodl will be heavily refactored later, so ignore these unless you're intent on doing that yourself. It'll be boring I asure you.
subscribe_threadlock = Lock()
checked_threads_threadlock = Lock()
maxconnections = 3
downoader_semaphore = BoundedSemaphore(value=maxconnections)
