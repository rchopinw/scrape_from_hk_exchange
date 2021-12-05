from os.path import expanduser
import random
import cfscrape
import numpy as np
import pandas as pd
import urllib
from collections import defaultdict, Counter
import json


class Scraper:
    def __init__(self):
        self.status = {
            'yss': 'LT',
            'sx': 'LP',
            'ch': 'W',
            'bjj': 'RJ',
            'clz': 'A'
        }
        self.status_name = {
            'LT': '已上市',
            'LP': '失效',
            'W': '撤回',
            'RJ': '被拒绝',
            'A': '处理中'
        }
        self.header = 'https://www1.hkexnews.hk/app/'

    def scrape(self, ):
        web = cfscrape.create_scraper()
        print('Please enter a year in 4 digits.')
        year = str(input())
        json_id = 1638657787440 + (-1)**random.randint(0, 1) * random.randint(0, 1000)
        response = web.get(
            'https://www1.hkexnews.hk/ncms/json/eds/app_{}_sehk_c.json?_={}'.format(
                year, json_id
            )
        )
        info = json.loads(
            response.text
        )
        update_date, content = info['uDate'], info['app']
        print('Last update date from website: {}.'.format(update_date))

        print('Please enter a starting date in 4 digits, e.g., 0423 indicates 23rd, April.')
        start_date = str(input())

        print('Please enter an ending date in 4 digits, e.g., 1201 indicates 1st, December.')
        end_date = str(input())

        start_date = year + start_date
        end_date = year + end_date

        # getting files between two dates
        formatted_content = [
            {'id': x['id'],
             'date': self.__rank_reference(x['d']),
             'company_name': x['a'],
             'status_code': x['s'],
             'status_name': self.status_name[x['s']],
             'full_file': x['ls'][0]['u1'],
             'partial_file': 0
             }
            for x in content
            if start_date <= self.__rank_reference(x['d']) <= end_date and x['ls']
        ]
        count = Counter(
            x['status_name'] for x in formatted_content
        )
        print(
            'Between {} and {}, '.format(start_date, end_date),
            ' '.join('{}: {} |'.format(x, y) for x, y in count.items())
        )

        # getting status
        print(
            'Please enter one or more status from the following: ',
            ''.join(
                '{}: {} | '.format(x, y)
                for x, y in zip(self.status.keys(), self.status_name.values())
            ),
            '\n',
            'For multiple input, please use comma to separate, e.g.: yss,sx'
        )
        status = input()
        status = {
            self.status[x.strip()]
            for x in status.split(',')
        }
        filtered_content = [
            x
            for x in formatted_content
            if x['status_code'] in status
        ]
        print('{} related file found.'.format(len(filtered_content)))

        # downloading
        print('Please input a download path in the form of /Users/bangxixiao/Desktop',
              ', or enter d to download directly to Desktop.')
        path = input()
        if path == 'd':
            path = expanduser('~/Desktop')
        for i, file in enumerate(filtered_content):
            print(
                'Downloading {} | {}/{}'.format(
                    file['company_name'], i, len(filtered_content)
                )
            )
            if file['full_file'] == '#':
                print(
                    'Unable to find corresponding pdf w.r.t. {}'.format(
                        file['company_name']
                    ),
                    ', it has the status of {}.'.format(
                        file['status_name']
                    )
                )
                continue
            d_path = path + '/{}_{}_{}.pdf'.format(
                file['date'], file['company_name'], file['status_name']
            )
            try:
                urllib.request.urlretrieve(
                    self.header + file['full_file'], d_path
                )
            except:
                print('Error encountered at: ', file)
                continue
        print('Done, file saved at {}.'.format(path))

    def __rank_reference(self, s):
        sp = s.split('/')
        return sp[2] + sp[1] + sp[0]
