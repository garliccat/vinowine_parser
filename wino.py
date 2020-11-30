# parser for vinowine.ru

import requests
from bs4 import BeautifulSoup as bs
import string
import datetime
import csv
import random
import time


def get_html(url):
    user_agent_list = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.3.136 Yowser/2.5 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
    ]

    try:
        r = requests.get(url, headers={'User-Agent': random.choice(user_agent_list)}, timeout=10)
    except:
        print('unable to reach page')
        return None

    return r.text


def write_csv(data):
    with open('alcohol.csv', 'a', newline='', encoding='UTF-8') as f:
        #newline - to avoid blank rows after each record
        #encoding utf-16 - we are in russia, thats all`
        writer = csv.writer(f, delimiter=';')
        writer.writerow(data)


def get_data(html):
    if html == None:
        print('Page: {} access denied'.format(html))
        return None

    soup = bs(html, 'lxml')
    try:
        items_count = soup.find('div', {'class': 'ItemsCount'}).get_text(strip=True).strip().split(' ')[-1]
        items_count = int(items_count.strip())
        print('Items count in category: {}\n'.format(items_count))
    except:
        return None
    
    item_number = 1
    page_number = 1

    while item_number <= items_count:

        global url
        print(url + '?page={}'.format(page_number))
        soup = bs(get_html(url + '?page={}'.format(page_number)), 'lxml')

        try:
            cards = soup.find_all('div', {'class':'Item'})
            print('Cards on page {} - {}'.format(page_number, len(cards)))
            
            for card in cards:
                title, price, item_type, item_country, item_color, item_alc, item_age, item_volume, item_raw, item_class = '', '', '', '', '', '', '', '', '', ''

                print('Item number: {}'.format(item_number))
                try:
                    title = card.find('div', {'class': 'ItemName'}).get_text(strip=True)
                except:
                    continue
                print('Title: {}'.format(title))

                try:
                    price = card.find('div', {'class': 'ItemPrice'}).find_all('div')[1].contents[0].replace('₽', '').replace(',', '').strip()
                except:
                    price = ''
                print('Price: {}'.format(price))

                for item_feat in card.find('div', {'class': 'ItemNames'}).find_all('div', {'class': 'ItemFeat'}):
                    try:
                        feature = item_feat.contents[0].lower()
                        # print(feature)
                        if 'тип:' in feature:
                            item_type = item_feat.contents[1].get_text(strip=True).lower()
                            print('Type: {}'.format(item_type))
                        elif 'страна' in feature:
                            item_country = item_feat.contents[1].get_text(strip=True).lower()
                            print('Country: {}'.format(item_country))
                        elif 'цвет:' in feature:
                            item_color = item_feat.contents[1].get_text(strip=True).lower()
                            print('Color: {}'.format(item_color))
                        elif 'крепость' in feature:
                            item_alc = item_feat.get_text().split()[-1].replace('%', '')
                            print('Alcohol: {}'.format(item_alc))
                        elif 'выдержка' in feature:
                            item_age = item_feat.contents[1].get_text(strip=True).lower().split()[0]
                            print('Age: {}'.format(item_age))
                        elif 'сырье:' in feature:
                            item_raw = item_feat.contents[1].get_text(strip=True).lower()
                            print('Raw: {}'.format(item_raw))
                        elif 'классификация:' in feature:
                            item_class = item_feat.contents[1].get_text(strip=True).lower()
                            print('Class: {}'.format(item_class))
                    except:
                        pass

                try:
                    item_volume = card.find_all('div', {'class': 'ItemFeats'})[-1].find('div', {'class': 'ItemAllPrices ItemAllPricesCheck ItemAllPricesCheckOn'}).get_text(strip=True).split()[0]
                except:
                    item_volume = ''
                print('Volume: {}'.format(item_volume))

                print('\n')

                item_number += 1

                write_csv([title, price, item_type, item_country, item_color, item_alc, item_age, item_volume, item_raw, item_class])

            page_number += 1

        except:
            return None


def main():
    drinks = ['vino', 'shampanskoe', 'igristoe-vino', 'konyak', 'viski', \
        'vodka', 'distillat', 'pivo', 'armanyak', 'brandy', 'kalvados', \
        'grappa', 'schnaps', 'dzhin', 'rom', 'tequila', 'sake', 'liqueur', 'absent', 'nastoyka']

    for i in drinks:
        global url
        url = 'https://www.vinowine.ru/{}/'.format(i)
        get_data(get_html(url))
    

if __name__ == '__main__':
    main()
