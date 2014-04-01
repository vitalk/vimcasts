#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    vimcasts.py
    ~~~~~~~~~~~

    Provide a script to download Vimcasts (http://vimcasts.org/episodes/archive)
    episodes.

    :copyright: Vital Kudzelka <vital.kudzelka@gmail.com>
    :license: MIT
"""
import os
import re
import urllib2
from datetime import datetime


_feed_re = re.compile('\<item\>(.*?)\</item\>', re.DOTALL)
_item_re = re.compile('\<title\>(.*?)\</title\>(?=.*?\<enclosure url=\"(.*?)\").*?\<pubDate\>(.*?)\</pubDate\>', re.DOTALL)


video_formats = {
    'quicktime': 'm4v',
    'ogg': 'ogv',
}


def ensure_dir_exists(path):
    """Ensure directory exists and create it if necessary.

    :param path: The path to check.
    """
    path = os.path.dirname(path)
    if not os.path.exists(path):
        os.makedirs(path)


class Episode(object):
    """A Vimcast episode.

    :param number: Number of the episode
    :param title: Descriptive title
    :param url: The url to fetch episode from
    :param video_format: The video format of the episode
    """

    def __init__(self, number, title, url, video_format):
        self.video_format = video_format
        self.number = number
        self.title = title
        self.url = url

    @property
    def ext(self):
        """Returns the file extension based on :attr:`video_format`."""
        return video_formats.get(self.video_format, 'm4v')

    def blob(self):
        """Lazy loaded binary object."""
        try:
            return urllib2.urlopen(self.url).read()
        except urllib2.URLError:
            pass

    def save(self, formatstr='{number}. {title}.{ext}'):
        """Save the episode to location.

        :param formatstr: The format string uses to create episode location.
        """
        path = formatstr.format(number=self.number, title=self.title,
                                ext=self.ext)
        ensure_dir_exists(path)
        with open(path, 'wb') as a_file:
            a_file.write(self.blob())


class Episodes(object):
    """An iterator that helps to retrieve all available Vimcast episodes.

    :param starts_from: The number of episode to start from
    :param video_format: The preferred video format to fetch

    Example::

       for episode in Episodes(starts_from=42, video_format='quicktime'):
           episode.save('Vimcasts/{number}. {title}.{ext}')

    """

    # The format string uses to get feed
    feedformatstr = 'http://vimcasts.org/feeds/{video_format}'

    def __init__(self, starts_from, video_format='quicktime'):
        """Initialize episode generator."""
        self.video_format = video_format
        self.starts_from = starts_from

    def __iter__(self):
        """Parse a xml feed and iterate over results."""
        return iter(self.feed[self.starts_from-1:])

    @property
    def feed(self):
        try:
            xml = urllib2.urlopen(self.get_feed_url(self.video_format)).read()
        except urllib2.URLError:
            xml = ''
        return self.parse_feed(xml)

    def parse_feed(self, xml):
        res = [x for item in _feed_re.findall(xml) for x in _item_re.findall(item)]
        res = sorted(res, key=lambda x: datetime.strptime(x[2], '%a, %d %b %Y %H:%M:%S %Z'))
        return [Episode(idx, title, url, self.video_format)
                for idx, (title, url, added_at) in enumerate(res, start=1)]

    def get_feed_url(self, video_format):
        return self.feedformatstr.format(video_format=video_format)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Retrieve Vimcasts (http://vimcasts.org) episodes.')
    parser.add_argument('--starts-from', default=1, type=int,
                        help='the episode number to start from')
    parser.add_argument('--video-format', default='quicktime',
                        help='the video format to download (quicktime, ogg)')
    parser.add_argument('--formatstr', help='the format string to name each episode')
    args = parser.parse_args()

    for episode in Episodes(starts_from=args.starts_from,
                            video_format=args.video_format):
        print 'Loading episode #{} from {}'.format(episode.number, episode.url)
        episode.save(formatstr=args.formatstr)
