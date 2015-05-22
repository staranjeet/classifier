# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
import random,string
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from categorizer.models import *
from django.core.context_processors import csrf
from django.template import RequestContext
import datetime,os,codecs,re
from django.utils import timezone
from math import log
from math import exp
from lxml import etree
import urllib,operator
import lxml.html
from categorizer.models import *
#from django.conf.settings import PROJECT_ROOT

# Create your views here.

def index(request):
	return render_to_response('index.html')


'''functions for tokenizer'''

def generate_sentence(text):
	'''returns an array of sentence'''
	sentence=text.split(u"।")
	return remove_space(sentence)

def sentence_count(sentences):
	return len(sentences)


def generate_tokens(text):
	if text.find(u"।"):
		sentences=generate_sentence(text)
	else:
		sentences=text
	tokens=[]
	for each_sentence in sentences:
		word_list=each_sentence.split(' ')
		tokens=tokens+word_list
	tokens=hyphenated_tokens(tokens)
	return (remove_space(set(tokens)),sentences,remove_space(tokens))

def remove_space(tokens):
	tokens=filter(lambda tok: tok.strip(),tokens)
	return tokens

def token_count(tokens):
	return len(set(tokens))

def hyphenated_tokens(tokens):
		'''removes tokens containing replicating words'''
		for each in tokens:
			if '-' in each:
				tok=each.split('-')
				tokens.remove(each)
				tokens.append(tok[0])
				#if tok[0]!=tok[1]:
				tokens.append(tok[1])
		return tokens

	#fake comment

def stem_word(word):
	rep_suf={}
	rep_suf[u'ने']=u'ना'
	not_suf={}
	not_suf[u"ांक्षी"]=u"कांक्षी"
	not_suf[u"क्षा"]=u"क्षा"
# 	rep_suf[u'ना']=u''
# 	rep_suf[u'ाती']=u'ात'
# 	rep_suf[u'ायु']=u'ायु'
# 	rep_suf[u'षा']=u'्षा'
# 	#rep_suf[u'पति']=u'पति'
# 	# rep_suf[u'ीयों']=u''
# 	# rep_suf[u'ने']=u'ना'
# 	# rep_suf[u'ने']=u'ना'
# 	# rep_suf[u'ने']=u'ना'
# 	# rep_suf[u'ने']=u'ना'
# 	suffixes = {
#     1: [u"ो",u"े",u"ू",u"ु",u"ि"],
#     2: [u"कर",u"ाओ",u"िए",u"ाई",u"ाए",u"ने",u"नी",u"ना",u"ी",u"ते",u"ीं",u"ती",u"ता",u"ाँ",u"ां",u"ों",u"ें"],
#     3: [u"ाकर",u"ाइए",u'षा',u"ाईं",u"ाया",u"ेगी",u"ा",u"ेगा",u"ोगी",u"ोगे",u"ाने",u"ायु",u"ाना",u"ाते",u"ाती",u"ाता",u"तीं",u"ाओं",u"ाएं",u"ुओं",u"ुएं",u"ुआं"],
#     4: [u"ाएगी",u"ाएगा",u"ाओगी",u"ाओगे",u"एंगी",u"ेंगी",u"एंगे",u"ेंगे",u'ीयों',u"ूंगी",u"ूंगा",u"ातीं",u"नाओं",u"नाएं",u"ताओं",u"ताएं",u"ियाँ",u"ियों",u"ियां"],
#     5: [u"ाएंगी",u"ाएंगे",u"ाऊंगी",u"ाऊंगा",u"ाइयाँ",u"ाइयों",u"ाइयां"],
# }
	suffixes = {
    1: [u"ो",u"े",u"ू",u"ु",u"ी",u"ि",u"ा"],
    2: [u"कर",u"ाओ",u"िए",u"ाई",u"ाए",u"ने",u"नी",u"ना",u"ते",u"ीं",u"ती",u"ता",u"ाँ",u"ां",u"ों",u"ें"],
    3: [u"ाकर",u"ाइए",u"ाईं",u"ाया",u"ेगी",u"ेगा",u"क्षा",u"ोगी",u"ोगे",u"ाने",u"ाना",u"ाते",u"ाती",u"ाता",u"तीं",u"ाओं",u"ाएं",u"ुओं",u"ुएं",u"ुआं"],
    4: [u"ाएगी",u"ाएगा",u"ाओगी",u"ाओगे",u"एंगी",u"ेंगी",u"एंगे",u"ेंगे",u"ूंगी",u"ूंगा",u"ातीं",u"नाओं",u"नाएं",u"ताओं",u"ताएं",u"ियाँ",u"ियों",u"ियां"],
    5: [u"ाएंगी",u"ाएंगे",u"ाऊंगी",u"ाऊंगा",u"ाइयाँ",u"ाइयों",u"ाइयां",u"ांक्षी"],

}
	for L in 5, 4, 3, 2, 1:
		if len(word) > L + 1:
			for suf in suffixes[L]:
				if word.endswith(suf):
					if suf in not_suf:
						return word
					if suf in rep_suf:
					#	print word,suf,L
					#	print word[:-L]
						return word[:-L]+rep_suf[suf]
					return word[:-L]
	return word

