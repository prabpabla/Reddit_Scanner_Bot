# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 14:19:43 2021

@author: prab_pabla


"""

import praw
import re
import pandas as pd
import copy

class ScannerBot:
    """
    A class used to query a given subreddit for stock ticker symbols
    Creates a list of regular expression matched stock ticker symbols
    Returns a compared directory with the NASDAQ stock exchange, filtered and sorted
    
    ...
    
    Attributes
    ----
    compare_file_name : str
        NASDAQ csv file name (provided by user)
    subreddit_name : str
        Subreddit name (provided by user)
    client_id : str
        Reddit client ID (provided through reddit)
    client_secret : str
        Reddit client secret (provided through reddit)
    user_agent : str
        Reddit user name (provided through reddit)
    query_size : int
        Query size for number of recent subreddit threads (default is 10)
    regex_pattern : str
        Regual expression for pattern match (default is "\$[A-Z]{2,7}|[A-Z]{2,4}")
    min_stock_freq : int
        Minimum number of stock counts to remove (default is 1)
    ignore_list : list
        List of stock ticker symbols to be remove (default is ['RSI'])
    
    
    Methods
    ----     
    stock_count()    
        Returns the final subreddit directory of querried, filtered and sorted stock ticker symbols and count
    """
    
    def __init__(self,compare_file_name,subreddit_name,
                 client_id = None,
                 client_secret = None,
                 user_agent = None,
                 query_size = 10, 
                 regex_pattern = "\$[A-Z]{2,7}|[A-Z]{2,4}",
                 min_stock_freq = 1,
                 ignore_list = ['RSI']):
        """
        Parameters
        ----
        compare_file_name : str
            NASDAQ csv file name (provided by user)
        subreddit_name : str
            Subreddit name (provided by user)
        client_id : str
            Reddit client ID (provided through reddit)
        client_secret : str
            Reddit client secret (provided through reddit)
        user_agent : str
            Reddit user name (provided through reddit)
        query_size : int
            Query size for number of recent subreddit threads (default is 10)
        regex_pattern : str
            Regual expression for pattern match (default is "\$[A-Z]{2,7}|[A-Z]{2,4}")
        min_stock_freq : int
            Minimum number of stock counts to remove (default is 1)
        ignore_list : list
            List of stock ticker symbols to be remove (default is ['RSI'])
        """
        self = self
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__user_agent = user_agent
        self.subreddit_name = subreddit_name
        self.query_size = query_size
        self.regex_pattern = regex_pattern
        self.compare_file_name = compare_file_name
        self.min_stock_freq = min_stock_freq
        self.ignore_list = ignore_list
        
        self.reddit = praw.Reddit( client_id = self.__client_id,
                 client_secret = self.__client_secret,
                 user_agent = self.__user_agent)
        
    def __stock_search(self, reg_pattern, string_name):
        """
        Performs a regular expression search on a string and cleans up eg. '$'

        Parameters
        ----
        reg_pattern : str
            Regular search expression
        string_name : str
            Text over which to perform pattern search
        
        Returns
        ----
        list
            List of all pattern matched results after cleanup
        """
        result = re.findall(reg_pattern, string_name)
        clean_result = []
        for stock in result:
            clean_result.append(re.sub("\$","", stock))   #['ABCD', 'DCBA']
        return clean_result
    
    def __subreddit_query(self):
        """
        Queries a certain number of most recent subreddit's title and comments for stock ticker symbol
                
        Returns
        ----
        list
            List of stock ticker symbol in subreddit
        """
        stock_list = []
        for submission in self.reddit.subreddit(self.subreddit_name).hot(limit=self.query_size):
            for comments in submission.comments:
                stock_body_list = (self.__stock_search(self.regex_pattern, comments.body)) 
                stock_list.extend(stock_body_list)
                stock_title_list = (self.__stock_search(self.regex_pattern, submission.title))
                stock_list.extend(stock_title_list)
                
        return stock_list
    
    def __stock_count_sort(self, stock_list):
        """
        Performs stock count on the passed list, and sorts it in descending order
        Removes any stocks with a count of one
        
        Parameters
        ----
        stock_list : list
            List of stocks ticker symbols 
        
        Returns
        ----
        dict
            Directory of stock ticker symbols and its accompanying count
        """
        stock_dict = {}
        for stock in stock_list:
            if stock_list.count(stock) > self.min_stock_freq:    
                if stock not in stock_dict:
                    stock_dict[stock] = stock_list.count(stock)
                
        stock_dict_sorted = sorted(stock_dict.items(), key = lambda x: x[1], reverse = True)
        stock_dict = dict(stock_dict_sorted)
        return stock_dict

    def __nasdaq_file_read(self):
        """
        Reads a csv file, and saves the stock ticker symbols to a list
       
        Returns
        ----
        list
            List of stock ticker symbols of all the stocks traded on the NASDAQ exchange
        """
        compare_file_read = pd.read_csv(self.compare_file_name, skiprows = 0, usecols = ['Symbol'])
        compare_file_list = []
        for index in range(len(compare_file_read)):   
            compare_file_list.append(compare_file_read.iloc[index,0])
        return(compare_file_list)

    def __stock_compairson(self, stock_count_dict, nasdaq_list):
        """
        Compares the subreddit queried stock ticker symbols directory with NASDAQ list and ignore list
        Removes and stock ticker symbols not found in the NASDAQ list, or in the ignore list
        
        Parameters
        ----
        stock_count_dict : dict
            Directory of subreddit stock ticker symbols
        nasdaq_list : list
            List of NASQAD exchange stock ticker symbols
        
        Returns
        ----
        dict
            Directory of stock ticker symbols after compairson
        """
        stock_dict = {}
        for stock in stock_count_dict:   
            if (stock in nasdaq_list) and (stock not in self.ignore_list):
                stock_dict[stock] = stock_count_dict[stock]
                #a = {}
                #a[stock] = stock_count_dic[stock]
                #stock_dic.update(stock_count_dic[stock] == [stock])
        return(stock_dict)
    
    def __stock_compairson_deep(self, stock_count, nasdaq_list):
        """
        Compares the subreddit queried stock ticker symbols directory with NASDAQ list and ignore list
        Removes and stock ticker symbols not found in the NASDAQ list, or in the ignore lsist
        
        Parameters
        ----
        stock_count_dict : dict
            Directory of subreddit stock ticker symbols
        nasdaq_list : list
            List of NASQAD exchange stock ticker symbols
        
        Returns
        ----
        dict
            Directory of stock ticker symbols after compairson
        """
        stock_dict = copy.deepcopy(stock_count)
        for stock in stock_count:   
            if (stock not in nasdaq_list) or (stock in self.ignore_list):
                stock_dict.pop(stock)
        return(stock_dict)
    
    def stock_count(self):
        """
        Calls __subreddit_query, __stock_count_sort, __nasdaq_file_read, __stock_compairson 
        
        Returns the final subreddit directory of querried, filtered and sorted stock ticker symbols and count
        
        Returns
        ----
        dict
            Final directory of stock ticker symbols and count
        """
        stock_list = self.__subreddit_query()   
        stock_count = self.__stock_count_sort(stock_list)
        nasdaq_list = self.__nasdaq_file_read()
        stock_comp = self.__stock_compairson(stock_count, nasdaq_list)
        return stock_comp
        
    def __write_cvs (self, stock_comp):
        """
        Writes the final subreddit directory as a cvs file
        
        Parameters
        ----
        stock_comp : dict
            Final directory of stock ticker symbols and count
        """
        stock_dict = stock_comp
        #stock_cvs_keys = list(stock_dict.keys())
        #stock_cvs_value = list(stock_dict.values())
        stock_dict_item = list(stock_dict.items())
        #print(stock_dict_item)
        stock_cvs_list = pd.DataFrame(stock_dict_item)
        stock_cvs_list.to_csv("reddit_stock_screener.csv",index=False,header=("Stocks","Count")) 
    