#!/usr/bin/python

import datetime
import requests
import re
import time
import sys

from lxml import etree
from random import randint
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

HOST = 'XXXX'
PREFIX = 'http://'
URL = 'XXXX'

XPATH_RESULTS_TABLE = '//*[@id="DataGrid1"]'
XPATH_HIDDEN_INPUT_TOKEN = '/html/body/form/input'
XPATH_ORIG_SELECT ='//*[@id="drpOrigin"]'

TABLE_HEADERS = ['ORIG', 'FLT#', 'DEST', 'DEP-DATE', 'DEP-TIME',
                        'ARR-DATE', 'ARR-TIME', 'A/C']

GET_HEADERS = {
        'Host': 'www2.alpa.org',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        }

POST_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;  q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Host': 'www2.alpa.org',
        'Referer': 'http://www2.alpa.org/fdx/jumpseat/Default.aspx',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0',
        }


class Client:
    """
    Provides some methods to interact with Alpa's website
    """
    def __init__(self):
        self.host = HOST
        self.baseurl = PREFIX + HOST
        self.url = self.baseurl + URL


    def get_date_from_input_file(self):
        '''
        Reads the date from an input file. It must be in the first line.
        The format must be xx-xx-xxxx
        '''
        # with statement automatically closes the file when the block ends
        with open('date.txt') as datefile:
            date = datefile.readline().strip()

        if not re.match('\d\d-\d\d-\d\d\d\d', date):
            raise Exception, 'date.txt must contain one date xx-xx-xxxx'

        return date


    def get_initial_data(self, celery_task=None):
        """
        Do a GET request and parse it to get the hidden input token and the
        list of possible departure airports. Returns a dict.
        """
        if celery_task and not celery_task.default_retry_delay == 180:
            raise Exception, 'celery_task must be a celery task'

        r = requests.get(self.url, headers=GET_HEADERS)

        # Wait between 5 and 10 seconds after each request
        print 'GET request done, waiting 5 seconds and parsing data...'
        meta_dict = {'status':   'running',
                     'progress': '1',
                     'info':     'GET request done, ' +
                                 'waiting 5 seconds and parsing data...',}
        if celery_task:
            celery_task.update_state(state="PROGRESS", meta=meta_dict)
        time.sleep(randint(5, 10))

        html = etree.HTML(r.text)
        hidden_input = html.xpath(XPATH_HIDDEN_INPUT_TOKEN)[0]
        originating_in_select = html.xpath(XPATH_ORIG_SELECT)[0]
        token = hidden_input.get('value')
        opts = originating_in_select.xpath('option')
        c = len(opts)
        print 'This will take around', c*10/60, 'minutes (' + str(c), 'locations)'
        if celery_task:
            meta_dict = {
                    'status':   'running',
                    'progress': '1',
                    'info':     'This will take around ' + str(c*10/60) +
                                ' minutes (' + str(c) + ' airports)',}
            celery_task.update_state(state="PROGRESS", meta=meta_dict)
        results = {'token': token, 'departure_airports': opts,}
        return results


    def get_flights_originating_from_all_airports_in_one_date(self, date,
            celery_task=None):
        '''
        Returns a list of rows with all the data. meta is an optional dict
        which will be updated with progress info.
        '''

        if not re.match('\d\d-\d\d-\d\d\d\d', date):
            raise Exception, 'date must be in the format xx-xx-xxxx'
        if celery_task and not celery_task.default_retry_delay == 180:
            raise Exception, 'celery_task must be a celery task'

        payload = {}

        # Do GET request to get initial data
        try:
            initial_data = self.get_initial_data(celery_task=celery_task)
        except:
            raise Exception('Could not get initial data, ' +
            'Is the site up and running? ' +
            'Are you connected to the internet?')

        # Fields for the other two forms
        today_str = datetime.date.strftime(datetime.date.today(), "%m/%d/%Y")
        payload['drpArrive'] = 'ABE'
        payload['drpFrom'] = 'ABE'
        payload['drpTo'] = 'ABE'
        payload['drpLegs'] = '3'
        payload['Text1'] = '0'
        payload['Text2'] = '5'
        payload['Text3'] = '12'
        payload['drpOn2'] = today_str
        payload['drpOn3'] = today_str

        # These fields seem to be sending the coordinates of the mouse pointer
        # relative to the image button. Make them random
        payload['ImageButton1.x'] = randint(5, 35)
        payload['ImageButton1.y'] = randint(5, 35)

        date = re.sub('-', '/', date)
        date = re.sub('-', '/', date)
        payload['drpOn1' ] = date

        # Hidden input token
        payload['__VIEWSTATE'] = initial_data.get('token')

        # Get data for all originating airports
        tables = {}
        total = len(initial_data.get('departure_airports'))
        count = 0
        for airport in initial_data.get('departure_airports'):
            count += 1
            percentage = count * 100 / total
            payload['drpOrigin'] = airport.get('value')
            r = requests.post(self.url, data=payload, headers=POST_HEADERS)
            if celery_task:
                meta_dict = {
                        'status': 'running',
                        'progress': percentage,
                        'info': 'Locations: <span style="text-align:left;">'
                        + str(total) + '</span><br />Loaded: ' +
                        '<span style="text-align:left;">' + str(count) +
                        '<br />Left: <span style="text-align:left;">' +
                        str(total - count) + '         &#8776 ' +
                        str((total - count) * 10 / 60) + ' minutes</span>',
                }
                celery_task.update_state(state="PROGRESS", meta=meta_dict)
            #sys.stdout.write(
            #        'POST request for ' + payload['drpOrigin'] + ' done, ' +
            #        str(total - count) + ' left (' + str(percentage) +
            #        '%)            \r')
            #sys.stdout.flush()
            time.sleep(randint(5, 10))
            html = etree.HTML(r.text)
            try:
                tables[airport.get('value')] = html.xpath(XPATH_RESULTS_TABLE)[0]
            except:
                pass

        print

        #TODO: include a check to confirm that tabe headers match

        res = self.join_tables(tables)
        return res


    def join_tables(self, tables):
        '''
        Builds a single table with all the data.

        @param tables       Dict with keys=airport names and values=html tables

        @return             List of rows
        '''
        results = [TABLE_HEADERS,]
        for airport, table in tables.items():
            for row in table.xpath('tr')[1:]:
                temp_dict = {'ORIG': airport,}
                for i, cell in enumerate(row.xpath('td')):
                    key = table.xpath('tr')[0].xpath('td')[i].text
                    temp_dict[key] = cell.text

                results.append([temp_dict.get(item) for item in TABLE_HEADERS])

        return results


    def write_to_file(self, row_list):
        date = re.sub('/', '-', self.get_date_from_input_file())
        with open('results.fedex.' + date + '.txt', 'wb') as f:
            for row in row_list:
                f.write(','.join(row) + '\n')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        print 'This script takes no arguments'
        sys.exit(1)
    else:
        c = Client()
        date = c.get_date_from_input_file()
        rows = c.get_flights_originating_from_all_airports_in_one_date(date)
        c.write_to_file(rows)

