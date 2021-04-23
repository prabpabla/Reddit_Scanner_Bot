# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 22:08:42 2021

@author: prab_

0) Fetch top 10 submissions for a subreddit
1) Fetch all comments for a submission
2) For each comment check if there is a stock in the comment 
3) Append stock to an array 

"""

import praw
import re
import pandas as pd
import copy



reddit = praw.Reddit(
    client_id=None,
    client_secret=None,
    user_agent=None,
)

"""
for submission in reddit.subreddit("learnpython").hot(limit=10):
    print(submission.title)
subreddit = reddit.subreddit("redditdev")
print(subreddit.display_name)
print(subreddit.title)
print(subreddit.description)
"""

def stock_search(regex_pattern, string_name):
    result = re.findall(regex_pattern, string_name)
    clean_result = []
    for stock in result:
        clean_result.append(re.sub("\$","", stock))   #['ABCD', 'DCBA']
    return clean_result

    
def subreddit_query(subreddit_name):
    stock_list = []
    for submission in reddit.subreddit(subreddit_name).hot(limit=query_size):
        for comments in submission.comments:
            stock_body_list = (stock_search(regex_pattern, comments.body))
            stock_list.extend(stock_body_list)
        stock_title_list = (stock_search(regex_pattern, submission.title))
        stock_list.extend(stock_title_list)
    return stock_list


def stock_count_sort(stock_list):   
    stock_dic = {}
    for stock in stock_list:
        if stock_list.count(stock) > min_stock_freq:    
            if stock not in stock_dic:
                stock_dic[stock] = stock_list.count(stock)
           
    stock_dic_sorted = sorted(stock_dic.items(), key = lambda x: x[1], reverse = True)
    stock_dic = dict(stock_dic_sorted)
    return stock_dic


def nasdaq_file_read(compare_file_name):
    compare_file_read = pd.read_csv(compare_file_name, skiprows = 0, usecols = ['Symbol'])
    compare_file_list = []
    for index in range(len(compare_file_read)):   
        compare_file_list.append(compare_file_read.iloc[index,0])
    return(compare_file_list)


def stock_compairson(stock_count_dic, nasdaq_list):
    stock_dic = {}
    for stock in stock_count_dic:   
        if (stock in nasdaq_list) and (stock not in ignore_list):
            stock_dic[stock] = stock_count_dic[stock]
            #a = {}
            #a[stock] = stock_count_dic[stock]
            #stock_dic.update(stock_count_dic[stock] == [stock])
    return(stock_dic)


def stock_compairson_deep(stock_count, nasdaq_list):
    stock_dic = copy.deepcopy(stock_count)
    for stock in stock_count:   
        if (stock not in nasdaq_list) or (stock in ignore_list):
            stock_dic.pop(stock)
    return(stock_dic)


def write_cvs(stock_comp):
    stock_dic = stock_comp
    #stock_cvs_keys = list(stock_dic.keys())
    #stock_cvs_value = list(stock_dic.values())
    stock_dic_item = list(stock_dic.items())
    #print(stock_dic_item)
    stock_cvs_list = pd.DataFrame(stock_dic_item)
    stock_cvs_list.to_csv("reddit_stock_screener.csv",index=False,header=("Stocks","Count")) 


subreddit_name = "Daytrading"
query_size = 10
regex_pattern = "\$[A-Z]{2,7}|[A-Z]{2,4}"
compare_file_name = "nasdaq_screener_stocks_short.csv"
min_stock_freq = 1
ignore_list = {'RSI', 'ING'}


stock_list = subreddit_query(subreddit_name)   
stock_count = stock_count_sort(stock_list)
nasdaq_list = nasdaq_file_read(compare_file_name)
stock_comp = stock_compairson(stock_count, nasdaq_list)
write_cvs(stock_comp)

print("Un-screened stock list from Subreddit:",subreddit_name, "\n", stock_list, "\n")
print("Sorted stock list with frequency count greater than", min_stock_freq, ":\n", stock_count, "\n")
#print("NASDAQ stock list: \n", nasdaq_file_read(compare_file_name), "\n")
print("NASDAQ and ignore list screened stock list: \n", stock_compairson(stock_count, nasdaq_list), "\n")

