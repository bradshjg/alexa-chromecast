import subprocess
import threading
import urllib
import urllib2

import alexandra
import click
from bs4 import BeautifulSoup
import pychromecast


app = alexandra.Application()


@click.group()
def cli():
    pass


@cli.command()
def server():
    app.run('127.0.0.1', 8000)


def _cast(query):
    chromecast = pychromecast.get_chromecast(friendly_name='Grover')
    escaped_query = urllib.quote(query)
    url = "https://www.youtube.com/results?search_query=" + escaped_query
    response = urllib2.urlopen(url)
    html = response.read()
    search_results = BeautifulSoup(html, 'html.parser')
    video_paths = map(lambda url: url['href'], search_results.findAll(attrs={'class':'yt-uix-tile-link'}))
    for path in video_paths:
        if path.startswith('/watch?'):
            video_url = 'https://www.youtube.com' + path
            break
    print video_url
    to_play = subprocess.check_output("youtube-dl -g -- " + video_url, shell=True)
    chromecast.media_controller.play_media(to_play, 'video/mp4')


@cli.command()
@click.option('--query', help="search query", required=True)
def cast(query):
    """Cast Youtube video"""
    _cast(query)


@app.intent('SendVideo')
def play_video(slots, session):
    query = slots['query']
    thread = threading.Thread(target=_cast, args=(query,))
    thread.start()
    return alexandra.respond("Now playing %s" % query)


if __name__ == "__main__":
    cli()

