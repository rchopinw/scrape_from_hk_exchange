from cfscrape import create_scraper
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from os.path import expanduser

web = create_scraper()
response = web.get(
    'https://www2.hkexnews.hk/New-Listings/New-Listing-Information/Main-Board?sc_lang=zh-HK'
)

print('Analyzing web response with html parser...')
bs = BeautifulSoup(response.text, 'html.parser')

print('Has the CSS path of the website table body has been changed? y/n')
x = str(input())

if x == 'n':
    path = '#pagecontent_0_pageContent > div > div > table > tbody'
else:
    print('Please input the new CSS path...')
    path = str(input())

print('...Executing...')
path += ' > tr'

companies = bs.select(path)

print('Initializing downloader, need alternative path? y/n \n')
print('If no, the default path will be set to Desktop...')
x = str(input())
if x == 'y':
    print('Please input a path...')
    download_path = str(input())
else:
    download_path = expanduser('~/Desktop')

for i, c in enumerate(companies):
    info = c.select('td')
    if not info:
        continue
    try:
        name = info[1].text
        link = info[3].select('a')[0]['href']
        file_format = link.split('.')[-1]
    except Exception as ex:
        print('Error encountered: {} \n'.format(ex))
        print('Continuing...')
        continue
    print(
        'Currenting downloading: Company: {} | File format: {} | Process: {}/{}'.format(
            name, file_format, i, len(companies) - 1
        )
    )
    try:
        urlretrieve(
            link,
            '{}/{}.{}'.format(download_path, name, file_format))
    except Exception as ex:
        print('Error encountered when downloading: {} \n'.format(ex))
        print('Download Link: {} \n'.format(link))
        print('Continuing...')
        continue