def generate_stem(text):
	temp=generate_tokens(text)
	sentences=temp[1]
	tokens=temp[2]
	stem={}
	for each in tokens:
		stem[each]=stem_word(each)
	return (tokens,sentences,stem)

def tokenizer(request):
	c = {}
	c.update(csrf(request))
	sentences,tokens,sent_count,tok_count=None,None,None,None
	if request.POST:
		print 'post request for tokenizer'
		try:
			input_text=request.POST['input_text']
		except:
			pass
		try:
			p_file = request.FILES['file']
			print p_file.name,p_file.content_type
			
			input_text=p_file.read()
			print type(input_text)
			#input_text=unicode(input_text,"utf-8")
			#input_text=input_text.encode('utf-8')
			print type(input_text)
			input_text=input_text.decode('utf-8')
			#print input_text
		except:
			pass
		#print input_text
		input_text=preprocess_string(input_text)
		temp=generate_tokens(input_text)
		sentences=temp[1]
		tokens=temp[0]
		sent_count=sentence_count(sentences)
		tok_count=token_count(tokens)
		#return render_to_response('tokenizer.html',{'sentence':sentences,'tokens':tokens,'scount':sent_count,'tcount':tok_count},context_instance=RequestContext(request))
	return render_to_response('tokenizer.html',{'sentence':sentences,'tokens':tokens,'scount':sent_count,'tcount':tok_count},context_instance=RequestContext(request))

def preprocess_string(strings):
	strings=re.sub(r'(\d+)',r'',strings)
	strings=strings.replace(',','')
	strings=strings.replace('"','')
	strings=strings.replace('(','')
	strings=strings.replace(')','')
	strings=strings.replace('"','')
	strings=strings.replace(':','')
	#strings=strings.replace('-','')
	strings=strings.replace("'",'')
	strings=strings.replace(u"‘‘",'')
	strings=strings.replace(u"’’",'')
	strings=strings.replace("''",'')
	strings=strings.replace(".",'')
	return strings

def stemmer(request):
	c = {}
	c.update(csrf(request))
	sentences,tokens,stem_words=None,None,None
	if request.POST:
		print 'post request for stemmer'
		try:
			input_text=request.POST['input_text']
		except:
			pass
		try:
			p_file = request.FILES['file']
			print p_file.name
			input_text=p_file.read()
			#print type(input_text)
			input_text=input_text.decode('utf-8')
			#print input_text
		except:
			pass
		#input_text=input_text.decode('utf-8')
		input_text=preprocess_string(input_text)
		temp=generate_stem(input_text)
		tokens=temp[0]
		sentences=temp[1]
		stem_words=temp[2]

	return render_to_response('stemmer.html',{'sentence':sentences,'tokens':tokens,'stem_words':stem_words},context_instance=RequestContext(request))

