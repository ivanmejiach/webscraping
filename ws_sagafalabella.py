
# coding: utf-8

# In[1]:


from requests import get
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import numpy as np


# In[2]:


def f_diccionario(my_url):       
    response = get(my_url)
    html_soup = BeautifulSoup(response.text, 'lxml')
    containers = html_soup.find_all('main')
    first = containers[0]
    ter =first.findAll('script',{'type':'text/javascript'})
    data = re.findall("var fbra_browseProductListConfig =(.+?);", str(ter[0]), re.S)
    return data


# In[3]:


#FUNCION return DATAFRAME URL
def f_url_detalle():
    url = 'https://www.falabella.com.pe/falabella-pe'
    response = get(url)
    page_soup = BeautifulSoup(response.text, 'lxml')
    pag_principal = page_soup.findAll("li",{"class":"fb-masthead__primary-links__item"})
    
    i=0
    rows =[]
    columns = ['ID','Url','Category']
    
    for p in pag_principal:
        #se excluye a categorias: moda hombre, moda mujeres, belleza, zapato, belleza, accesorios
        if (i>=3 and i<=7): #or i== 12 :
            pagina = p.findAll("a",{"class":"fb-masthead__child-links__item__link js-masthead__child-links__item__link"})
            
            for x in pagina:
                href = "https://www.falabella.com.pe"+ (x.get("href"))            
                separador = href.split("?")[0]
                categoria = separador.split("/")[-1].upper()

                #validar paginacion de ur        
                response = get(href)
                html_soup = BeautifulSoup(response.text, 'lxml')
                containers = html_soup.find_all('main')
                first = containers[0]
                ter =first.findAll('script',{'type':'text/javascript'})
                if len(ter)>0 :
                    row = [i,href,categoria]
                    rows.append(row)
                else:
                    ter=first.findAll('div',{'class':'fb-hero-subnav--nav__block'})
                    for t in ter:
                        href_f = "https://www.falabella.com.pe"+ (t.a.get("href"))
                        row = [i,href_f,categoria]
                        rows.append(row)
            
            #print (str(i)+"|"+href )
        i += 1
    df_url = pd.DataFrame(rows, columns=columns)
    return df_url


# In[4]:


# funcion return nro paginas
def f_paginas (my_url):        
    #ter  = f_diccionario(my_url)
    data = f_diccionario(my_url)
    
    ls_ini = []
    ls_fin = []
    ls_ult =[]

    ult_pag=0
    if data:
        ls_ini = json.loads(data[0])
        if ls_ini:
            ls_fin =ls_ini['state']
            if ls_fin:    
                ls_ult =ls_fin['searchItemList']
                if ls_ult:    
                    ult_pag=ls_ult['pagesTotal'] 
                
    return ult_pag


# In[5]:


def get_datos(v_url):
    from requests import get
    from bs4 import BeautifulSoup
    href = v_url           
    response = get(href)
    html_soup = BeautifulSoup(response.text, 'lxml')
    containers = html_soup.find_all('table',{'class','fb-product-information__specification__table'})
    
    modelo=''
    
    if len(containers)>0:
        tr = containers[0].find_all('tr',{'class','fb-product-information__specification__table__row-data'})
        if len(tr)>0:
            for t in tr:
                tag= t.th.text.strip()
                if tag.upper()=='MODELO':
                    modelo =t.td.text
                    break
    return modelo


# In[6]:


#funcion ejecuta extraccion, usando funciones anteriores
def f_extraccion (ult_pag,url_grupo,category):
    min_pag = 1 
    while min_pag <= ult_pag:
        url = url_grupo +'?page='+str(min_pag)+''

        my_url = url        
        #ter  = f_diccionario(my_url)
        data = f_diccionario(my_url)
    
        separador = my_url.split("?")[0]
        sub_categoria = separador.split("/")[-1].upper() 

        ls_ini = []
        ls_fin = []
        ls_ult =[]
        
        if data:
            ls_ini = json.loads(data[0])  
            if ls_ini:
                ls_fin =ls_ini['state']
                if ls_fin:    
                    ls_ult =ls_fin['searchItemList']
                    if ls_ult:    
                        ls_grid =ls_ult['resultList']
                        if ls_grid:         
                            i=0
                            rows=[]
                            for x in ls_grid :
                                skuId= x["skuId"]
                                ls_grid[i].update({'Category':category})
                                ls_grid[i].update({'Sub_category':sub_categoria})
                                ls_grid[i].update({'group_url':my_url})
                                
                                url_prod= "https://www.falabella.com.pe" +x["url"]
                                modelo = get_datos(url_prod)
                                ls_grid[i].update({'model':modelo})
                                
                                for q in ls_grid[i]["prices"]:
                                    q.update({'skuId':skuId})
                                    #q.update({'category':categoria})
                                    #q.update({'my_url':my_url})
                                    rows.append(q) 

                                i +=1

                            df_cab = pd.DataFrame(ls_grid, columns=['availableSkusTotal', 'backendCategory', 'brand',
                                                                    'isHDAvailable','productId','published','rating',
                                                                    'skuId','title','totalReviews','url','Category','Sub_category','group_url','model'])

                            df_det = pd.DataFrame(rows,columns=['label','opportunidadUnica','originalPrice','symbol','type','skuId'])

                            df_union = pd.merge(df_cab,df_det , on='skuId')

                            if min_pag ==1 :
                                    df_result = df_cab
                            df_result = df_result.append(df_union)

        print(url)
        min_pag +=1
        
    return df_result


