
def sliceString(string,beginStr,endStr='nothing'):
    startIndex = string.find(beginStr)+len(beginStr) #doesnt include beginStr
    if endStr=='nothing':
        return string[startIndex:]
    stopIndex = string.find(endStr,startIndex) #so it doesn't take beginStr into consideration
    output = string[startIndex:stopIndex]
    return output

import requests
import json
import pandas as pd
from bs4 import BeautifulSoup

f = open('Report.xls','rb')
content = f.read()
soup = BeautifulSoup(content,'html.parser')
mainHeaderText = soup.find(id='MainReportDiv').text.strip().split('Report Time')[0]

data = []

#grabs first table since there are two tables and CSS
table = soup.find(class_='TableStyle')

#grabs business unit and then PC#
businessUnit = sliceString(mainHeaderText,'Business Unit','-')
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

with open('testOutput.json','w') as f:
    json.dump(data,f)

df = pd.read_json(open('testOutput.json','r'))
#df.set_index('PC Number', inplace=True) takes its own row
#print(df)
df.to_csv(r'.\export_dataframe.csv', index=False,header=True)

#These are some checks to have (there are a lot to check, but these are the crucial ones):

#this one should show the last row:
#print(dataCell)

#these should match:
#print(len(dataRows))
#print(len(data))
#end
f.close()

#proper sibling navigation:
#dataRows[0].select('.CellStyle')[0].next_sibling.next_sibling['dval']

#should grab count of the table, including total ROWS
#lastID = table.tfoot.find('tr')['id']
