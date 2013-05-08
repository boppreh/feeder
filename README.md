feeder
======

*feeder* is the simplest possible RSS reader. You export you subscriptions.xml
from Google Reader and run this program. *feeder* opens all unread entries in
your browser and saves the stuff you've read in `read.txt`.

This little program is the result of my very specific, very simple needs. I
have a dozen RSS feeds that I read daily, in their entirety, in only one device,
without using folders or stars or anything. If this is not your case, please be
very careful and review the source code before running it.

Limitations
-----------

- `read.txt` is just a list of the URLs seen, of all feeds, chronologically

- there is no "mark as unread" (but you can change the file manually)

- there is no follow or star or comment or tag or folder

- uses very stupid regexes to parse the feeds

- feed titles displayed in console have no care about encodings

- `read.txt` can get very large (you can always remove the first items
  manually, though)