def generate_stopword(text):
	temp=generate_tokens(text)
	sentences=temp[1]
	tokens=temp[0]
	module_dir=os.path.dirname(__file__)
	file_path=os.path.join(module_dir,'swords.txt')
	print module_dir
	f=codecs.open(file_path,encoding='utf-8')
	stopwords=[x.strip() for x in f.readlines()]
	stop_rem_tokens=[i for i in tokens if unicode(i) not in stopwords]
	return (tokens,sentences,stop_rem_tokens)



def stop_word_remover(request):
	c = {}
	c.update(csrf(request))
	stop_rem,stop_rem_len,st_rem_len,stop_words_removed=None,None,None,None
	if request.POST:
		print 'post request for stop words removal'
		try:
			input_text=request.POST['input_text']
		except:
			pass
		try:
			p_file = request.FILES['file']
			print p_file.name
			input_text=p_file.read()
			#print type(input_text)
			input_text=input_text.decode('utf-8')
			#print input_text
		except:
			pass
		input_text=preprocess_string(input_text)
		temp=generate_stopword(input_text)
		stop_rem=temp[2]
		stop_words_removed=set(temp[0])-set(temp[2])
		#print len(stop_words_removed)
		stop_rem_len=len(stop_rem)
		st_rem_len=len(stop_words_removed)

	return render_to_response('stopwords.html',{'stopwords':stop_rem,'words_count':stop_rem_len,'stop_words_rem_count':st_rem_len,'words_remv':stop_words_removed},context_instance=RequestContext(request))

def make_frequency(text):
	temp=generate_tokens(text)
	tokens=temp[0]
	words=temp[2]
	freq={}
	for each in tokens:
		freq[each]=words.count(each)
	return freq

def freq(request):
	c = {}
	c.update(csrf(request))
	freq_dict=None
	if request.POST:
		print 'post request for freq generation'
		try:
			input_text=request.POST['input_text']
		except:
			pass
		try:
			p_file = request.FILES['file']
			print p_file.name
			input_text=p_file.read()
			#print type(input_text)
			input_text=input_text.decode('utf-8')
			#print input_text
		except:
			pass
		input_text=preprocess_string(input_text)
		freq_dict=make_frequency(input_text)
		#=temp
	return render_to_response('freq.html',{'dict':freq_dict},context_instance=RequestContext(request))

def make_dict_file(f):
	b={}
	temp_dict=f.readlines()
	for line in temp_dict:
		h=line.split(',')
		b[h[0]]=int(h[1])
	f.close()
	return b

def size_dict(fr):
	# temp=0
	# for i in fr.keys():
	# 	temp+=fr[i]
	# return temp
	return sum(fr.values())

def find_prob(fr,word,word_count):
	return 1.0*fr[word]/word_count

