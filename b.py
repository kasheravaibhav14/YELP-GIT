
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import pandas as pd
from time import sleep
from random import randint
import os


def fun(review_element,soup):
    ret = []
    for rev in review_element:
        # print(type(rev))
        tmp = dict()
        review = rev.text.split('\n')
        print(review)
        #Author Name
        tmp['AuthorName'] = review[0]
        st = 1

        #Elite User
        if(review[1][:5]=='Elite'):
            tmp['Elite'] = "Elite"
            st = 2
        else:
            tmp['Elite'] = ""

        #Location
        tmp['AuthorLocation'] = review[st]
        st+=1

        #Friends
        tmp['Num Friends'] = "0"
        if len(review[st].split('/')) != 3:
            tmp['Num Friends'] = review[st]
            st+=1

        #Reviews
        tmp['Num Reviews'] = "0"
        if len(review[st].split('/')) != 3:
            tmp['Num Reviews'] = review[st]
            st+=1

        #Photots
        tmp['Num Photos'] = "0"
        if len(review[st].split('/')) != 3:
            tmp['Num Photos'] = review[st]
            st+=1

        for line in range(st,len(review)):
            split_bs = review[line].split('/')
            if len(split_bs) == 3:
                tmp['dateUS'] = review[line]
                date = line
                while line < len(review):
                    splt = review[line].split(' ')
                    if splt[0]=='Useful':
                        for i in range(3):
                            tspl = review[line+i].split(' ')
                            if len(tspl)==1:
                                tmp[tspl[0]] = "0"
                                continue
                            tmp[tspl[0]] = tspl[1]
                        break
                    line = line+1
                break
        rev_text = '\n'.join(review[date + 1:-3])
        tmp['review'] = rev_text

        # author id
        reviewer_name = tmp['AuthorName']
        try:
            reviewer_box = soup.find('div', {"aria-label": reviewer_name}).parent.parent.parent
            authorId =  reviewer_box.find('a', text=reviewer_name)['href']
        except:
            authorId = ''
        tmp['AuthorId'] = authorId

        # rating
        try:
            reviewer_box = soup.find('div', {"aria-label": reviewer_name}).parent.parent.parent.parent
            rating = reviewer_box.find('div', {'role':'img'})['aria-label'][0]
        except:
            rating = ''
        tmp['Rating'] = rating
        ret.append(tmp)
    return ret


def getlinks(driver,link,outp):
    a = json.load(open(outp,"r"))
    dmp=json.load(open('missing'+outp,'r'))
    try:
        soup = BeautifulSoup(driver.page_source, features="html.parser")
        div=soup.find("div",{"class":"pagination__09f24__VRjN4 border-color--default__09f24__NPAKY"})
        print(div)
        span=div.find("span",{"class":"css-chan6m"}).get_text()
        print(span)
        tot=int(span.split(' of ')[-1])
    
    # review_element = driver.find_elements_by_xpath(
    #     "/html/body/yelp-react-root/div[1]/div[4]/div/div/div[2]/div/div[1]/div[2]/section[2]/div[2]/div/div[4]/div[2]/span")
    # tot = int(str(review_element[0].text).split()[-1])
        for i in range(tot):
            a[link + "?start=" + str(10*i)] = "1"
        print('done', link)
        json.dump(a,open(outp,'w'),indent=6)
    except:
        print('No reviews')
        dmp[link]='0'
        json.dump(dmp,open('missing'+outp,'w'))
        pass

def dumpLinks(driver,name,outp):
    a = json.load(open(name,'r'))
    for link in a:
        sleep(randint(2,10))
        driver.get(link)
        getlinks(driver,link,outp)

def dumpreviews(driver,inp,outp):
    a = json.load(open(inp,'r'))
    column = json.load(open(outp,'r'))
    for link in a:
        os.system('cp reviews-5b.json bkp1/reviews-5b.json')
        driver.get(link)
        sleep(randint(1,2))
        soup = BeautifulSoup(driver.page_source, features="html.parser")
        review_element = driver.find_elements_by_xpath("/html/body/yelp-react-root/div[1]/div[4]/div/div/div[2]/div/div[1]/div[2]/section[2]/div[2]/div/ul/li")
        reviews = fun(review_element, soup)
        column[link] = reviews
        json.dump(column,open(outp,'w'), indent=6)
        sleep(randint(1,2))

chromeOptions = Options()
chromeOptions.add_argument('--headless')
driver = webdriver.Chrome(ChromeDriverManager().install(),options=chromeOptions)

# make empty Json files
# urls-x.json
# links-x.json
# eviews-x.json

# first run this
# dumpLinks(driver,"urls-9.json","links-9.json")

# then this
dumpreviews(driver,"links-5b.json","reviews-5b.json")


driver.close()
driver.quit()