from selenium import webdriver
import selenium.common.exceptions as exexception
import time
import pandas as pd
from bs4 import BeautifulSoup
import random

browser = None

username = input("Enter your Email ID:")
password = input("Enter your Password:")

def log_in():
    global browser
    browser = webdriver.Chrome('chromedriver.exe')
    print("Opening Browser")
    time.sleep(2)
    browser.get('https://www.linkedin.com/sales/login')
    time.sleep(random.randint(2,4))
    browser.maximize_window()
    time.sleep(2)
    elementID = browser.find_element_by_xpath('/html/body/div/main/div[2]/form/div[1]/input').send_keys(username) # send email id
    print("Entered ID")
    time.sleep(random.randint(2,4))
    elementID = browser.find_element_by_xpath('/html/body/div/main/div[2]/form/div[2]/input').send_keys(password) # send pass
    print("Entered Password")
    time.sleep(random.randint(2,4))
    elementID = browser.find_element_by_xpath('/html/body/div/main/div[2]/form/div[3]/button').click() # click sign-in
    print("Clicked on Sign-in")
    time.sleep(random.randint(7,9))

    while True:
        if browser.current_url.find('checkpoint') != -1:
            time.sleep(15)
            print('Checkpoint present:Need to clear....')
        else:
            print('Checkpoint Passed.')
            break

    while True:
        if browser.current_url.find('sales/homepage') == -1:
            time.sleep(15)
            print('Waiting for homepage to load....')
        else:
            print('Homepage loaded.')
            break
    time.sleep(10)

def scrape_links(pages,dic):
    if pages.find_all('ol',{'class':'search-results__pagination-list'})[0].find_all('li')[-1].find_all('button')==[]:
        print("1 page found in search results.")
        time.sleep(4)
        for i in range(15):
            browser.execute_script(f"window.scrollTo(Math.ceil(({i}*(document.body.scrollHeight))/15),Math.ceil(({i+1}*(document.body.scrollHeight))/15));")
            time.sleep(2)
        time.sleep(5)
        url = browser.page_source
        doc = BeautifulSoup(url, 'html.parser')
        base_link='https://www.linkedin.com'
        for i in range(len(doc.find_all("div",{"class":"horizontal-person-entity-lockup-4 result-lockup__entity ml6"}))):
            try:
                dic['Name'].append(doc.find_all("div",{"class":"horizontal-person-entity-lockup-4 result-lockup__entity ml6"})[i].find_all('a',{'class':'ember-view'})[1].text.strip())
            except IndexError:
                dic['Name'].append('Not Given.')
            try:
                dic['link'].append(base_link+doc.find_all("div",{"class":"horizontal-person-entity-lockup-4 result-lockup__entity ml6"})[i].find_all('a',{'class':'ember-view'})[1]['href'])
            except IndexError:
                dic['link'].append('Not Given')
            try:
                dic['Designation'].append(doc.find_all('span',{'class':'t-14 t-bold'})[i].text)
            except IndexError:
                dic['Designation'].append('Not Given')
            try:
                dic['Location'].append(doc.find_all('li',{'class':'result-lockup__misc-item'})[i].text)
            except IndexError:
                dic['Location'].append('Not Given')
            dic['Scrapping_Status'].append('Not Done')
        pd.DataFrame(dic).to_csv('link_leads.csv',index=None)
    else:
        p = int(pages.find_all('ol',{'class':'search-results__pagination-list'})[0].find_all('li')[-1].find_all('button')[0].text.strip())
        print(f"{p} no. of pages found")
        time.sleep(4)
        for pa in range(p):
            print(f"Scrapping through {pa+1} page.")
            for i in range(15):
                browser.execute_script(f"window.scrollTo(Math.ceil(({i}*(document.body.scrollHeight))/15),Math.ceil(({i+1}*(document.body.scrollHeight))/15));")
                time.sleep(1)
            time.sleep(5)
            url = browser.page_source
            doc = BeautifulSoup(url, 'html.parser')
            base_link='https://www.linkedin.com'
            for i in range(len(doc.find_all("div",{"class":"horizontal-person-entity-lockup-4 result-lockup__entity ml6"}))):
                try:
                    dic['Name'].append(doc.find_all("div",{"class":"horizontal-person-entity-lockup-4 result-lockup__entity ml6"})[i].find_all('a',{'class':'ember-view'})[1].text.strip())
                except IndexError:
                    dic['Name'].append('Not Given.')
                try:
                    dic['link'].append(base_link+doc.find_all("div",{"class":"horizontal-person-entity-lockup-4 result-lockup__entity ml6"})[i].find_all('a',{'class':'ember-view'})[1]['href'])
                except IndexError:
                    dic['link'].append('Not Given')
                try:
                    dic['Designation'].append(doc.find_all('span',{'class':'t-14 t-bold'})[i].text)
                except IndexError:
                    dic['Designation'].append('Not Given')
                try:
                    dic['Location'].append(doc.find_all('li',{'class':'result-lockup__misc-item'})[i].text)
                except IndexError:
                    dic['Location'].append('Not Given')
                dic['Scrapping_Status'].append('Not Done')
            if pa == (p-1):
                pass
            else:
                elementID = browser.find_element_by_xpath('/html/body/main/div[1]/div/section/div[2]/nav/button[2]/span').click()
                time.sleep(2)
        pd.DataFrame(dic).to_csv('link.csv',index=None)
    pd.DataFrame(dic).to_csv('link.csv',index=None)