def classify_news_score(input_news_dict):
	module_dir=os.path.dirname(__file__)
	#file_path=os.path.join(module_dir,category+'.txt')
	fbusiness=codecs.open(os.path.join(module_dir,'business.txt'),encoding='utf-8')
	fsports=codecs.open(os.path.join(module_dir,'sports.txt'),encoding='utf-8')
	fentertainment=codecs.open(os.path.join(module_dir,'entertainment.txt'),encoding='utf-8')
	fnational=codecs.open(os.path.join(module_dir,'national.txt'),encoding='utf-8')
	finternational=codecs.open(os.path.join(module_dir,'international.txt'),encoding='utf-8')
	#make dicts
	business=make_dict_file(fbusiness)
	business_data_count=size_dict(business)
	sports=make_dict_file(fsports)
	sports_data_count=size_dict(sports)
	entertain=make_dict_file(fentertainment)
	entertain_data_count=size_dict(entertain)
	national=make_dict_file(fnational)
	national_data_count=size_dict(national)
	international=make_dict_file(finternational)
	international_data_count=size_dict(international)

	# p_sports_doc=0.0
	# p_business_doc=0.0
	# p_entertain_doc=0.0

	p_sports_sum=0.0
	p_business_sum=0.0
	p_entertain_sum=0.0
	p_national_sum=0.0
	p_international_sum=0.0

	for w in input_news_dict.keys():
		word=w.decode('utf-8')
		word_count=0
		p_word_business,p_word_sports,p_word_entertain,p_word_national,p_word_international=0,0,0,0,0
		if word in sports.keys():
			p_word_sports=find_prob(sports,word,sports_data_count)
			word_count+=sports[word]
		if word in business.keys():
			p_word_business=find_prob(business,word,business_data_count)
			word_count+=business[word]
		if word in entertain.keys():
			p_word_entertain=find_prob(entertain,word,entertain_data_count)
			word_count+=entertain[word]
		if word in national.keys():
			p_word_national=find_prob(national,word,national_data_count)
			word_count+=national[word]
		if word in international.keys():
			p_word_international=find_prob(international,word,international_data_count)
			word_count+=international[word]

		p_word=1.0*word_count/(sports_data_count+business_data_count+entertain_data_count+national_data_count+international_data_count) #right
		if p_word==0:
			p_word=1
	
		if p_word_sports>0:
			p_sports_sum+=log(input_news_dict[w]*p_word_sports/p_word)
		if p_word_business>0:
			p_business_sum+=log(input_news_dict[w]*p_word_business/p_word)
		if p_word_entertain>0:
			p_entertain_sum+=log(input_news_dict[w]*p_word_entertain/p_word)
		if p_word_national>0:
			p_national_sum+=log(input_news_dict[w]*p_word_national/p_word)
		if p_word_international>0:
			p_international_sum+=log(input_news_dict[w]*p_word_international/p_word)
	outcome=['business','entertainment','sports','national','international']
	score_business=exp(p_business_sum+log(1.0/5.0))
	score_sports=exp(p_sports_sum+log(1.0/5.0))
	score_national=exp(p_national_sum+log(1.0/5.0))
	score_international=exp(p_international_sum+log(1.0/5.0))
	score_entertain=exp(p_entertain_sum+log(1.0/5.0))
	scores=[score_business,score_entertain,score_sports,score_national,score_international]
	scores1=[(score_business,'business'),(score_entertain,'entertainment'),(score_sports,'sports'),(score_national,'national'),(score_international,'international')]
	scores1.sort(reverse=True)
	print scores1
	print scores
	max_score=scores1[0][0]
	#message=outcome[scores.index(max_score)]
	message=scores1[0][1]
	msc1=scores1[1][0]
	message1=scores1[1][1]
	msc2=scores1[2][0]
	message2=scores1[2][1]
	#print 'business = ', exp(p_business_sum+log(1.0/3.0)),'sports = ',exp(p_sports_sum+log(1.0/3.0)), 'entertain = ',exp(p_entertain_sum+log(1.0/3.0))
	return [(message,max_score),(message1,msc1),(message2,msc2)]

def check_state(input_text):
	pass
	

def make_data_set(input_text):
	'''this is the main function.
	it will return a dictionary for the input text'''

	input_text=preprocess_string(input_text)
		
	temp=generate_stem(input_text)
	stem_dict=temp[2]
	stem_words=[]
	tokens=temp[0]
	for i in tokens:
		stem_words.append(stem_dict[i])
	module_dir=os.path.dirname(__file__)
	f=codecs.open(os.path.join(module_dir,'swords.txt'),encoding='utf-8')
	stopwords=[x.strip() for x in f.readlines()]
	tokens=[i for i in stem_words if unicode(i) not in stopwords]
	sample_tokens=[]
	for i in tokens:
		sample_tokens.append(i)
	temp_tokens=sample_tokens
	temp=0
	ssfr={}
	tok=set(sample_tokens)
	sample_data_count=0
	for i in tok:
		if i:
			ch=temp_tokens.count(i)
			ssfr[i.encode('utf-8')]=ch
	sample_data_count=size_dict(ssfr)
	return (ssfr,sample_data_count)



