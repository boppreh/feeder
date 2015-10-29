import os
import re
import requests
import webbrowser
from html.parser import HTMLParser
import sys

def fetch(url):
    """
    Returns the entries in a given feed address.
    """
    content = requests.get(url).text

    if 'twitter.com' in url:
        return [i for i in re.findall('href="([^"]+)"', content) if 't.co' in i]

    elif '</html>' in content:
        text = re.sub('<.+?>', '', content)
        return ['{}#{}'.format(url, hash(text))]

    else:
        if '<entry>' in content:
            item_regex = '<entry[^>]*>(.+?)</entry>'
            link_regex = '''<link[^>]+?href=.([^'"]+)'''
        elif '<item>' in content:
            item_regex = '<item>(.+?)</item>'
            link_regex = '<link[^>]*>(.+?)</link>'
        else:
            print('Unknown feed format ({}):'.format(url), file=sys.stderr)
            print(content, file=sys.stderr)
            return

        for item_text in re.findall(item_regex, content, re.DOTALL):
            link = re.findall(link_regex, item_text, re.DOTALL)[0].strip()
            yield HTMLParser().unescape(link)

def open_all_unread(feed_url, ignore, entries_read):
    """
    Opens the unread items from a feed url. Items are considered read if they
    are in the `ignore` set, and `entries_read` is updated with the entries
    seen.
    """
    entries = list(fetch(feed_url))
    unread = list(reversed([entry for entry in entries
                            if entry not in ignore]))

    if len(unread) > 5:
        print('{} has {} unread entries.'.format(feed_url, len(unread)))
        print('Do you want to open all (o), mark as read (r) or ignore (i)?')
        option = input('(o/r/I)').lower()
        if option == 'r':
            entries_read.update(entries)
            return
        elif option == 'i':
            # Migrate the previously read items from the old set to the new
            # one. Since we don't know which entries belong to which feeds,
            # include everything.
            entries_read.update(ignore)
            return

    for entry in unread:
        #print('Opening ', entry)
        webbrowser.open(entry)
        entries_read.add(entry)

def bounded_parallel_run(function, args, max_concurrent=8):
    """
    Runs `functions` in parallel threads, with up to `max_concurrent` threads
    at the same time. Roughly equivalent to ThreadPoolExecutor in Python 3k.
    """
    from threading import Thread, Semaphore

    threads = []
    semaphore = Semaphore(max_concurrent)

    def run_locked(function, arg):
        semaphore.acquire()
        function(arg)
        #print('.', sep='', end='', file=sys.stderr)
        semaphore.release()
        
    #print('#' * len(args), file=sys.stderr)
    for arg in args:
        thread = Thread(target=run_locked, args=(function, arg))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    feeds_urls = set(filter(len, open('feeds.txt').read().split('\n')))
    entries_file = open('read.txt', 'r+')
    entries_read = set(filter(len, entries_file.read().split('\n')))

    def process_feed(feed_url):
        try:
            unread = reversed([entry for entry in fetch(feed_url)
                               if entry not in entries_read])
            for entry in unread:
                print(entry)
                entries_read.add(entry)
        except:
            print('Error processing ' + feed_url, file=sys.stderr)
            raise

    bounded_parallel_run(process_feed, feeds_urls)

    entries_file.seek(0)
    entries_file.write('\n'.join(sorted(entries_read)))
    entries_file.truncate()
