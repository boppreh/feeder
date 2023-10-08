import os
import re
import requests
import webbrowser
from html import unescape
import sys
import concurrent.futures

def fetch(url):
    """
    Returns the entries in a given feed address.
    """
    try:
        content = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
        } if 'tapas.io' in url else None, timeout=2).text
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        return []

    if 'twitter.com' in url:
        return [i for i in re.findall('href="([^"]+)"', content) if 't.co' in i]

    #elif '</html>' in content:
    #    text = re.sub('<.+?>', '', content)
    #    return ['{}#{}'.format(url, hash(text))]

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
            return []

        items = []
        for item_text in re.findall(item_regex, content, re.DOTALL):
            link = re.findall(link_regex, item_text, re.DOTALL)[0].strip()
            items.append(unescape(link))
        return sorted(set(items), key=lambda i: items.index(i))

def open_all_unseen(feed_url, ignore, entries_seen):
    """
    Opens the unseen items from a feed url. Items are considered seen if they
    are in the `ignore` set, and `entries_seen` is updated with the entries
    seen.
    """
    entries = list(fetch(feed_url))
    unseen = list(reversed([entry for entry in entries
                            if entry not in ignore]))

    if len(unseen) > 5:
        print('{} has {} unseen entries.'.format(feed_url, len(unseen)))
        print('Do you want to open all (o), mark as seen (r) or ignore (i)?')
        option = input('(o/r/I)').lower()
        if option == 'r':
            entries_seen.update(entries)
            return
        elif option == 'i':
            # Migrate the previously seen items from the old set to the new
            # one. Since we don't know which entries belong to which feeds,
            # include everything.
            entries_seen.update(ignore)
            return

    for entry in unseen:
        #print('Opening ', entry)
        webbrowser.open(entry)
        entries_seen.add(entry)

if __name__ == '__main__':
    feeds_urls = open('feeds.txt').read().strip().split('\n')
    with open('seen.txt', 'r+') as f:
        entries_seen = dict.fromkeys(filter(len, f.read().split('\n')))
    entries_new = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for feed_url in feeds_urls:
            futures.append(executor.submit(fetch, feed_url))
        for future in concurrent.futures.as_completed(futures):
            for entry in future.result():
                #print(entry)
                if entry not in entries_seen:
                    entries_new.append(entry)
                    entries_seen[entry] = True

    if entries_new:
        with open('seen.txt', 'a') as f:
            f.write('\n'.join(entries_new) + '\n')
        with open('new.txt', 'a') as f:
            f.write('\n'.join(entries_new) + '\n')
