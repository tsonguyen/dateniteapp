from flask import render_template, request
from flaskexample import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
from a_Model import ModelIt
from geopy.geocoders import Nominatim
geolocator = Nominatim()
from yelpapi import YelpAPI
key='secret'
secret='secret'
token='secret'
token_secret='secret'
yelp_api = YelpAPI(key, secret, token, token_secret)
YOUR_KEY='secret'
YOUR_SECRET='secret'
from BeautifulSoup import BeautifulSoup
Soup=BeautifulSoup
import BeautifulSoup
from urllib import urlopen
import re
import time
from string import join
import random

user = 'tson' #add your username here (same as previous postgreSQL)            
host = 'localhost'
dbname = 'yelp_db'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.route('/DatePlannr')
def index():
    return render_template("dateplannr.html",
       title = 'Home', user = { 'nickname': 'Miguel' },
       )

@app.route('/')
def cesareans_input():
    return render_template("input.html")

@app.route('/output')
def cesareans_output():
		#pull 'address' from input field and store it
		addy = request.args.get('address')
		city = request.args.get('city')
		state = request.args.get('state')
		zipp = request.args.get('zip')
		occay = request.args.get('occasion')
		print occay
		numq=6
		sb = request.args.get('sort_by')
		location = geolocator.geocode(addy+city+state+zipp)
		if location is None:
			location = geolocator.geocode(addy+city+state)
			if location is None:
				location = geolocator.geocode(addy+city)
				if location is None:
					location = geolocator.geocode(addy)
		lat=location.latitude
		lng= location.longitude
		#find closest address
		if occay.lower() =="anniversary":
			sel= 'anniversary'
		elif occay.lower() =="birthday":
			sel= 'birthday'
		elif occay.lower() =="celebration":
			sel= 'celebration'
		elif occay.lower() =="date night":
			sel='date_night'
		query = "SELECT * FROM final_table2 WHERE %s > 0 AND stars_y > stars_z ORDER BY ranking DESC" % sel		
		tdf=pd.read_sql_query(query,con)
		del tdf['level_0']
		ttdf=tdf[tdf.anniversary>0]
		if occay.lower() =="anniversary":
			ttdf=tdf[tdf.anniversary>0]
		elif occay.lower() =="birthday":
			ttdf=tdf[tdf.birthday>0]
		elif occay.lower() =="celebration":
			ttdf=tdf[tdf.celebration>0]
		elif occay.lower() =="date night":
			ttdf=tdf[tdf.date_night>0]
		ttdf.reset_index(level=0, inplace=True)
		ds=find_dist(lat,lng,ttdf['latitude'],ttdf['longitude'])
		ttdf['ds']=ds
		ds.sort_values(inplace=True)
		plc=ds[:200]
		plc=plc.index[:]
		plc=plc.values.tolist()
		if sb =="Distance":
			query_results=ttdf.iloc[plc].sort_index(by='ds', ascending=1)
		elif sb =="Ratings (dates)":
			query_results=ttdf.iloc[plc].sort_index(by='stars_y', ascending=0)
		elif sb=="Ratings (others)":
			query_results=ttdf.iloc[plc].sort_index(by='stars_z', ascending=0)
		elif sb =="# Reviews (others)":
			query_results=ttdf.iloc[plc].sort_index(by='review_count', ascending=0)
		elif sb =="# Reviews (dates)":
			query_results=ttdf.iloc[plc].sort_index(by='num', ascending=0)
		query_results=query_results[:15]
		query_results.sort_values('ranking',ascending=False, inplace=True)
		restrts = []
		for i in range(0,int(numq)):
				query = """
				SELECT s.text, s.pos_rev, l.bay_avg
				FROM ndates_rev_table as l
				JOIN rev_rank_table as s on l.review_id = s.review_id
				WHERE s.business_id = '%s' AND s.%s>0
				ORDER BY bay_avg DESC, l.pos_rev DESC, pol ASC;
				""" % (query_results.iloc[i]['business_id'],sel)
				cdf = pd.read_sql_query(query,con)
				query = """
				SELECT * 
				FROM lv_tot_table
				WHERE business_id = '%s'
				""" % query_results.iloc[i]['business_id']
				mdf = pd.read_sql_query(query,con)
				cdf = cdf.sort_values(by='pos_rev', ascending=False)
				#generate_words(cdf,i)
				status=find_dets(query_results.iloc[i])
				print query_results.iloc[i]['name']
				#data = places.search(query_results.iloc[i]['name']).geo(circle(query_results.iloc[i]['latitude'], query_results.iloc[i]['longitude'], 5)).data()
				cnt=len(cdf)
				cntt=cnt
				if cnt >3:
					cntt=3
				for ii in range(cntt):
					#ff=re.findall(r"([^.]*?"+occay+"[^.]*\.)",cdf.text[ii])
					#if ff==[]:
					#	ff=re.findall(r"([^.]*?"+occay+"[^.]*\!)",cdf.text[ii])
					#if ff==[]:
					#	ff=re.findall(r"([^.]*?"+occay.title()+"[^.]*\!)",cdf.text[ii])
					#if ff==[]:
					#	ff=re.findall(r"([^.]*?"+occay.title()+"[^.]*\!)",cdf.text[ii])
					#if ff!=[]:					
					#	zz=cdf.text[ii].decode('utf-8').replace(str(ff)[2:-2], '<b>'+str(ff)[2:-2]+'</b>')
					zz=cdf.text[ii].decode('utf-8').replace(occay, '<b>'+occay.upper()+'</b>').replace(occay.upper(), '<b>'+occay.upper()+'</b>').replace(occay.title(), '<b>'+occay.upper()+'</b>')
					#zz=re.findall(r"([^.]*?"+occay.upper()+"[^.]*\.)",zz)
					if len(zz)>400:
						z0=zz.find(occay.upper())
						if z0>200:
							z00=z0-200
						else:
							z00=0
						if (len(zz)-z0)>200:
							z01=z0+200
						else:
							z01=len(zz)
						zz=zz[z00:z01]
					cdf.text[ii]='...'+zz+'...'
				if len(cdf)>2:
					restrts.append(dict(rn=(i+1),latt=mdf.latitude[0],lngg=mdf.longitude[0],iurl=status[5].decode('utf-8'),image=status[4],cnt=cnt,rev1=cdf.iloc[0]['text'],rev2=cdf.iloc[1]['text'],rev3=cdf.iloc[2]['text'],site=status[2].decode('utf-8'), price=str(status[0]),stat=str(status[1])[2:-2],distance="{0:.2f}".format(query_results.iloc[i]['ds']),name=query_results.iloc[i]['name'].decode('utf-8'), address=status[3].encode('utf-8'), stars1="{0:.0f}".format(query_results.iloc[i]['ranking']*100), stars2="{0:.2f}".format(query_results.iloc[i]['stars_z']), reviews1=query_results.iloc[i]['num'], reviews2=query_results.iloc[i]['review_count']))
				elif len(cdf)==2:
					restrts.append(dict(rn=(i+1),latt=mdf.latitude[0],lngg=mdf.longitude[0],iurl=status[5].decode('utf-8'),image=status[4],cnt=cnt,rev1=cdf.iloc[0]['text'],rev2=cdf.iloc[1]['text'],rev3='',site=status[2].decode('utf-8'), price=str(status[0]),stat=str(status[1])[2:-2],distance="{0:.2f}".format(query_results.iloc[i]['ds']),name=query_results.iloc[i]['name'].decode('utf-8'), address=status[3].encode('utf-8'), stars1="{0:.0f}".format(query_results.iloc[i]['ranking']*100), stars2="{0:.2f}".format(query_results.iloc[i]['stars_z']), reviews1=query_results.iloc[i]['num'], reviews2=query_results.iloc[i]['review_count']))
				elif len(cdf)==1:
					restrts.append(dict(rn=(i+1),latt=mdf.latitude[0],lngg=mdf.longitude[0],iurl=status[5].decode('utf-8'),image=status[4],cnt=cnt,rev1=cdf.iloc[0]['text'],rev2='',rev3='',site=status[2].decode('utf-8'), price=str(status[0]),stat=str(status[1])[2:-2],distance="{0:.2f}".format(query_results.iloc[i]['ds']),name=query_results.iloc[i]['name'].decode('utf-8'), address=status[3].encode('utf-8'), stars1="{0:.0f}".format(query_results.iloc[i]['ranking']*100), stars2="{0:.2f}".format(query_results.iloc[i]['stars_z']), reviews1=query_results.iloc[i]['num'], reviews2=query_results.iloc[i]['review_count']))
				elif len(cdf)==0:
					restrts.append(dict(rn=(i+1),latt=mdf.latitude[0],lngg=mdf.longitude[0],iurl=status[5].decode('utf-8'),image=status[4],cnt=cnt,rev1='No relevant reviews availaible... :(',rev2='',rev3='',site=status[2].decode('utf-8'), price=str(status[0]),stat=str(status[1])[2:-2],distance="{0:.2f}".format(query_results.iloc[i]['ds']),name=query_results.iloc[i]['name'].decode('utf-8'), address=status[3].encode('utf-8'), stars1="{0:.0f}".format(query_results.iloc[i]['ranking']*100), stars2="{0:.2f}".format(query_results.iloc[i]['stars_z']), reviews1=query_results.iloc[i]['num'], reviews2=query_results.iloc[i]['review_count']))
		return render_template("output.html", city=city,state=state,zipp=zipp,lat=lat,lng=lng,addy = addy, numq = numq, occay = '<b>'+occay.lower()+'</b>', sb = sb.lower(),restrts = restrts,)

