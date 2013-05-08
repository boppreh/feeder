import os
import re
import requests
from itertools import starmap

class Feed(object):
    """
    Class for each individual feed source.
    """
    items_read = None
    read_file_path = 'read.txt'

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.entries = None

    def pull(self):
        """
        Returns the most recent feed contents, read or not.
        """
        content = requests.get(self.url).content

        if '<entry>' in content:
            item_regex = '<entry[^>]*>(.+?)</entry>'
            link_regex = '<link[^>]+?href="([^"]+)"[^>]*/?>'
        elif '<item>' in content:
            item_regex = '<item>(.+?)</item>'
            link_regex = '<link[^>]*>(.+?)</link>'

        for item_text in re.findall(item_regex, content, re.DOTALL):
            yield re.findall(link_regex, item_text, re.DOTALL)[0].strip()

    def is_read(self, link):
        """
        Returns True if `link` has already been marked as read.
        """
        if Feed.items_read is None:
            if os.path.exists(Feed.read_file_path):
                Feed.items_read = set(open(Feed.read_file_path).read().split())
            else:
                Feed.items_read = set()

        return link in Feed.items_read

    def unread(self):
        """
        Returns all unread entries.
        """
        if self.entries is None:
            self.entries = self.pull()

        for entry in self.entries:
            if not self.is_read(entry):
                yield entry

    def mark_as_read(self, entry):
        """
        Mark an entry as read, storing this information in the read file.
        """
        Feed.items_read.add(entry)
        with open(Feed.read_file_path, 'a') as read_file:
            read_file.write(entry + '\n')

    def __str__(self):
        return 'Feed({} [{}])'.format(self.name, self.url)

def import_feeds(subscription_path='subscriptions.xml'):
    """
    Import Google Reader subscriptions file.
    """
    with open(subscription_path) as subscription_file:
        content = subscription_file.read()
        titles = re.findall('title="(.+?)"', content)
        urls = re.findall('xmlUrl="(.+?)"', content)
        return list(starmap(Feed, zip(titles, urls)))

if __name__ == '__main__':
    if os.path.exists(Feed.read_file_path):
        do_display = True
    else:
        print "It seems this is the first time you are running feeder."
        print "As you have no entries read, all your feeds will be open in "
        print "your browser, which may be a overwhelming."
        print ""
        print "Do you want to mark all entries as read, starting in a clean"
        print "slate? (Y/n)"
        do_display = raw_input().lower() != 'n'

    import webbrowser

    for feed in import_feeds():
        print feed.name
        for entry in feed.unread():
            print entry
            if do_display:
                webbrowser.open(entry)
            feed.mark_as_read(entry)