def classify(request):
	c = {}
	c.update(csrf(request))
	outcome=''
	hindi={}
	other={}
	x=''
	hindi['business']=u'यह समाचार व्यापार से संबंधित है।'
	hindi['national']=u'यह राष्ट्रीय समाचार है।'
	hindi['international']=u'यह अंतरराष्ट्रीय समाचार है।'
	hindi['sports']=u'यह समाचार खेल से संबंधित है।'
	hindi['entertainment']=u'यह समाचार मनोरंजन क्षेत्र से संबंधित है।'

	other['business']=u'व्यापार'
	other['national']=u'राष्ट्रीय'
	other['international']=u'अंतरराष्ट्रीय'
	other['sports']=u'खेल'
	other['entertainment']=u'मनोरंजन'
	if request.POST: 
		print 'post request on predict page'
		try:
			input_text=request.POST['input_text']
		except:
			pass
		try:
			p_file = request.FILES['file']
			print p_file.name
			input_text=p_file.read()
			#print type(input_text)
			input_text=input_text.decode('utf-8')
			#print input_text
		except:
			pass
		
		temp=make_data_set(input_text)
		ssfr,sample_data_count=temp[0],temp[1]
		print sample_data_count
		h = classify_news_score(ssfr)
		out=h[0][0]

		print hindi[out]
		outcome=hindi[out]
		out1=h[1][0]
		outcome1=other[out1]
		out2=h[2][0]
		outcome2=other[out2]
		print outcome1,outcome2


	return render_to_response('predict.html',{'outcome':outcome ,'prob1':outcome1,'prob2':outcome2},context_instance=RequestContext(request))

def clean_html(input_text):
	text=lxml.html.document_fromstring(input_text)
	return text.text_content()

def generate_news(url):
	'''works for 
	ndtv,hindustan,jansatta
	'''
	empty=None,None,None,None
	try:
		response=urllib.urlopen(url)
		print 'news gen'
	except:
		return empty
		print 'exception raised'
	tree=etree.parse(response)

	t=tree.xpath('//item/title/text()')
	l=tree.xpath('//item/link/text()')
	d=tree.xpath('//item/description/text()')
	# for i in d:
	# 	i=clean_html(i)

	#map(lambda i:clean_html(i),d)
	p=tree.xpath('//item/pubDate/text()')
	return (t,l,d,p)

def return_each_news(description,category):

	max_score=0
	for i in description:
		temp=make_data_set(i)
		ssfr,sample_data_count=temp[0],temp[1]
		h = classify_news_score(ssfr)
		outcome=h[0]
		if outcome==category:
			#return description.index(i)
			if h[1]>max_score:
				max_score=h[1]
				ind=description.index(i)
	if max_score==0:			
		return -1
	else:
		return (ind,max_score)


def suggest(request):
	
	c = {}
	c.update(csrf(request))
	news=[]
	input_text=''
	hindi={}
	hindi['business']=u'व्यापार'
	hindi['national']=u'राष्ट्रीय'
	hindi['international']=u'अंतरराष्ट्रीय'
	hindi['sports']=u'खेल'
	hindi['entertainment']=u'मनोरंजन'
	if request.POST:
		print 'post req on suggest page'
		input_text=request.POST['input_text']

		urls=['http://feeds.feedburner.com/ndtvkhabar','http://www.livehindustan.com/home/rssfeed/1.html']

		for each_url in urls:
			#do processing here
			print 'working for ',each_url
			title,link,description,pubdate=generate_news(each_url)
			if not title:
				return HttpResponse("<h2>Kindly check your internet connection</h2>")

			print 'len of news generated ',len(title)

			temp_ci=return_each_news(description,input_text)
			if temp_ci==-1:
				temp_news=None
			else:
				ci=temp_ci[0]
				temp_news=News(url=link[ci],headline=title[ci],content=clean_html(description[ci]),pub_date=pubdate[ci])
				pair_news=(temp_news,temp_ci[1])
				news.append(pair_news)
		
		news.sort(key=operator.itemgetter(1),reverse=True)
		#news.reverse()
		input_text=hindi[input_text]




	return render_to_response('suggest.html',{'news':news,'your_choice':input_text},context_instance=RequestContext(request))