def find_dist(lat1,lng1,lat2,lng2):
    return ((lat1-lat2)**2+(lng1-lng2)**2)**.5*97.76
def color_func1(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(0, %d%%, %d%%)" % (random.randint(60, 100),random.randint(10, 50))
def corr_matrix_of_important_words(term_doc_mat, word_list, scores, n_features_to_keep):
    selector = SelectKBest(k=n_features_to_keep).fit(term_doc_mat, scores)
    informative_words_index = selector.get_support(indices=True)
    labels = [word_list[i] for i in informative_words_index]
    data = pd.DataFrame(term_doc_mat[:,informative_words_index].todense(), columns=labels)
    data['Score'] = scores
    return(data.corr())
def generate_words(df,pic):
		vectorizer = CountVectorizer(max_features = 300, stop_words='english')
		term_doc_mat=vectorizer.fit_transform(df.text)
		word_list = vectorizer.get_feature_names()
		corrs_large = corr_matrix_of_important_words(term_doc_mat, word_list, df.pos_rev, 'all')
		pp=corrs_large.Score.sort_values(inplace=False)[:-1]
		pp=pp[pp>0]
		pp=pp[-20:].index
		wc = WordCloud(background_color="white", max_words=20, stopwords=STOPWORDS.add("b"))
		wc.generate(join(df.text))
		wc=wc.recolor(color_func=color_func1)
		wc.to_file('./flaskexample/static/img/p'+str(pic)+'.png')
		#plt.imshow(wc)
		#plt.axis("off")
		#plt.figure()

def find_dets(results):
		site='http://www.yelp.com/biz/'+results.bus_name.decode('utf8')
		site1='http://www.yelp.com/biz_photos/'+results.bus_name.decode('utf8')
		#page = urlopen(site.encode('utf-8'))
		#soup = Soup(page)
		status=[]
		#status.append(re.findall(r'([\w\.-]+)\n',str(soup.findAll('dd', attrs={'class':'nowrap price-description'}))))
		print results['price']		
		if results['price']=='{10}':
			status.append('$')
		elif results['price']=='{11-30}':
			status.append('$$')
		elif results['price']=='{31-60}':
			status.append('$$$')		
		elif results['price']=='{61}':
			status.append('$$$$')	
		else:
			status.append('N/A')
		#closed=re.findall(r'">(.*?)</span>',str(soup.findAll('span', attrs={'class':'nowrap extra closed'})))	
		#if len(closed)<1:
		#	closed="['Open now']"
		#status.append(closed)
		status.append("['Open now']")
		status.append(site.encode('utf-8'))
		status.append(results['addy'])
		status.append(results['iurl'])
		status.append(site1.encode('utf-8'))
		return status


