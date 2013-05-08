feeder
======

*feeder* is the simplest possible RSS reader. You export you subscriptions.xml
from Google Reader and run this program. *feeder* opens all unread entries in
your browser and saves the stuff you've read in `read.txt`.

This little program is the result of my very specific, very simple needs. I
have a dozen RSS feeds that I read daily, in their entirety, in only one device,
without using folders or stars or anything. If this is not your case, please be
very careful and review the source code before running it.


Pros
----

- doesn't depend on external servers and can't be shutdown

- easy to review items you have read and your feed list

- trivial exporting to other services

- no required input

- easily extensible

- plays well with sync software


Cons
-----------

- no pretty feed titles, stars, folders, tags or comments

- no social features whatsoever

- "mark as unread" is a manual action

- uses very stupid regexes to parse the feeds

- `read.txt` can get large (I'll add automatic trimming later on)

- if you miss an item and it falls off the feed list, it's lost for good

- takes a moment to fetch all feeds

- no preview, opens everything regardless of your opinion
