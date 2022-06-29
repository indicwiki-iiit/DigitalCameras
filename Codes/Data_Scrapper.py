import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_brands():
    r=requests.get("https://www.digicamdb.com/cameras/")
    soup=BeautifulSoup(r.content,'lxml')
    brands=soup.findAll('div',{'class':'font_tiny'})
    dfs=[]
    print(len(brands),"brands")
    for brand in brands:
        a=brand.find('a').attrs['href']
        b=brand.findAll('b')
        print(a)
        print(b[1].text,"cameras")
        df=get_brand("https://www.digicamdb.com/"+a)
        df['Headquarters']=b[0].text
        dfs.append(df)
    return pd.concat(dfs,ignore_index=True)
    
def get_brand(url):
    pages=get_pages(url)
    if(len(pages)==0):
        return get_cams(url)
    else:
        dfs=[]
        print(len(pages),"pages")
        for page in pages:
            print(page[34:])
            dfs.append(get_cams(page))
        return pd.concat(dfs,ignore_index=True)

def get_pages(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")
    nav=soup.findAll('li',{'class':'pagination_nr'})
    l=[]
    for k in nav:
        a=k.find("a").attrs['href']
        l.append("https://www.digicamdb.com/"+a)
    return l

def get_cams(url):
    cams_page = requests.get(url)
    soup = BeautifulSoup(cams_page.content, "lxml")
    cams=soup.findAll('div',{'class':'newest_div'})
    dfs=[]
    for item in cams:
        x=item.find('div',{'class':'newest_1'})
        a=x.find('a').attrs['href']
        print(a)
        dfs.append(get_cam("https://www.digicamdb.com/"+a))
    return pd.concat(dfs,ignore_index=True)

def get_cam(url):
    cam_page=requests.get(url)
    soup=BeautifulSoup(cam_page.content,'lxml')
    df=pd.DataFrame()
    df['Name']=[soup.find(name='h1').text]
    table=soup.find(name='table',attrs={'class':'w100 table_specs font_smaller'})
    for t in table.findAll(name='span'):
        t.string=t['class'][0]
    li=[[td.text.strip(': \n\t') for td in row.findAll('td')] for row in table.findAll('tr')]
    di={ele[0]:[ele[1]] for ele in li}
    if 'Depth of field' in di:
        del di['Depth of field']
    if 'Megapixels' in di:
        di['Effective megapixels']=di.pop('Megapixels')
        di['Total megapixels']=''
    df=pd.concat([df,pd.DataFrame(di)],axis=1)
    df['Reference']=url
    return df

digicamdb_df=get_brands()
digicamdb_df.to_csv('digicamdb.csv',index=False)