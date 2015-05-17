
#Bamboodl Graphical Version

This version of Bamboodl is run has a GUI built in PyQT5. It is bundled with the [console version](tutorial_console.md#bamboodl-console-version).

##Requirements

The graphical version requires all the same setup as the console version, so be sure to follow [those steps](tutorial_console.md#requirements) first. Then, to install PyQT5 and use the graphical version, visit the [PyQT website](http://www.riverbankcomputing.com/software/pyqt/download5) and download the proper installer for your platform (note: most major Linux distributions have PyQT in their package managers). 

##Adding Threads to Download

The graphical version will process `new.txt` just like the console version, but you can also enter URLs directly in the GUI. Start up Bamboodl graphical version as explained below, enter yoru thread's URL in the text field, and press 'Register'. That's it! When you run the downloader it will be downloaded, and when you exit Bamboodl you will see the URL added to `subscribed.json`. If the URL you enter isn't valid, it will not be processed, and you will see a debug message below the text field.

##Running

Running the graphical version is very similar to running the [console version](tutorial_console.md#requirements). Make sure you understand how to run *that*, and then just substitute `bamboodl.py` in the commands with `bamboogui.py`. That's it!

Once you have the Bamboodl window up, paste new URLs into the text field under 'Register New URL', and hit 'Register' to register them. Then, hit 'Normal Update' to download the threads you've subscribed to. You will get debug messages for both underneath their respective interfaces.

Have fun, and happy archiving!
