
#Python

#Running Bamboodl with multiple versions of Python installed

If you have Python 2.x and Python 3.x both installed, you will need to make sure Bamboodl is run by Python 3.4 or higher. On Linux, you should already have a dedicated command, `python3`. On Windows, you will have to create that command yourself. Open an Explorer window, and go to `C:\Python3`, then copy `python.exe` and name the new copy `python3.exe`.

Once that's done, you can use the same instructions as below, but use `python3 bamboodl.py` instead of `python bamboodl.py`. You can also run bamboodl by doubse clicking `win.bat` on Windows, or running `lin.sh` on a Linux desktop.

#Running Bamboodl if you only have Python 3 installed

You can run Bamboodl by double-clicking `bamboodl.py`, or by dragging `bamboodl.py` into a console window and pressing enter. The advantage to the latter is that the console window will stay open long enough for you to see any error messages, or if any threads have 404'd. You can also open a console window, navigate to your Bamboodl folder (the one containing `bamboodl.py`, `bambootil.py`, `xenutils.py`, etc), and enter `python bamboodl.py`. On some Linux distributions, you may need to enter `python3` instead of just `python`.

Bamboodl will first check `new.txt` for new links, as described above, and create records for those URLs in `subscribed.json`. When that's done, it'll check each URL's record, and see if enough time has passed since the last time that URL was checked. If so, it'll download that page, and all its media. Then it'll update the URL record, changing the 'last checked' field, and if the thread was updated, it'll update that field too.