def scrape_profiles(link_df):
    start = 0
    dic = {'Name':None,'link':None,'Designation':None,'Location':None,'Scrapping_Status':None}
    for i in range(len(link_df)):
        if link_df['Scrapping_Status'][i] == 'Not Done':
            break
        else:
            start+=1

    if (len(link_df)-start-1)>950:
        end = start+950
    else:
        end = len(link_df)
    print(f'Start position:{start+1}')
    print(f'Ending position:{end}')
    dic['Name']=link_df['Name'].tolist()
    dic['link']=link_df['link'].tolist()
    dic['Designation']=link_df['Designation'].tolist()
    dic['Location']=link_df['Location'].tolist()
    dic['Scrapping_Status']=link_df['Scrapping_Status'].tolist()

    data = {
        'Name':[],
        'Link':[],
        'Sub Title':[],
        'Location':[],
        'Experience':[]
    }
    if start==0:
        df1 = pd.DataFrame()
    else:
        df1 = pd.read_csv('output_leads.csv')

    break_list = [i for i in range(start,end,100)]
    for i in range(start,end):
        print(f"Scrapping details from {i+1}th profile.")
        browser.execute_script("window.open('');")
        time.sleep(2)
        browser.switch_to.window(browser.window_handles[1])
        time.sleep(2)
        browser.get(dic['link'][i])
        time.sleep(5)
        try:
            elementID = browser.find_element_by_xpath('/html/body/main/div[2]/div[1]/div/div[1]/section[1]/div/button').click()
        except exexception.NoSuchElementException:
            pass
        time.sleep(3)
        mem = browser.page_source
        mem_details = BeautifulSoup(mem, 'html.parser')
        data['Name'].append(dic['Name'][i])
        data['Link'].append(dic['link'][i])
        data['Sub Title'].append(dic['Designation'][i])
        data['Location'].append(dic['Location'][i])
        temp = []
        if mem_details.find_all('ul',{'class':'profile-experience__position-list list-style-none'})!=[]:
            # Details in long format
            for j in range(len(mem_details.find_all('ul',{'class':'profile-experience__position-list list-style-none'})[0].find_all('li',{'class':'profile-position display-flex align-items-flex-start'}))):
                exp = {
                    'Position':None,
                    'Company_name':None,
                    'Time Period':None,
                    'Duration':None,
                    'location':None
                }
                try:
                    exp['Position'] = mem_details.find_all('ul',{'class':'profile-experience__position-list list-style-none'})[0].find_all('li',{'class':'profile-position display-flex align-items-flex-start'})[j].find('dt').text.strip()
                except AttributeError:
                    exp['Position']='NA'
                try:
                    exp['Company_name'] = mem_details.find_all('ul',{'class':'profile-experience__position-list list-style-none'})[0].find_all('li',{'class':'profile-position display-flex align-items-flex-start'})[j].find('a',{'class':'ember-view inverse-link-on-a-light-background font-weight-400'}).text.strip()
                except AttributeError:
                    exp['Company_name'] = 'NA'
                try:
                    tp = mem_details.find_all('ul',{'class':'profile-experience__position-list list-style-none'})[0].find_all('li',{'class':'profile-position display-flex align-items-flex-start'})[j].find('p',{'class':'profile-position__dates-employed fl t-12 t-black--light'}).text.replace('\n','').replace(' ','')[13:]
                    exp['Time Period'] = tp[:7]+'-'+tp[8:]
                except AttributeError:
                    exp['Time Period'] = 'NA'
                try:
                    exp['Duration'] = mem_details.find_all('ul',{'class':'profile-experience__position-list list-style-none'})[0].find_all('li',{'class':'profile-position display-flex align-items-flex-start'})[j].find('p',{'class':'profile-position__duration mb1 t-12 t-black--light t-italic'}).text.replace('\n','').replace(' ','')[18:]
                except AttributeError:
                    exp['Duration'] = 'NA'
                try:
                    exp['location'] = mem_details.find_all('ul',{'class':'profile-experience__position-list list-style-none'})[0].find_all('li',{'class':'profile-position display-flex align-items-flex-start'})[j].find('dd',{'class':'profile-position__company-location mb2 t-12 t-black--light'}).text.replace('\n','').replace(' ','')[8:]
                except AttributeError:
                    exp['location'] = 'NA'
                temp.append(exp)
        else:
            # Short Format
            if mem_details.find_all('dd',{'class':'profile-topcard__current-positions flex mt3'}) !=[]:
                cur = mem_details.find_all('dd',{'class':'profile-topcard__current-positions flex mt3'})[0].find_all('div',{'class':'profile-topcard__summary-position flex align-items-top'})
                for k in range(len(cur)):
                    exp = {
                        'Position':None,
                        'Company_name':None,
                        'Time Period':None,
                        'Duration':None,
                        'location':None
                    }
                    try:
                        exp['Position'] = cur[k].find('span',{'class':'profile-topcard__summary-position-title'}).text
                    except AttributeError:
                        exp['Position'] = 'NA'
                    try:
                        exp['Company_name'] = cur[k].find('span',{'class':'t-14 t-black t-bold'}).text
                    except ArithmeticError:
                        exp['Company_name'] ='NA'
                    try:
                        exp['Duration'] = cur[k].find('span',{'class':'profile-topcard__time-period-bullet'}).text.strip()
                    except AttributeError:
                        exp['Duration'] = 'NA'
                    exp['Time Period'] = 'NA'
                    exp['location'] = 'NA'
                    temp.append(exp)
            else:
                exp = {
                        'Position':None,
                        'Company_name':None,
                        'Time Period':None,
                        'Duration':None,
                        'location':None
                    }
                exp['Position'] = 'NA'
                exp['Company_name'] = 'NA'
                exp['Duration'] = 'NA'
                exp['Time Period'] = 'NA'
                exp['location'] = 'NA'
                temp.append(exp)
            if mem_details.find_all('dd',{'class':'profile-topcard__previous-positions flex mt3'})!=[]:
                prev = mem_details.find_all('dd',{'class':'profile-topcard__previous-positions flex mt3'})[0].find_all('div',{'class':'profile-topcard__summary-position flex align-items-top'})
                for l in range(len(prev)):
                    exp = {
                        'Position':None,
                        'Company_name':None,
                        'Time Period':None,
                        'Duration':None,
                        'location':None
                    }
                    try:
                        exp['Position'] = prev[l].find('span',{'class':'profile-topcard__summary-position-title'}).text
                    except AttributeError:
                        exp['Position'] = 'NA'
                    try:
                        exp['Company_name'] = prev[l].find('span',{'class':'t-14 t-black t-bold'}).text
                    except AttributeError:
                        exp['Company_name'] = 'NA'
                    try:
                        exp['Duration'] = prev[l].find('span',{'class':'profile-topcard__time-period-bullet'}).text.strip()
                    except AttributeError:
                        exp['Duration'] = 'NA'
                    exp['Time Period'] = 'NA'
                    exp['location'] = 'NA'
                    temp.append(exp)
            else:
                exp = {
                        'Position':None,
                        'Company_name':None,
                        'Time Period':None,
                        'Duration':None,
                        'location':None
                    }
                exp['Position'] = 'NA'
                exp['Company_name'] = 'NA'
                exp['Duration'] = 'NA'
                exp['Time Period'] = 'NA'
                exp['location'] = 'NA'
                temp.append(exp)
        if (i+1) in break_list:
            print(f'Break after {i+1} profiles.')
            time.sleep(random.choice([br for br in range(240,481,60)]))
        data['Experience'].append(temp)
        dic['Scrapping_Status'][i] = 'Done'
        pd.DataFrame(dic).to_csv('link_leads.csv',index=None)
        time.sleep(1)
        browser.close()
        time.sleep(2)
        browser.switch_to.window(browser.window_handles[0])
        print(f"{i+1}th profile scrapped.")

        # Store Data in Particular format
        print(f"Storing data of {i+1} profile(s).")
        data_exp_lens = []
        for i in range(len(data['Experience'])):
            data_exp_lens.append(len(data['Experience'][i]))
        #max(data_exp_lens)

        df_data = {
            'Name':[],
            'Link':[],
            'Sub Title':[],
            'Location':[],
            'Current_Position':[],
            'Current_Company':[],
            'Current_Duration':[],
            'Current_Time_Period':[],
            'Current_Location':[]
        }

        for i in range(max(data_exp_lens)-1):
            df_data[f'Previous_Position_{i+1}'] = []
            df_data[f'Previous_Company_{i+1}'] = []
            df_data[f'Previous_Duration_{i+1}'] = []
            df_data[f'Previous_Time_Period_{i+1}'] = []
            df_data[f'Previous_Location_{i+1}'] = []

        for i in range(len(data['Name'])):
            if data['Experience'][i]!=[]:
                df_data['Name'].append(data['Name'][i])
                df_data['Link'].append(data['Link'][i])
                df_data['Sub Title'].append(data['Sub Title'][i])
                df_data['Location'].append(data['Location'][i])
                
                df_data['Current_Position'].append(data['Experience'][i][0]['Position'])
                df_data['Current_Company'].append(data['Experience'][i][0]['Company_name'])
                df_data['Current_Duration'].append(data['Experience'][i][0]['Duration'])
                df_data['Current_Time_Period'].append(data['Experience'][i][0]['Time Period'])
                df_data['Current_Location'].append(data['Experience'][i][0]['location'])
                if len(data['Experience'][i])>1:
                    if len(data['Experience'][i])==max(data_exp_lens):
                        for j in range(1,len(data['Experience'][i])):
                            df_data[f'Previous_Position_{j}'].append(data['Experience'][i][j]['Position'])
                            df_data[f'Previous_Company_{j}'].append(data['Experience'][i][j]['Company_name'])
                            df_data[f'Previous_Duration_{j}'].append(data['Experience'][i][j]['Duration'])
                            df_data[f'Previous_Time_Period_{j}'].append(data['Experience'][i][j]['Time Period'])
                            df_data[f'Previous_Location_{j}'].append(data['Experience'][i][j]['location'])
                    else:
                        for j in range(1,len(data['Experience'][i])):
                            df_data[f'Previous_Position_{j}'].append(data['Experience'][i][j]['Position'])
                            df_data[f'Previous_Company_{j}'].append(data['Experience'][i][j]['Company_name'])
                            df_data[f'Previous_Duration_{j}'].append(data['Experience'][i][j]['Duration'])
                            df_data[f'Previous_Time_Period_{j}'].append(data['Experience'][i][j]['Time Period'])
                            df_data[f'Previous_Location_{j}'].append(data['Experience'][i][j]['location'])
                        for j1 in range(j+1,max(data_exp_lens)):
                            df_data[f'Previous_Position_{j1}'].append('NA')
                            df_data[f'Previous_Company_{j1}'].append('NA')
                            df_data[f'Previous_Duration_{j1}'].append('NA')
                            df_data[f'Previous_Time_Period_{j1}'].append('NA')
                            df_data[f'Previous_Location_{j1}'].append('NA')
                else:
                    for j in range(1,max(data_exp_lens)):
                        df_data[f'Previous_Position_{j}'].append('NA')
                        df_data[f'Previous_Company_{j}'].append('NA')
                        df_data[f'Previous_Duration_{j}'].append('NA')
                        df_data[f'Previous_Time_Period_{j}'].append('NA')
                        df_data[f'Previous_Location_{j}'].append('NA')
            else:
                df_data['Name'].append(data['Name'][i])
                df_data['Link'].append(data['Link'][i])
                df_data['Sub Title'].append(data['Sub Title'][i])
                df_data['Location'].append(data['Location'][i])
                df_data['Current_Position'].append('Not Given')
                df_data['Current_Company'].append('Not Given')
                df_data['Current_Duration'].append('Not Given')
                df_data['Current_Time_Period'].append('Not Given')
                df_data['Current_Location'].append('Not Given')
                for j in range(1,max(data_exp_lens)):
                    df_data[f'Previous_Position_{j}'].append('Not Given')
                    df_data[f'Previous_Company_{j}'].append('Not Given')
                    df_data[f'Previous_Duration_{j}'].append('Not Given')
                    df_data[f'Previous_Time_Period_{j}'].append('Not Given')
                    df_data[f'Previous_Location_{j}'].append('Not Given')

        df2 = pd.DataFrame(df_data)
        final_df = pd.concat([df1,df2])
        final_df.fillna('NA',inplace=True)
        final_df.to_csv('leads.csv',index=None)
        print("Data saved as output_leads.csv")
        
