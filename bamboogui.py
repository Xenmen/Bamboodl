#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#Bamboodl GUI - a cultural archival tool
#Copyright Daniel Tadeuszow
#2015-05-15
#License: AGPL3+

#Code that follows is under QT's BSD license until I rewrite it

#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
		QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
		QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
		QVBoxLayout)


##
#Python STD
##
import re
import threading

##
#bamboodl
##

from xenutils import *

#

from bambootil import subscribe,  Downloader
from bambootil import load_user_settings, load_subscribe_object, save_subscribe_object, load_newsubs, add_json_to_subscribe, reprocess_the_dead
from bambootil import check_everything, spawn_downloaders, join_downloaders

#

from bamboovar import dom_4chan, dom_8chan, dom_tumblr, dom_newgrounds, dom_deviantart, dom_furaffinity
from bamboovar import key_regex, key_reg_replace

class Dialog(QDialog):
	NumGridRows = 3
	NumButtons = 4

	##
	#Window Initialization
	##

	def __init__(self):
		super(Dialog, self).__init__()

		self.createMenu()

		self.widget_register_url()
		self.widget_download()
		self.thread_download = threading.Thread( group=None, target=self.run_downloader, name=None, args=(), kwargs={}, daemon=True )
		self.running = False

		bigEditor = QTextEdit()
		bigEditor.setPlainText("This widget takes up all the remaining space "
				"in the top-level layout.")

		buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)

		mainLayout = QVBoxLayout()
		mainLayout.setMenuBar(self.menuBar)

		mainLayout.addWidget(self.form_register_url)
		mainLayout.addWidget(self.form_download_urls)

		self.setLayout(mainLayout)

		self.setWindowTitle("Bamboodl")

	def createMenu(self):
		self.menuBar = QMenuBar()

		self.fileMenu = QMenu("&File", self)
		self.exitAction = self.fileMenu.addAction("E&xit")

		self.exitAction.setShortcut('Ctrl+Q')
		self.exitAction.setStatusTip('Exit application')
		#self.exitAction.triggered.connect(qApp.quit)

		self.menuBar.addMenu(self.fileMenu)

		self.exitAction.triggered.connect(self.accept)

	def createButton(self, text, member):
		button = QPushButton(text)
		button.clicked.connect(member)
		return button

	##
	#Registering a new URL
	##

	def set_label_text_register(self, new_text):
		self.label_new_url_debug.setText(new_text)

	def click_process_new_url(self):
		global subscribe, paths, key_regex, key_reg_replace

		line = self.text_input_new_url.text()

		if line.isspace():
			self.set_label_text_register("'URL' space is blank, enter a url!")

		else:
			json_test=""
			domain = extract_root_domain_from_url(line.replace('\n',''))

			if domain in key_regex:
				myregex = re.compile(key_regex[domain])
				line_parsed = myregex.sub(key_reg_replace[domain], line)

				try:
					json_test = json.loads(line_parsed)
				except Exception as e:
					debug("\nInvalid URL:" + line.replace('\n',''), critical=True)
					#raise e
					new_newfile = new_newfile + line
					#print("WHOOPS there was an error!")
					return
				temp_string = add_json_to_subscribe(json_test)
				
				self.text_input_new_url.clear()

				#If the downloader is running, add the subscription just created to the list for the downloaders to grab
				if self.running:
					print("ADDING A THING WHILE RUNNING")
					watch_subscription_or_dont(json_test)

				#Update the debug field if there's feedback,
				if temp_string != None:
					self.set_label_text_register(temp_string)
				#Otherwise, blank it.
				else:
					self.set_label_text_register("Enter URLs here and press 'Register' to add them to your subscriptions.")
					
			else:
				if domain == None:
					self.set_label_text_register("Invalid URL")
				else:
					self.set_label_text_register("No handler for: " + domain)

	def widget_register_url(self):
		self.form_register_url = QGroupBox("Register new URL")
		layout = QFormLayout()

		self.text_input_new_url = QLineEdit()
		self.button_register_url = self.createButton("Register", self.click_process_new_url)
		layout.addRow(self.button_register_url, self.text_input_new_url)

		self.label_new_url_debug = QLabel("Enter URLs here and press 'Register' to add them to your subscriptions.")
		layout.addRow(self.label_new_url_debug)

		self.form_register_url.setLayout(layout)

	##
	#Running Bamboodl Update
	##

	def run_downloader(self):
		self.running = True

		#2 Spawn Fetch threads for everything, run through regular link list by date, seeing if wait time has been reached, and if so spawn a Fetch thread
		self.set_label_text_download("Preparing to download. . .")
		check_everything()
		spawn_downloaders()

		#3 Wait for those threads to join again~
		self.append_label_text_download("Downloading. . .")
		join_downloaders()
		self.append_label_text_download("Done downloading.")

		self.running = False

	def set_label_text_download(self, new_text):
		self.label_download_debug.setText(new_text)

	def append_label_text_download(self, new_text):
		self.label_download_debug.setText(self.label_download_debug.text() + '\n' + new_text)

	def click_process_download(self):

		if self.running:
			pass
		else:
			self.thread_download = threading.Thread( group=None, target=self.run_downloader, name=None, args=(), kwargs={}, daemon=True )
			self.thread_download.start()

	def widget_download(self):
		self.form_download_urls = QGroupBox("Download subscribed threads")
		layout = QFormLayout()

		self.button_download = self.createButton("Normal Update", self.click_process_download)
		layout.addRow(self.button_download)

		self.label_download_debug = QLabel("Press the button above to download updates to the threads you've subscribed to.")
		layout.addRow(self.label_download_debug)

		self.form_download_urls.setLayout(layout)

	##
	#Original Code
	##

if __name__ == '__main__':

	import sys

	debug_enable()

	#1 Load user settings and subscription object
	load_user_settings()
	print("Settings loaded...")
	load_subscribe_object()
	print("Current Subscriptions loaded...")

	app = QApplication(sys.argv)
	dialog = Dialog()

	dialog.exec_()

	print("Saving updated subscription data...")
	save_subscribe_object()

	sys.exit()
