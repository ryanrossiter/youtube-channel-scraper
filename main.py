#####################
#
# YouTube Channel Scraper
# Author: Ryan Rossiter <https://github.com/ryanrossiter>
#
# This script will scrape queries from Channel Crawler (https://www.channelcrawler.com/),
# check if the YouTube channel has an email available, and then it will output a CSV of
# the scraped channels.
#
# Usage:
#   python3 main.py <ChannelCrawler Request ID> <CSV filename> [page limit] [start page]
#    - <ChannelCrawler Request ID>: The channel crawler request ID (see below to get one)
#    - <CSV filename>: Where the output csf should be written
#    - [page limit]: Max pages to fetch from channel crawler
#    - [start page]: Channel crawler page to start on
#
# To get a Channel Crawler request ID:
#  - Go to https://www.channelcrawler.com/ and perform a search with whatever parameters you need
#  - Take the URL of the results page, and copy the ID part (https://www.channelcrawler.com/eng/results/[ID IS HERE])
#
# WARNING: Part of this script will GET about pages from YouTube to check if there is a
#          business email available (via CAPTCHA). YouTube will rate limit these requests if
#          this script is run too many times. (Nothing a VPN can't solve 🙃)
#
#####################

import sys
import csv
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
import multiprocessing.pool
from tqdm import tqdm

CONCURRENT = 10
DEFAULT_PAGE_LIMIT = 20

EMAIL_REGEX = re.compile(r'((([^<>()\[\]\.,;:\s@\"]+(\.[^<>()\[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,}))', re.MULTILINE)

def print_usage():
  print("USAGE: %s <ChannelCrawler Request ID> <CSV filename> [page limit] [start page]" % sys.argv[0])

def check_if_yt_channel_has_business_email(channel_url: str):
  about_url = re.sub(r'/about$', '', channel_url) + '/about'
  try:
    about_contents = urlopen(about_url).read()
  except Exception:
    return False
  else:
    has_business_email = str(about_contents).find('"businessEmailLabel":') != -1
    return has_business_email

def fetch_channel_crawler_page(id, page=1):
  channels = [] # tuples of (title, href, category, description, subscribers, scraped_email, has_email_available)

  url = "https://www.channelcrawler.com/eng/results/%s/page:%d" % (id, page)
  with urlopen(url) as f:
    soup = BeautifulSoup(f, "html.parser", from_encoding="iso-8859-1")
    for el in soup.find_all('div', class_='channel'):
      title = el.h4.a.get('title')
      href = el.h4.a.get('href')
      category = el.small.b.get_text()
      description = el.find_all('a', recursive=False)[0].get('title')
      subscribers = el.p.small.contents[0].strip().replace(' Subscribers', '')

      email_re_match = EMAIL_REGEX.findall(description)
      scraped_email = email_re_match[0][0] if len(email_re_match) else None
      has_email_available = bool(scraped_email or check_if_yt_channel_has_business_email(href))
  
      channels.append((title, href, category, description, subscribers, scraped_email, has_email_available))
  
  return channels

def do_thread_work(ccid, page):
  try:
    channels = fetch_channel_crawler_page(ccid, page)
    return "success", page, channels
  except Exception as err:
    return "error", page, []


def write_channels_to_csv(channels, filename):
  with open(filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(channels)

def main(ccid, filename, start_page, end_page):
  print(f'Fetching pages {start_page}..{end_page} from Channel Crawler results ID {ccid}...')

  pool = multiprocessing.pool.ThreadPool(processes=CONCURRENT)

  work_fn = lambda p: do_thread_work(ccid, p)
  imap = pool.imap_unordered(work_fn, range(start_page, end_page))
  channel_lists = list(tqdm(imap, total=(end_page - start_page)))
  pool.close()

  print("Done.")
  
  channels = []
  for (status, page, data) in channel_lists:
    if status == "error":
      print(f"Page {page} encountered an error")
    else:
      channels.extend(data)

  write_channels_to_csv(channels, filename)

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print_usage()
  else:
    ccid = sys.argv[1]
    filename = sys.argv[2]
    page_limit = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_PAGE_LIMIT
    start_page = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    end_page = start_page + page_limit - 1

    main(ccid, filename, start_page, end_page)
