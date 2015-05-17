
#Bamboodl Console Version

This version of Bamboodl is run in the commandline/terminal. It is bundled with the [graphical version](blob/master/tutorial_graphical.md#bamboodl-graphical-version).

##Requirements

Bamboodl requires Python 3.4+, and one package from the Python Package Index.

If you know what that means, then just run the following line in your console, and you're ready to go:

```pip3 install beautifulsoup4```

If you don't know what Python or Pypi are, but you're still interested in archiving 8chan threads, then here are some instructions for getting up to speed on Windows. I can write instructions for other platforms such as OSX if requested:

1. [Download Python 3.4, or higher](https://www.python.org/downloads/)

2. Python 3.4 includes Pip, the python package installer, so now all you need to do is install Beautiful Soup. Open the Windows command line by holding Windows Key + R on your keyboard, or click on 'Run' in your Start Menu. If you're on Windows 8, you should be able to get access to the commandline by entering 'cmd' at the Home Screen.

3. Once you have a console window open, type the following line, and press enter:
```pip3 install beautifulsoup4```

Note: On some platforms, Python 3 will install with `pip` instead of `pip3`. If you've installed Python 3 and `pip3` doesn't do anything, run the command without the '3'.

**Remember how to open the command console window!** You will need that to run Bamboodl, unless you use the graphical version.

To use the console version of Bamboodl, please visit its [dedicated tutorial page](blob/master/tutorial_graphical.md).

##Adding Threads to Download

The 'new URLs' file is located at `~/_python/bamboodl/new.txt`. Add new URLs to new lines, save the file, run Bamboodl, and they'll be added and checked.

Be sure to have one URL per line. The following URL styles are all valid:

- https://boards.4chan.org/tg/thread/39969383

- https://boards.4chan.org/tg/thread/39969383/

- http://boards.4chan.org/tg/thread/39969383/that-guygm

- http://8ch.net/tg/res/103166.html

- http://8ch.net/tg/res/103166.json

^It doesn't matter whether the URLs have http or https, Bamboodl will convert them to https when it processes the links.

When Bamboodl processes the file, links that it recognizes and are properly formatted will be removed from `new.txt`, and added to `subscribed.json`.

If a URL is not recognized, or is formatted incorrectly, the link will be left in the file for you to correct or remove.

##Running

Execute `bamboodl.py` with Python 3, and if it's the first time you've run it, it'll create its configuration files.

In your terminal, in the directory where you've saved Bamboodl, run `python3 bamboodl.py`. Alternatively, right-click `bamboodl.py`, select 'Open With', and select Python 3. (If that doesn't work, try just `python bamboodl.py`. Make sure you've followed the steps outlined above in [requirements](#requirements), and checked the [Python help page](blob/master/faq_python.md#python) for more information.)

Then, it'll load `new.txt` looking for new URLs to process. Lines with valid URLs will be removed and stored in `subscribed.json`.

If a URL has just been added, or its been a while since it's been checked, it will be added to the 'to check' list, and several threads will be spawned to download the threads and their media. Media that has already been saved will be skipped.

When that's done, the URL metadata will be updated and saved in `subscribed.json`.

Rinse and repeat! Add more URLs and keep downloading.
