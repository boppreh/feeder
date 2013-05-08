import os
import re
import requests
from HTMLParser import HTMLParser

class Feed(object):
    """
    Class for each individual feed source.
    """
    items_read = None
    read_file_path = 'read.txt'
    feeds_file_path = 'feeds.txt'

    @staticmethod
    def all_feeds():
        """
        Returns all feeds from the feeds file.
        """
        with open(Feed.feeds_file_path) as feeds_file:
            return map(Feed, feeds_file.read().split())

    @staticmethod
    def load_read_entries():
        """
        Loads the list of entries read.
        """
        if os.path.exists(Feed.read_file_path):
            Feed.items_read = set(open(Feed.read_file_path).read().split())
        else:
            Feed.items_read = set()

    def __init__(self, url):
        self.url = url
        self.entries = None

    def pull(self):
        """
        Returns the most recent feed contents, read or not.
        """
        content = requests.get(self.url).content

        if '<entry>' in content:
            item_regex = '<entry[^>]*>(.+?)</entry>'
            link_regex = '''<link[^>]+?href="|'([^"']+)"|'[^>]*/?>'''
        elif '<item>' in content:
            item_regex = '<item>(.+?)</item>'
            link_regex = '<link[^>]*>(.+?)</link>'

        for item_text in re.findall(item_regex, content, re.DOTALL):
            link = re.findall(link_regex, item_text, re.DOTALL)[0].strip()
            yield HTMLParser().unescape(link)

    def is_read(self, link):
        """
        Returns True if `link` has already been marked as read.
        """
        if Feed.items_read is None:
            Feed.load_read_entries()

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

def import_feeds(subscription_path):
    """
    Import Google Reader subscriptions file and write the feeds found to the
    feeds file.
    """
    with open(subscription_path) as subscription_file:
        content = subscription_file.read()

    urls = re.findall('xmlUrl="(.+?)"', content)

    with open(Feed.feeds_file_path, 'a') as feeds_file:
        feeds_file.write('\n'.join(urls) + '\n')

if __name__ == '__main__':
    if os.path.exists(Feed.read_file_path):
        do_display = True
    else:
        print "It seems this is the first time you are running feeder."
        print "As you have no entries read, all your feeds will be open in "
        print "your browser, which may be overwhelming."
        print ""
        print "Do you want to mark all entries as read, starting in a clean"
        print "slate? (Y/n)"
        do_display = raw_input().lower() == 'n'

    import webbrowser

    if os.path.exists('subscriptions.xml'):
        import_feeds('subscriptions.xml')
        os.rename('subscriptions.xml', 'subscriptions (already imported).xml')

    for feed in Feed.all_feeds():
        print feed.url
        for entry in feed.unread():
            print entry
            if do_display:
                webbrowser.open(entry)
            feed.mark_as_read(entry)
