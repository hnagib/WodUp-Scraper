import pandas as pd
from selenium import webdriver
from lxml import html
import time
import re
import numpy as np


class WodUp:

    def __init__(self, email, password, url, chrome_driver_path='../src/chromedriver'):
        """

        :param email: Email address login for WodUp
        :param password: WodUp login password
        :param url: url for profile/user to scrape
        :param chrome_driver_path: path to chromedriver executable
        """
        self.url = url
        self.email=email
        self.password=password
        self.browser = webdriver.Chrome(chrome_driver_path)
        self.browser.get(url)
        self.login()
        self.raw_logs = {}
        self.logs = {}
        
    def login(self):
        """
        Sign into WodUp using self.email and self.password
        """
        time.sleep(2)
        self.browser.find_element_by_xpath("//input[@name='username']").send_keys(self.email)
        self.browser.find_element_by_xpath("//input[@type='password']").send_keys(self.password)
        self.browser.find_element_by_xpath("//button[@type='submit']").click()

    def get_html_tree(self, movement, wait=1.5):
        """
        Get html tree for a given movement
        :param movement: movement to pull html for
        :param wait: wait to load page
        :return:
        """
        self.browser.get(f'{self.url}/movements/{movement}')
        time.sleep(wait)
        return html.fromstring(self.browser.page_source)
        
    def get_log(self, movement):
        """
        The xpaths pull data for strengh and metcon workouts in a list.

        :param movement: movement to pull data for
        :return:
            Store raw output to self.raw_logs dictionary under the movement key
        """
        tree = self.get_html_tree(movement)
        df = pd.DataFrame({
            'date':tree.xpath('//span[@class="di dn-ns"]/text()'),
            'reps':tree.xpath('//span[@class="f6 fw7"]/text()'),
            'weights':tree.xpath('//div[@class="f6 truncate"]/text()')
        })
        
        self.raw_logs[movement] = df
    
    def gen_weights_list(self, x):
        """
        Take out "lbs" from the end of the string and split using dashes.
        e.g. [35 - 35 - 50 - 90 lbs] --> [35,35,50,90]

        :param x: String containing weights used in the workout
        :return:
            list of weights
        """
        return x.replace(' lbs', '').split(' – ')

    def gen_reps_list(self, x):
        """
        Generate reps list. Usually this shows up as "8-8-5-5-3-2-1". However, sometimes this will contain "1 Rep" or
        "1RM" to indicate a one rep max workout. Sometimes it might also be present in "Reps x Sets" format. e.g. 3 x 5.
        In that scenario convert it to "3-3-3-3-3" first and then split by '-' to get [3,3,3,3,3].

        :param x:
        :return:
            list of reps
        """
        x = x.strip()
        if re.match('\d+\sx\s\d+', x):
            x = '-'.join(int(x[0])*[x[-1].strip()])
        elif ('1 Rep' in x)|('1RM' in x):
            x = '1'
        return x.split('-')
    
    def clean_date(self, x):
        """
        Date data comes in as Day, Month formant. e.g. "18 Aug". Yesterday's workouts are logged as "Yesterday".
        Replaces this with yesterday's date and adds current year to all date. Note that the year in the outout of this
        function is not correct as the current year is applied to all dates. This is fixed by fix_date_year() function.

        :param x: html scraped date strings. e.g "18 Aug"
        :return:
            DateTime object corresponding to x
        """
        if x=='Yesterday':
            out = (pd.Timestamp.today() - pd.DateOffset(days=1)).strftime('%d %b')
        elif x=='Today':
            out = pd.Timestamp.today().strftime('%d %b')
        else:
            out = x
            
        out = pd.to_datetime(out+str(pd.Timestamp.today().year))
        return out
    
    def fix_date_year(self, df):
        """
        The html scraped dates come in descending order without year. Every time the month value increases,
        it indicates a year change. e.g. months: 2, 1, 12  means row corresponding to month 12 is December of last year.
        Use this increase to indicate rows where a year adjustment needs to be applied. Note: This method will not work
        if data is too sparse.

        :param df: dataframe with data as DateTime objects
        :return:
            df with year correction
        """
        df.loc[:,'month'] = df['date'].dt.month
        df.loc[:,'month-1'] = df['month'].shift()
        df.loc[:,'offset'] = (df['month-1'] < df['month']).cumsum().apply(lambda x: pd.DateOffset(years=x))
        df.loc[:,'date'] = df['date'] - df['offset']
        return df
    
    def equalize_reps_and_weights(self, df):
        """
        Check to see if reps and weights lists are of euqal lengths. If not, adjust them to be equal. There are several
        reasons why they may not be equal:
            - 1 rep max workout
            - Did extra work beyond workout plan --> len(weights_list) > len(reps_list)
            - Didn't complete all sets --> len(weights_list) < len(reps_list)

        :param df: DataFrame with reps_list and weights_list columns
        :return:
            DataFrame with reps_list and weights_list that are of equal lengths
        """
        # Convert un-equal length lists into strings
        for i in df.iterrows():
            if len(i[1]['reps_list']) == 1:
                df.loc[i[0],'reps_list'] = '-'.join(i[1]['reps_list']*len(i[1]['weights_list']))
            elif len(i[1]['reps_list']) < len(i[1]['weights_list']):
                df.loc[i[0],'reps_list'] = '-'.join(i[1]['reps_list'] + ['Extra']*(len(i[1]['weights_list'])-len(i[1]['reps_list'])))
            elif len(i[1]['reps_list']) > len(i[1]['weights_list']):
                df.loc[i[0],'reps_list'] = '-'.join(i[1]['reps_list'][:len(i[1]['weights_list'])])

        # Convert the exploded strs back to list
        df.loc[:,'reps_list'] = df['reps_list'].apply(lambda x: x.split('-') if type(x) != list else x)
        return df
    
    def clean_rep_list(self, df):
        """
        Take max of clustered reps in clusters. e.g. "4.2" should be counted as 4 reps. Impute missing or empty data
        with 0

        :param df: DataFrame with reps_list
        :return: DataFrame with cleaned up reps_list
        """
        for i in df.iterrows():
            for idx, r in enumerate(i[1]['reps_list']):
                # For clusters, take first rep
                if re.match('\d.\d', r):
                    df.loc[i[0],'reps_list'][idx] = int(max(r.split('.')))
                if r == '':
                    df.loc[i[0],'reps_list'][idx] = 0 
        return df
    
    def clean_weight_list(self, df):
        """
        Sometimes reps data is embedded in weights items. e.g. "25 - 5x35 - 3x50 lbs". Here the rep data for 25 lbs
        will be in reps_list, but for 35 and 50lbs, the reps in reps_list need to be overwritten by 5 and 3 respectively.

        :param df: DataFrame with weights_list
        :return: DataFrame with cleaned up weights_list
        """
        for i in df.iterrows():
            # If rep data is available in weights as r x w, overwrite reps data with r and remove r from weights
            for idx, w in enumerate(i[1]['weights_list']):
                if 'x' in w:
                    df.loc[i[0],'reps_list'][idx] = int(max((w.split('x')[0]).split('.')))
                    df.loc[i[0],'weights_list'][idx] = int(w.split('x')[1])
                if w == 'No sets completed':
                    df.loc[i[0],'weights_list'][idx] = 0
        return df
    
    def clean_log(self, movement):
        """
        Add cleaned up version of self.raw_logs[movement] to self.logs[movement]

        :param movement: movement string. e.g. "back-squat"
        :return: Cleaned up version of self.raw_logs[movement] that's stored in self.logs[movement]
        """
        movement_name = ' '.join([i.capitalize() for i in movement.split('-')])
        #print(f'cleaning {movement_name} data...')

        # Get movement logs
        df = self.raw_logs[movement].copy()
        
        # Exclude Metcon workouts
        df = df[df['reps'].apply(lambda x: x.startswith(movement_name))].copy()

        # Fix date column
        df.loc[:,'date'] = df['date'].apply(self.clean_date)
        df = self.fix_date_year(df)

        # Remove movement name string prefix
        df.loc[:,'reps'] = df['reps'].apply(lambda x: x[len(movement_name):])

        # Generate reps and weights lists
        df['reps_list'] = df['reps'].apply(self.gen_reps_list)
        df['weights_list'] = df['weights'].apply(self.gen_weights_list)
        df = self.equalize_reps_and_weights(df)

        # Clearn rep and weight list items
        df = self.clean_rep_list(df)
        df = self.clean_weight_list(df)
        
        clean_log_cols = ['date', 'reps', 'weights', 'reps_list', 'weights_list']
        self.logs[movement] = df[clean_log_cols]

        return df[clean_log_cols]

    def clean_all_logs(self):
        """
        Iterate through all movements found in self.raw_logs and clean the logs and populate self.logs
        """
        for movement in self.raw_logs.keys():
            self.clean_log(movement)
            
    def gen_movement_hist(self, movement):
        """
        Explodes the self.logs[movement] DataFrame. This view is useful for generating lift charts

        :param movement: movement string. e.g. "front-squat"
        :return: Exploded self.logs[movement] DataFrame
        """
        df = self.logs[movement].copy()
        df_w = df.explode('weights_list').reset_index().drop(columns=['index']).reset_index()[['index', 'date', 'weights_list']]
        df_r = df.explode('reps_list').reset_index().drop(columns=['index']).reset_index()[['index', 'reps_list']]
        df_hist = df_w.merge(df_r, on='index', how='inner', validate='one_to_one')[['date', 'weights_list', 'reps_list']].rename(columns={'reps_list':'reps', 'weights_list':'weights'})
        df_hist = df_hist.astype({'reps':float, 'weights':float})
        return df_hist

    def gen_pr_table(self, movement, monotonize=True):
        """
        Generate PR table for a given movement. PR table should be monotonic. e.g. If you can do 8 reps as 225, then
        you should be able to do 7 reps at 225 as well.

        :param movement: movement string. e.g. "front-squat"
        :return: PR table
        """
        df_pr = self.gen_movement_hist(movement).groupby('reps').max()

        if monotonize:
            df_pr['weights'] = np.maximum.accumulate(df_pr.weights.sort_index(ascending=False))

        return df_pr

    def gen_all_pr_tables(self):
        """
        :return: Generate PR tables for all movements with clean logs.
        """
        tables = []
        for movement in self.logs.keys():
            df_pr = self.gen_pr_table(movement, monotonize=True)
            df_pr.columns = ['date', movement]
            tables.append(df_pr)

        return pd.concat(tables, axis=1)