feeder
======

*feeder* is the simplest possible RSS reader. You export you subscriptions.xml
from Google Reader and run this program. *feeder* opens all unread entries in
your browser and saves the stuff you've read in `read.txt`.

This little program is the result of my very specific, very simple needs. I
have a dozen RSS feeds that I read daily, in their entirety, in only one device,
without using folders or stars or anything.

**WARNING**
-----------

`read.txt` is just a list of the URLs seen, there is no "mark as unread", no
follow or star or comment or tag or folder, and the first time you run it it'll
open *everything* in your feeds unless you comment that line from the (tiny)
source code. Also, it uses very stupid regexes to parse the feeds.
