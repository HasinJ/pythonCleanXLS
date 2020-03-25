
def sliceString(string,beginStr,endStr='nothing'):#default parameter, as used to find date
    startIndex = string.find(beginStr)+len(beginStr) #doesnt include beginStr
    if endStr=='nothing': #if there is no parameter for endStr
        return string[startIndex:]
    stopIndex = string.find(endStr,startIndex) #so it doesn't take beginStr into consideration, it solves the problem with having beginStr and endStr being the same string (like when finding PCnumber)
    output = string[startIndex:stopIndex]
    return output

import json
import pandas as pd
import os.path
import csv
import MySQLdb
from os import path
from bs4 import BeautifulSoup

#looking at the "output" file on github shows what's being parsed
#the output file contains the HTML DOM of what we're trying to extract from
# HTML DOM is made up of HTML/CSS to begin with, some javascript to add afterwards, and then javscript EVENTS to add whenever a user prompts for it

#text - grabs TEXT
#strip() - is a method, it strips the string (in this case the .text) from what's called 'whitespace' in webdev (you can inspect any page and see where whitespace is in a HTML DOM)

mydb = MySQLdb.connect(host='hasindatabase.c0v7lriogf7u.us-east-2.rds.amazonaws.com',
    user='admin',
    passwd='hasinmc11',
    db='hasindatabase')
cursor = mydb.cursor()

dir = fr'C:\Users\Hasin Choudhury\Desktop\pythonBeautifulSoupScrape'

f = open(dir + r'\Report.xls','rb') # 'rb' stands for read-binary, write-binary needs chmoding, this is necessary for the content to be readable by BeautifulSoup
content = f.read()
soup = BeautifulSoup(content,'html.parser')
mainHeaderText = soup.find(id='MainReportDiv').text.strip().split('Report Time')[0] #here I grab the main text from the div container with id ='MainReportDiv', split it from 'Report Time', and then select the left portion of the split (0)

data = []

#grabs first table since there are two tables and CSS
table = soup.find(class_='TableStyle') #again look at the 'output' file, the file contains more than just 1 table, and even includes the CSS, which is what we dont want, we just want the first table

#grabs business unit and then PC#
businessUnit = sliceString(mainHeaderText,'Business Unit','-')
#sliceString is my own function, so it doesn't repeat, it basically takes a portion of the string, by locating a portion of the string, 'Business Unit' and '-', and using them as a starting point and ending point respectively.
PCnumber = sliceString(businessUnit,' ',' ')

#grabs date
businessDate = sliceString(mainHeaderText,'Date','End')
date = sliceString(businessDate,' ')

#grabs count of the table without total rows
dataRows = table.findAll(True, {'class':['RowStyleData', 'RowStyleDataEven']})

#find (first) header row
rowHead = table.find(class_="RowStyleHead")
columns = rowHead.select('.CellStyle')

#main data
for count in range(len(dataRows)):
    dataCell = dict()
    dataCell['PC Number'] = PCnumber
    dataCell['Date'] = date
    for index in range(len(columns)):
        try:
            dataCell[columns[index].text.strip()] = dataRows[count].select('.CellStyle')[index]['dval']
        except: #if there is no value, then the data cell has to represent the item name
            dataCell[columns[index].text.strip()] = dataRows[count].select('.CellStyle')[index].text.strip()
    data.append(dataCell)
f.close()

#cleaning date string of slashes
date = date.replace('/','.')

#checks for .json existence
if path.exists(dir + fr'\{date}Output.json')==False: #f-string to differentiate files, r-string to change the use of backslashes (for absolute path)
    with open(dir + fr'\{date}Output.json','w') as f:
        json.dump(data,f)

#checks for dataframe export existence
if path.exists(dir + fr'\{date}dataframe.csv')==False:
    df = pd.read_json(open(dir + fr'\{date}Output.json','r'))
    #df.set_index('PC Number', inplace=True) takes its own row
    #print(df)
    df.to_csv(dir + fr'\{date}dataframe.csv', index=False, header=True)

csv_data = csv.reader(open(dir + fr'\{date}dataframe.csv'))
next(csv_data)
for row in csv_data:
    cursor.execute('INSERT INTO testcsv ()')

#These are some checks to have (there are a lot to check, but these are the crucial ones):

#this one should show the last row:
#print(dataCell)

#these should match:
#print(len(dataRows)) #what is in the HTML DOM
#print(len(data)) #what the script makes
#end


#proper sibling navigation:
#dataRows[index].select('.CellStyle')[0].next_sibling.next_sibling['dval'] #twice because of whitespace

#should grab count of the table, including 'total' ROWS (the rows labeled as 'total')
#lastID = table.tfoot.find('tr')['id']
