import os
import re
import requests
import webbrowser
import simplecrypto
from HTMLParser import HTMLParser

class Feed(object):
    """
    Class for each individual feed source.
    """
    entries_read = set()
    feeds = []

    @staticmethod
    def load_entries_read_list(path):
        """ Loads the entries from `path` into a static class attribute.  """
        Feed.entries_read = set(open(path).read().split())

    @staticmethod
    def load_feeds_list(path):
        """ Loads the feeds from `path` into a static class attribute.  """
        Feed.feeds = map(Feed, open(path).read().split())

    @staticmethod
    def save_all_entries(path):
        """ Saves all entries from the known feeds into `path`.  """
        entries = sum((feed.entries for feed in Feed.feeds), [])
        open(path, 'w').write('\n'.join(entries))
        # It overwrites the previous entries by design. Without this the
        # entries file would grow without limits.

    def __init__(self, url):
        """ Creates a new Feed object from a URL, starting with no entries. """
        self.url = url
        self.entries = []

    def fetch(self):
        """ Fetches and stores all entries from this feed's url. """
        content = requests.get(self.url).content
        if '</html>' in content:
            self.entries.append(self.url + '#' + simplecrypto.hash(content))
            return

        if '<entry>' in content:
            item_regex = '<entry[^>]*>(.+?)</entry>'
            link_regex = '''<link[^>]+?href=.([^'"]+)'''
        elif '<item>' in content:
            item_regex = '<item>(.+?)</item>'
            link_regex = '<link[^>]*>(.+?)</link>'
        else:
            print 'Unknown feed format:'
            print content
            raw_input()
            return

        for item_text in re.findall(item_regex, content, re.DOTALL):
            link = re.findall(link_regex, item_text, re.DOTALL)[0].strip()
            self.entries.append(HTMLParser().unescape(link))

    def open_all_unread(self):
        """
        Open all feed entries not in Feed.entries_read in a new webbrowser tab.
        """
        self.fetch()
        unread = list(reversed([entry for entry in self.entries
                                if entry not in Feed.entries_read]))

        if len(unread) > 5:
            print 'Feed {} has {} unread entries, which is a lot.'.format(self.url, len(unread))
            print 'Are you sure you want to open all those in your browser?'
            option = raw_input('(y/N)')
            if option != 'y':
                # Discard the entries unread.
                self.entries = list(Feed.entries_read.intersection(self.entries))
                return

        for entry in reversed(self.entries):
            if entry not in Feed.entries_read:
                webbrowser.open(entry)

def convert_feeds(subscription_path):
    """
    Import Google Reader subscriptions file and write the feeds found to the
    feeds file.
    """
    with open(subscription_path) as subscription_file:
        content = subscription_file.read()

    urls = re.findall('xmlUrl="(.+?)"', content)

    with open(Feed.feeds_file_path, 'a') as feeds_file:
        feeds_file.write('\n'.join(urls) + '\n')

def bounded_parallel_run(functions, max_concurrent=8):
    """
    Runs `functions` in parallel threads, with up to `max_concurrent` threads
    at the same time. Roughly equivalent to ThreadPoolExecutor in Python 3k.
    """
    from threading import Thread, Semaphore
    import sys

    threads = []
    semaphore = Semaphore(max_concurrent)

    def run_locked(function):
        semaphore.acquire()
        function()
        sys.stdout.write('.')
        semaphore.release()
        
    sys.stdout.write('#' * len(functions) + '\n')
    for function in functions:
        thread = Thread(target=run_locked, args=(function,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    # Convert subscriptions.xml into feeds.txt.
    if os.path.exists('subscriptions.xml'):
        convert_feeds('subscriptions.xml')
        os.rename('subscriptions.xml', 'subscriptions (already imported).xml')

    # Load feeds file.
    Feed.load_feeds_list('feeds.txt')

    if os.path.exists('read.txt'):
        # Common path, opens all unread entries.
        Feed.load_entries_read_list('read.txt')
        bounded_parallel_run([feed.open_all_unread for feed in Feed.feeds])
    else:
        # First execution path, doesn't open anything.
        print "`read.txt` not found, marking all feeds' items as read."
        for feed in Feed.feeds:
            print 'Loading entries from', feed.url
            feed.fetch()

    # Cleans entries file and save the new entries.
    Feed.save_all_entries('read.txt')
