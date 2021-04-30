# YouTube Channel Scraper

This script will scrape queries from [Channel Crawler](https://www.channelcrawler.com/),
check if the YouTube channel has an email available, and then it will output a CSV of
the scraped channels.

## Usage
```python3 main.py <ChannelCrawler Request ID> <CSV filename> [page limit] [start page]```
 - `<ChannelCrawler Request ID>`: The channel crawler request ID (see below to get one)
 - `<CSV filename>`: Where the output csf should be written
 - `[page limit]`: Max pages to fetch from channel crawler
 - `[start page]`: Channel crawler page to start on

### Getting A Channel Crawler Request ID
 - Go to [Channel Crawler](https://www.channelcrawler.com/) and perform a search with whatever parameters you need
 - Take the URL of the results page, and copy the ID part (`https://www.channelcrawler.com/eng/results/[ID IS HERE]`)

## ⚠️⚠️ WARNING ⚠️⚠️
  Part of this script will GET about pages from YouTube to check if there is a
  business email available (via CAPTCHA). YouTube will rate limit these requests if
  this script is run too many times. (Nothing a VPN can't solve 🙃)