import pandas as pd
import numpy as np
from selenium import webdriver
from lxml import html
import time
import getpass
import re
import matplotlib.pyplot as plt


class wodup:

    def __init__(self, email, password, url, chrome_driver_path='../src/chromedriver'):
        self.url = url
        self.email=email
        self.password=password
        self.browser = webdriver.Chrome(chrome_driver_path)
        self.browser.get(url)
        self.login()
        self.raw_logs = {}
        self.logs = {}
        
    def login(self):
        time.sleep(2)
        self.browser.find_element_by_xpath("//input[@name='username']").send_keys(self.email)
        self.browser.find_element_by_xpath("//input[@type='password']").send_keys(self.password)
        self.browser.find_element_by_xpath("//button[@type='submit']").click()

    def get_html_tree(self, movement):
        self.browser.get(f'{self.url}/movements/{movement}')
        time.sleep(3)
        return html.fromstring(self.browser.page_source)
        
    def get_log(self, movement):
        tree = self.get_html_tree(movement)
        df = pd.DataFrame({
            'date':tree.xpath('//span[@class="di dn-ns"]/text()'),
            'reps':tree.xpath('//span[@class="f6 fw7"]/text()'),
            'weights':tree.xpath('//div[@class="f6 truncate"]/text()')
        })
        
        self.raw_logs[movement] = df
    
    def clean_weights(self, x):
        return x.replace(' lbs', '').split(' – ')

    def clean_reps(self, x):
        x = x.strip()
        if re.match('\d\sx\s\d', x):
            x = '-'.join(int(x[0])*[x[-1]])
        elif ('1 Rep' in x)|('1RM' in x):
            x = '1'
        return x.split('-')
        
    def clean_logs(self):
        for k,v in self.raw_logs.items():
            movement_name = ' '.join([i.capitalize() for i in k.split('-')])
            df = v[v['reps'].apply(lambda x: x.startswith(movement_name))].copy()
            df.loc[:,'reps'] = df['reps'].apply(lambda x: x[len(movement_name):])
            df.loc[:,'date'] = df['date'].apply(lambda x: (pd.Timestamp.today() - pd.DateOffset(days=1)).strftime('%d %b') if x=='Yesterday' else x)
            df.loc[:,'date'] = pd.to_datetime(df['date']+'2020')
            df.loc[:,'month'] = df['date'].dt.month
            df.loc[:,'month-1'] = df['month'].shift()
            df.loc[:,'offset'] = (df['month-1'] < df['month']).cumsum().apply(lambda x: pd.DateOffset(years=x))
            df.loc[:,'date'] = df['date'] - df['offset']
            
            # clean reps and weights 
            df['reps_list'] = df['reps'].apply(self.clean_reps)
            df['weights_list'] = df['weights'].apply(self.clean_weights)
            
            # explode 1 RM day reps
            for i in df.iterrows():
                if len(i[1]['reps_list']) == 1:
                    df.loc[i[0],'reps_list'] = '-'.join(i[1]['reps_list']*len(i[1]['weights_list']))
                elif len(i[1]['reps_list']) < len(i[1]['weights_list']):
                    df.loc[i[0],'reps_list'] = '-'.join(i[1]['reps_list'] + ['Extra']*(len(i[1]['weights_list'])-len(i[1]['reps_list'])))
                elif len(i[1]['reps_list']) > len(i[1]['weights_list']):
                    df.loc[i[0],'reps_list'] = '-'.join(i[1]['reps_list'][:len(i[1]['weights_list'])])
                    
            # convert the exploded strs to list
            df.loc[:,'reps_list'] = df['reps_list'].apply(lambda x: x.split('-') if type(x) != list else x)
            
            for i in df.iterrows():
                for idx, r in enumerate(i[1]['reps_list']):
                    # For clusters, take first rep
                    if re.match('\d.\d', r):
                        df.loc[i[0],'reps_list'][idx] = int(r.split('.')[0])
                    if r == '':
                        df.loc[i[0],'reps_list'][idx] = 0
                        
                # If rep data is available in weights as r x w, overwrite reps data with r and remove r from weights
                for idx, w in enumerate(i[1]['weights_list']):
                    if 'x' in w:
                        df.loc[i[0],'reps_list'][idx] = int(max((w.split('x')[0]).split('.')))
                        df.loc[i[0],'weights_list'][idx] = int(w.split('x')[1])
                        
            self.logs[k] = df[['date', 'reps', 'weights', 'reps_list', 'weights_list']].copy()
            
    def gen_hist(self, movement):
        df = self.logs[movement].copy()
        df_w = df.explode('weights_list').reset_index().drop(columns=['index']).reset_index()[['index', 'date', 'weights_list']]
        df_r = df.explode('reps_list').reset_index().drop(columns=['index']).reset_index()[['index', 'reps_list']]
        df_hist = df_w.merge(df_r, on='index', how='inner', validate='one_to_one')[['date', 'weights_list', 'reps_list']].rename(columns={'reps_list':'reps', 'weights_list':'weights'})
        df_hist = df_hist.astype({'reps':int, 'weights':int})
        return df_hist