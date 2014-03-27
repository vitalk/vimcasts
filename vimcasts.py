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
    """

    def __init__(self, number, title, url):
        self.number = number
        self.title = title
        self.url = url

    def blob(self):
        """Lazy loaded binary object."""
        try:
            return urllib2.urlopen(self.url).read()
        except urllib2.URLError:
            pass

    def save(self, formatstr='{number}. {title}'):
        """Save the episode to location.

        :param formatstr: The format string uses to create episode location.
        """
        path = formatstr.format(number=episode.number, title=episode.title)
        ensure_dir_exists(path)
        with open(path, 'wb') as a_file:
            a_file.write(self.blob())


class Episodes(object):
    """An iterator that helps to retrieve all available Vimcast episodes.

    :param starts_from: The number of episode to start from
    :param video_format: The preferred video format to fetch

    Example::

       for episode in Episodes(starts_from=42, video_format='m4v'):
           episode.save('Vimcasts/{number}. {title}')

    """

    # The format string uses to create episode location
    formatstr = 'http://media.vimcasts.org/videos/{episode}/{filename}'

    def __init__(self, starts_from, video_format='m4v'):
        """Initialize episode generator."""
        self.video_format = video_format
        self.starts_from = self.last_episode = starts_from

    def __iter__(self):
        """Create an iterator."""
        return self

    def __next__(self):
        """Python 3 compatibility."""
        return self.next()

    def next(self):
        """Iterate over available episodes."""
        if self.next_episode_exists():
            return self.next_episode()
        else:
            raise StopIteration()

    def next_episode(self):
        """Returns an instance of :class:`Episode`. Ensure that next episode
        exists before call.
        """
        filename = self.get_next_episode_filename()
        url = self.get_next_url(filename)
        episode = Episode(self.last_episode, filename, url)
        self.last_episode += 1
        return episode

    def get_next_url(self, filename=''):
        return self.formatstr.format(episode=self.last_episode, filename=filename)

    def get_next_episode_filename(self):
        html = self.response.read()
        m = re.search('href=\"(.*{})\"'.format(self.video_format), html)
        return m.group(1)

    def next_episode_exists(self):
        try:
            self.response = urllib2.urlopen(self.get_next_url())
        except urllib2.URLError:
            print 'No more episodes exist'
            return False
        return True


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Retrieve Vimcasts (http://vimcasts.org) episodes.')
    args = parser.parse_args()

    for episode in Episodes(starts_from=64):
        print 'Loading episode #{} from {}'.format(episode.number, episode.url)
        episode.save(formatstr='Vimcasts/{number}-{title}')
