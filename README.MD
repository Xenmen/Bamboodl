
Bamboodl - The Culture Archiver
===============================

This is Bamboodl, or "Bamboo DL"/"Bamboo Downloader", a tool for archiving 8chan threads and more. You put thread URLs in a text file, run the script, and it adds them to your "Subscribed Threads" list. It downloads the threads' JSON, then grabs all the media (images, webms, pdfs, etc). 4chan threads are also supported.

There is a config file located at '~/_python/bamboodl' (~ being your user directory, C:/Users/&lt;name&gt; on Windows, /home/&lt;name&gt; on Linux, etc), where you can change the path threads are downloaded to. In the future, the config path will be changed to '~/.python/bamboodl', but since OSX makes it difficult to access hidden folders I'm holding off until I can add several more features to Bamboodl.

By default, Bamboodl downloads threads to '~/bamboodl'. You can change that in the config file, 'bamboodl.json'.

In the future, this project will include a 'thread browser'; an HTML file that you open, and use to browse your local archive as if it was a live imageboard.

There is some additional information, and pictures, available at:

http://daniel.tadeuszow.com/index.html#/projects/bamboodl

This is the first public release, which I meant to do much earlier. Since a lot of people have asked for an 8chan archiver, I'm sharing Bamboodl early, since it works quite well in its current state. Bamboodl will be compatible with Tumblr, Newgrounds, Deviantart, and many more sites, and have many more features, as I have time to implement them. Some sites (like Newgrounds) already work in my internal build, but the code is lousy, and needs cleanup before I share publically.

Additionally, if you would like an archiver for 4chan with more features than Bamboodl has presently, bibanon's is the best I know of:

https://github.com/bibanon/BA-4chan-thread-archiver

^It's capable of polling a thread continuously (one at a time per-instance) until it 404's. Bamboodl cannot yet do this, but when it gets a graphical interface, I can multithread Bamboodl and make real-time thread watching a reality.

I'm confused
============

If you don't know how to access your home (~) directory, or all this 'directory' stuff is kind of a mystery to you, and you're on Windows and just want this stuff to work, open an Explorer window, and on the left side click your C drive. Then double click the 'Users' folder (on XP, 'Documents and Settings'). Then, double click the folder with your account name. There, you're in!

To learn more about what a home directory is, and why I use '~' instead of a full path, check the following link:

https://en.wikipedia.org/wiki/Home_directory

Requirements
============

Bamboodl requires Python 3.4+, and one package from the Python Package Index.

If you know what that means, then just run the following line in your console, and you're ready to go:

'pip3 install beautifulsoup4'

If you don't know what Python or Pypi are, but you're still interested in archiving 8chan threads, then here are some instructions for getting up to speed on Windows. I can write instructions for other platforms such as OSX if requested:

Visit this link and download Python 3.4, or higher: https://www.python.org/downloads/

Python 3.4 includes Pip, the python package installer, so now all you need to do is install Beautiful Soup. Open the Windows command line by holding Windows Key + R on your keyboard, or click on 'Run' in your Start Menu. If you're on Windows 8, you should be able to get access to the commandline by entering 'cmd' at the Home Screen.

Once you have a console window open, type the following line, and press enter:

'pip3 install beautifulsoup4'

Note: On some platforms, Python 3 will install with 'pip' instead of 'pip3'. If you've installed Python 3 and 'pip3' doesn't do anything, run the command without the '3'.

Remember how to open the command console window! You will need that to run Bamboodl, until I create a friendly interface.

Adding Threads to Download
==========================

The 'new URLs' file is located at '~/_python/bamboodl/new.txt'. Add new URLs to new lines, save the file, run Bamboodl, and they'll be added and checked.

Be sure to have one URL per line. The following URL styles are all valid:

https://boards.4chan.org/tg/thread/39969383

https://boards.4chan.org/tg/thread/39969383/

http://boards.4chan.org/tg/thread/39969383/that-guygm

http://8ch.net/tg/res/103166.html

http://8ch.net/tg/res/103166.json

^It doesn't matter whether the URLs have http or https, Bamboodl will convert them to https when it processes the links.

When Bamboodl processes the file, links that it recognizes and are properly formatted will be removed from 'new.txt', and added to 'subscribed.json'.

If a URL is not recognized, or is formatted incorrectly, the link will be left in the file for you to correct or remove.

Running Bamboodl with multiple versions of Python installed
===========================================================

If you have Python 2.x and Python 3.x both installed, you will need to make sure Bamboodl is run by Python 3.4 or higher. On Linux, you should already have a dedicated command, 'python3'. On Windows, you will have to create that command yourself. Open an Explorer window, and go to 'C:\Python3', then copy 'python.exe' and name the copy 'python3.exe'.

Once that's done, you can use the same instructions as below, but use 'python3 bamboodl.py' instead of 'python bamboodl.py'. You can also run bamboodl by doubse clicking 'win.bat' on Windows, or running 'lin.sh' on a Linux desktop.

Running Bamboodl if you only have Python 3 installed
====================================================

You can run Bamboodl by double-clicking 'bamboodl.py', or by dragging 'bamboodl.py' into a console window and pressing enter. The advantage to the latter is that the console window will stay open long enough for you to see any error messages, or if any threads have 404'd. You can also open a console window, navigate to your Bamboodl folder (the one containing 'bamboodl.py', 'bambootil.py', 'xenutils.py', etc), and enter 'python bamboodl.py'. On some Linux distributions, you may need to enter 'python3' instead of just 'python'.

Bamboodl will first check 'new.txt' for new links, as described above, and create records for those URLs in 'subscribed.json'. When that's done, it'll check each URL's record, and see if enough time has passed since the last time that URL was checked. If so, it'll download that page, and all its media. Then it'll update the URL record, changing the 'last checked' field, and if the thread was updated, it'll update that field too.

Features and How It Works
=========================

Bamboodl stores all URLs and their metadata in a json file, located at '~/_python/bamboodl/subscribed.json'.

Bamboodl uses 4chan's and 8chan's JSON interface, to put less strain on their networks and run faster.

Bamboodl knows better than to check every thread you're subscribed to every time you run it. Bamboodl records the last time each URL was checked, the last time a post/update was made, and the minimum time to wait until Bamboodl checks that URL again. Every time Bamboodl checks that URL, and there hasn't been an update, Bamboodl increases the amount of time it'll wait until it checks again. If there *has* been an update, it'll reset the wait time to the minimum amount. These wait times are currently per-domain, and you can check the times in 'bamboovar.py'.

Bamboodl has a function called 'reprocess_the_dead()'. If your Internet connection fizzled out while Bamboodl was running, don't worry, just open 'bamboodl.py', and uncomment that line in the bamboodl_run() block (remove the '#' at the beginning of the line). Then, just run Bamboodl, and it'll recheck all the URLs flagged as dead. Note: Over time the number of dead URLs can become quite large, and you *don't* want to needlessly recheck a bunch of genuinely 404'd threads. I will add functionality later for periodically moving these genuinely dead links into a separate file, as a manual command and to be done automatically after several successful runs with no 404'd threads.