def leads_scrapper():
    log_in()
    global browser
    elementID = browser.find_element_by_xpath('/html/body/header/div/div[2]/section/div/div[1]/div/div/div[2]/a').click() # select filter tab
    print('Filter pop-up opened.')
    time.sleep(random.randint(4,7))

    u = browser.current_url
    c=0
    time.sleep(2)
    while c==0:
        if browser.current_url==u:
            print(c)
            print("Waiting for user to click on search...")
            time.sleep(15)
        else:
            c+=1
            print(c)

    dic = {'Name':[],'link':[],'Designation':[],'Location':[],'Scrapping_Status':[]}
    s = browser.page_source
    pages = BeautifulSoup(s,'html.parser')
    check = 0
    if pages.find_all('ol',{'class':'search-results__pagination-list'})!=[]: # search result found
        print('Search results present.')
        # Scrape Profile Links
        scrape_links(pages,dic)
        print('Links Scrapped')
        time.sleep(2)
        #pd.DataFrame(dic).to_csv('link_leads.csv',index=None)
        print('Links scraped as "link.csv".')
        time.sleep(2)
    else:
        print('No search results found.\nScrapping stopped.')
    # Scape Data from Profile
    link_df = pd.read_csv('link.csv')
    if link_df['Scrapping_Status'][0] == 'Not Done':

        print('Starting individual profile scraping.')
        print('Strating profile scraping....')
        scrape_profiles(link_df)
        print("Scrapping complete!!")
    else:
        print("File 'output_leads.csv' is not present.\n Please place the mentioned file in current folder and try again.")
    browser.close()
    
    
    
    
    