# In[116]:


paginas= f_url_detalle()
i=0
j=0
for index,x in paginas.iterrows():
    if len(x)>0 :        
        my_url  = x["Url"]
        category= x["Category"]
        print (my_url)
        
        try:
            ult_pag  = f_paginas(my_url)

            if ult_pag>0:
                df_result= f_extraccion(ult_pag,my_url,category)

                if j==0 :
                    df_result_f=df_result
                df_result_f = df_result_f.append(df_result) 
                j += 1
        except Exception as e:
            print ("ERROR==> "+str(e)+"==>"+my_url)
    i += 1


# In[117]:


import datetime
i = datetime.datetime.now()
fecha= i.strftime('%Y%m%d')
filename = "saga_falabella_"+ fecha +".csv"
df_result_f.to_csv(filename, sep='|', encoding='utf-8',index=False)


# # ================ FIN =================

# In[79]:


#paginas.loc[paginas['Category'].isin(['TV-TELEVISORES','COMPUTADORAS','LINEA BLANCA','ELECTRODOMÉSTICOS',''])]
#paginas= f_url_detalle(pag_principal)
#pag_principal

url = 'https://www.falabella.com.pe/falabella-pe'
response = get(url)
page_soup = BeautifulSoup(response.text, 'lxml')
pag_principal = page_soup.findAll("li",{"class":"fb-masthead__primary-links__item"})

i=0
rows=[]
columns = ['ID','Url','Category']
for p in pag_principal:
    if (i>=3 and i<=7) or i== 12 :
        
        pagina = p.findAll("a",{"class":"fb-masthead__child-links__item__link js-masthead__child-links__item__link"})
        for x in pagina:
            href = "https://www.falabella.com.pe"+ x.get("href")
            separador = href.split("?")[0]
            categoria = separador.split("/")[-1].upper()

            #validar paginacion de ur        
            response = get(href)
            html_soup = BeautifulSoup(response.text, 'lxml')
            containers = html_soup.find_all('main')
            first = containers[0]
            ter =first.findAll('script',{'type':'text/javascript'})
            if len(ter)>0 :
                row = [i,href,categoria]
                rows.append(row)
            else:
                ter=first.findAll('div',{'class':'fb-hero-subnav--nav__block'})
                for t in ter:
                    href_f = "https://www.falabella.com.pe"+ (t.a.get("href"))
                    row = [i,href_f,categoria]
                    rows.append(row)

            #print (str(i)+"|"+href )           
        
            print (str(i)+"-->"+p.h3.text+"-->"+href)
        #rows.append([pagina])             
    #print(p.h3)
    i +=1
df_url = pd.DataFrame(rows, columns=columns)    


# In[ ]:


i=0
rows =[]
columns = ['ID','Url','Category']
for x in pag_principal:
    href = "https://www.falabella.com.pe"+ (a_url[i].get("href"))            
    separador = href.split("?")[0]
    categoria = separador.split("/")[-1].upper()

    #validar paginacion de ur        
    response = get(href)
    html_soup = BeautifulSoup(response.text, 'lxml')
    containers = html_soup.find_all('main')
    first = containers[0]
    ter =first.findAll('script',{'type':'text/javascript'})
    if len(ter)>0 :
        row = [i,href,categoria]
        rows.append(row)
    else:
        ter=first.findAll('div',{'class':'fb-hero-subnav--nav__block'})
        for t in ter:
            href_f = "https://www.falabella.com.pe"+ (t.a.get("href"))
            row = [i,href_f,categoria]
            rows.append(row)

    #print (str(i)+"|"+href )
    i+=1
df_url = pd.DataFrame(rows, columns=columns)


# In[88]:


from requests import get
from bs4 import BeautifulSoup
href = "https://www.falabella.com.pe/falabella-pe/product/13593082/Control-Remoto-Universal-RM-786#longDescription"           
response = get(href)
html_soup = BeautifulSoup(response.text, 'lxml')
#containers = html_soup.find_all('article',{'class','fb-accordion-tabs js-accordion-tabs'})
containers = html_soup.find_all('table',{'class','fb-product-information__specification__table'})
tr = containers[0].find_all('tr',{'class','fb-product-information__specification__table__row-data'})
#td = containers[0].find_all('td')
#td[0].text
for t in tr:
    tag= t.th.text.strip()
    if tag.upper()=='MODELO':
        print (t.td.text)
        #print (t.th.text.strip())

#lista =containers[0].find_all('div',{'class','fb-product-information-tab__copy'})
#li = lista[0].find_all('li')
#li[1].text


# In[103]:


#paginas.select('Category').distinct().show()
#paginas.toPandas()['Category'].unique()
paginas['Category'].unique()


# In[10]:


df= f_extraccion(3,'https://www.falabella.com.pe//falabella-pe/product/16312626/Parlante-MUO-Bluetooth-Oro','AUDIO')
df


# In[11]:




