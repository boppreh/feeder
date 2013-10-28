import os
import re
import requests
import webbrowser
from html.parser import HTMLParser

def fetch(url):
    """
    Returns the entries in a given feed address.
    """
    content = requests.get(url).text

    if 'twitter.com' in url:
        return [i for i in re.findall('href="([^"]+)"', content) if 't.co' in i]

    elif '</html>' in content:
        import simplecrypto
        text = re.sub('<.+?>', '', content)
        return [url + '#' + simplecrypto.hash(text)]

    else:
        if '<entry>' in content:
            item_regex = '<entry[^>]*>(.+?)</entry>'
            link_regex = '''<link[^>]+?href=.([^'"]+)'''
        elif '<item>' in content:
            item_regex = '<item>(.+?)</item>'
            link_regex = '<link[^>]*>(.+?)</link>'
        else:
            print('Unknown feed format:')
            print(content)

        entries = []
        for item_text in re.findall(item_regex, content, re.DOTALL):
            link = re.findall(link_regex, item_text, re.DOTALL)[0].strip()
            entries.append(HTMLParser().unescape(link))

        return entries

def open_all_unread(feed_url, ignore, entries_read):
    """
    Opens the unread items from a feed url. Items are considered read if they
    are in the `ignore` set, and `entries_read` is updated with the entries
    seen.
    """
    entries = fetch(feed_url)
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
        print('.', sep='', end='')
        semaphore.release()
        
    print('#' * len(args))
    for arg in args:
        thread = Thread(target=run_locked, args=(function, arg))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    feeds_file = open('feeds.txt', 'r+')
    feeds_urls = set(filter(len, feeds_file.read().split('\n')))
    entries_file = open('read.txt', 'r+')
    entries_already_read = set(filter(len, entries_file.read().split('\n')))
    entries_read_now = set()

    def process_feed(feed_url):
        try:
            open_all_unread(feed_url, entries_already_read, entries_read_now)
        except:
            # Without this we would lose the list of items read for this feed.
            # It does persist _all_ read items, but we assume the issue will be
            # fixed in the future and the list will be trimmed back naturally.
            entries_read_now.update(entries_already_read)
            raise

    bounded_parallel_run(process_feed, feeds_urls)

    all_entries = entries_read_now.union(entries_already_read)

    entries_file.seek(0)
    entries_file.write('\n'.join(sorted(all_entries)))
    entries_file.truncate()
