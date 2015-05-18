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
#VARIABLES
##

#PATHS

dir_settings=Path(path.expanduser("~/_python/bamboodl/"))
dir_downloads=Path(path.expanduser("~/bamboodl/"))
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

domains_imageboards_json_capable=[
	dom_4chan,
	dom_8chan,
	dom_wizchan
]

domains_imageboards_html_scrape=[
	dom_shanachan
]

domains_imageboards=domains_imageboards_json_capable + domains_imageboards_html_scrape

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
#ACCEPTED DIRECTORY NAMES
##

dir_4chan="4chan"
dir_8chan="8chan"
dir_wizchan="wizchan"
dir_tumblr="tumblr"
dir_newgrounds="newgrounds"
dir_deviantart="deviantart"
dir_furaffinity="furaffinity"
dir_inkbunny="inkbunny"
dir_mangafox="mangafox"
dir_pixiv="pixiv"

directories={
	dom_4chan:"4chan",
	dom_8chan:"8chan",
	dom_wizchan:"wizchan",
	dom_tumblr:"tumblr",
	dom_newgrounds:"newgrounds",
	dom_deviantart:"deviantart",
	dom_furaffinity:"furaffinity",
	dom_inkbunny:"inkbunny",
	dom_mangafox:"mangafox",
	dom_pixiv:"pixiv"
}

##
#WAIT TIMES
##

min_wait={
	dom_4chan:300,			#5 minutes
	dom_8chan:600,			#10 minutes
	dom_wizchan:600,		#10 minutes
	dom_tumblr:86400,		#daily
	dom_newgrounds:604800,	#weekly
	dom_deviantart:604800,	#weekly
	dom_furaffinity:604800,	#weekly
	dom_inkbunny:604800,	#weekly
	dom_mangafox:2419200,	#monthly
	dom_pixiv:2419200		#monthly
}

max_wait={
	dom_4chan:604800,			#weekly
	dom_8chan:1209600,			#bimonthly
	dom_wizchan:1209600,		#bimonthly
	dom_tumblr:2419200,			#monthly
	dom_newgrounds:2419200,		#monthly
	dom_deviantart:2419200,		#monthly
	dom_furaffinity:2419200,	#monthly
	dom_inkbunny:2419200,		#monthly
	dom_mangafox:14515200,		#bi-yearly
	dom_pixiv:2419200			#monthly
}

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
	dom_4chan:rep_start + r'"4chan.org",\n\t"board":"\g<1>",\n\t"thread":"\g<2>",\n\t"url":"https://boards.4chan.org/\g<1>/thread/\g<2>.json",\n\t"wait_time":' + str(min_wait[dom_4chan]) + rep_stop,
	dom_8chan:rep_start + r'"8ch.net",\n\t"board":"\g<1>",\n\t"thread":"\g<2>",\n\t"url":"https://8ch.net/\g<1>/res/\g<2>.json",\n\t"wait_time":' + str(min_wait[dom_8chan]) + rep_stop,
	dom_wizchan:rep_start + r'"wizchan.org",\n\t"board":"\g<1>",\n\t"thread":"\g<2>",\n\t"url":"https://wizchan.org/\g<1>/res/\g<2>.json",\n\t"wait_time":' + str(min_wait[dom_wizchan]) + rep_stop,
	dom_tumblr:rep_start + r'"tumblr.com",\n\t"account":"\g<1>",\n\t"url":"http://\g<1>.tumblr.com/",\n\t"tags":["\g<2>"],\n\t"wait_time":' + str(min_wait[dom_tumblr]) + rep_stop,
	dom_newgrounds:rep_start + r'"newgrounds.com",\n\t"account":"\g<1>",\n\t"url":"\g<0>",\n\t"wait_time":' + str(min_wait[dom_newgrounds]) + rep_stop,
	dom_deviantart:rep_start + r'"deviantart.com",\n\t"account":"\g<1>",\n\t"url":"\g<0>",\n\t"wait_time":' + str(min_wait[dom_deviantart]) + rep_stop,
	dom_furaffinity:rep_start + r'"furaffinity.com",\n\t"account":"\g<1>",\n\t"url":"\g<0>",\n\t"wait_time":' + str(min_wait[dom_furaffinity]) + rep_stop,
	dom_inkbunny:rep_start + r'"inkbunny.net",\n\t"account":"\g<1>",\n\t"url":"\g<0>",\n\t"wait_time":' + str(min_wait[dom_inkbunny]) + rep_stop,
	dom_mangafox:rep_start + r'"mangafox.me",\n\t"account":"\g<1>",\n\t"url":"\g<0>",\n\t"wait_time":' + str(min_wait[dom_pixiv]) + rep_stop,
	dom_pixiv:rep_start + r'"pixiv.net",\n\t"account":"\g<1>",\n\t"url":"\g<0>",\n\t"wait_time":' + str(min_wait[dom_pixiv]) + rep_stop
}

#USER SETTINGS

config = {}
config_default = {
	"bamboodl":{
		"database_version_date":"2015.4.1",
		"download_dir":str(dir_downloads/"active"),
		"complete_dir":str(dir_downloads/"complete")
	}
}

#SUBSCRIPTIONS

subscribe = {}
subscribe_default = {
	'dead':[]
}

for domain in domains:
	subscribe_default[domain]={}

total_json = []
new_watch = []
new_dead = []
threads = []
skipped = []

subscribe_threadlock = Lock()
checked_threads_threadlock = Lock()
maxconnections = 3
downoader_semaphore = BoundedSemaphore(value=maxconnections)
