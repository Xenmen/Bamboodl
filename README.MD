
#Graphical Version Released

Bamboodl now has a basic GUI using PyQT5. To use it, prepare its [dependencies](#requirements) and then visit its [tutorial page](tutorial_graphical.md#bamboodl-graphical-version).


#Bamboodl - The Culture Archiver

This is Bamboodl, aka *Bamboo Downloader*, a lightweight tool for archiving 8chan/4chan threads. You give it thread links, and it downloads them. Run Bamboodl again to fetch updates since the last time it was run.

Bamboodl will eventually be compatible with Tumblr, Newgrounds, Deviantart, PHPBB threads, and many more sites, and have many more features, as I have time to implement them. Some sites (like Newgrounds) already work in my internal build, but the code is lousy, and needs cleanup before public release.

If you have questions about Bamboodl that aren't answered on this page, check [this faq](faq_general.md#faq) for more information.

If you have questions about the future of Bamboodl, please read the [roadmap](faq_roadmap.md#roadmap) page.

Alternatively, if you would like an archiver for 4chan with more features than Bamboodl has presently, [bibanon's](https://github.com/bibanon/BA-4chan-thread-archiver) is the best I know of. It's capable of polling a thread continuously (one at a time per-instance) until it 404's, and downloading only thumbnails. Bamboodl cannot yet do this, but it's under consideration.

#Requirements

[Bamboodl in the console](tutorial_console.md#requirements) requires:

- [Python 3.4+](https://www.python.org/downloads/)

- [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/)

[The graphical version of Bamboodl](tutorial_graphical.md#requirements) additionally requires:

- [PyQT5](http://www.riverbankcomputing.com/software/pyqt/download5)

#Running

- `python3 bamboodl.py` for the [console version](tutorial_console.md)

- `python3 bamboogui.py` for the [graphical version](tutorial_graphical.md)

#The Basics

Bamboodl:

- Loads new URLs from `~/_python/bamboodl/new.txt`

- Stores all URLs and their metadata in a json file, located at `~/_python/bamboodl/subscribed.json`

- Records when a URL was last accessed, when it was last changed, how long to wait before it should check that URL again, and more

- Downloads all media in a thread, and does not overwrite files that have already been downloaded, saving you bandwidth

- Keeps records of URLs that are unaccessible/404'd, so if your Internet connection drops mid-download, you can `reprocess_the_dead()` and retry downloading them

- Uses 4chan's and 8chan's JSON interface, to put less strain on their networks and run faster

Before a URL ends up in `subscribed.json`, you must either put it in `new.txt` or in the URL Register field in the graphical version and register it. Then, run the console version (`bamboodl.py`) or press 'Normal Download' in the graphical version, and it adds them to `subscribed.json`, which is your 'subscribed threads' list. It then downloads the threads' JSON, grabs all the media (images, webms, pdfs, etc), and updates the records in `subscribed.json`. 8chan and 4chan threads are currently supported.

Bamboodl knows better than to check every thread you're subscribed to every time you run it. Bamboodl records the last time each URL was checked, the last time a post/update was made, and the minimum time to wait until Bamboodl checks that URL again. Every time Bamboodl checks that URL, and there hasn't been an update, Bamboodl increases the amount of time it'll wait until it checks again. If there *has* been an update, it'll reset the wait time to the minimum amount. These wait times are currently per-domain, and you can check the times in 'bamboovar.py'.

Bamboodl has a function called `reprocess_the_dead()`. If your Internet connection fizzled out while Bamboodl was running, don't worry, just open `bamboodl.py`, and uncomment that line in the `bamboodl_run()` block (remove the `#` at the beginning of the line). Then, just run Bamboodl, and it'll recheck all the URLs flagged as dead. Note: Over time the number of dead URLs can become quite large, and you *don't* want to needlessly recheck a bunch of genuinely 404'd threads. I will add functionality later for periodically moving these genuinely dead links into a separate file, as a manual command and to be done automatically after several successful runs with no 404'd threads.

#Confused?

If there's anything on this page you don't understand, visit [this faq page](faq_neophytes.md#help) for some clarification.

If you have more technical questions about Bamboodl, check [this faq](faq_general.md#faq) instead.
