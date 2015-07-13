import glob
import re
#import matplotlib
import os
import BeautifulSoup
import sys

  
class Catalog():
  def __init__(self, books='books.tsv'):
    self.books = dict([l.strip().split('\t') for l in open(books).readlines()]) 
    self.dirs = glob.glob('./webreport_langsci-press.org_catalog_20[0-9][0-9]_[01][0-9]')
    self.monthstats = dict([(d[-7:],Stats('%s/awstats.langsci-press.org.urldetail.html'%d).getBooks()) for d in self.dirs]) 
  
  def plotall(self): 
    for month in self.monthstats: 
      for book in self.monthstats[month]:
	self.plot(book, self.monthstats[month][book]) 
	
  def plotaggregate(self):
    d = {}
    for month in self.monthstats: 
      for book in self.monthstats[month]:
	try:
	  d[book] += self.monthstats[month][book]
	except KeyError:
	  d[book] = self.monthstats[month][book]
    for book in d:
	self.plot(book, d[book])
	
  def plotcumulative(self):
    d = {}
    for month in sorted(self.monthstats):
      print ''
      print month
      print 30*'='
      for book in sorted(self.monthstats[month]):
	try:
	  d[book] += self.monthstats[month][book]
	except KeyError:
	  d[book] = self.monthstats[month][book]
	self.plot(book, d[book])
	
	
  def plot(self,book,hits):
    print hits, hits/20*'|', self.books[str(book)]
      
       
    
class Stats():
  def __init__(self,f):
    self.hits = dict([(tr.findAll('td')[0].text,int(tr.findAll('td')[1].text.replace(',',''))) for tr in BeautifulSoup.BeautifulSoup(open(f)).find('table',attrs={'class':'aws_data'}).findAll('tr')[1:]])
    
  def getBooks(self):
    d = {}
    for k in self.hits:
      if 'view' in k:
	try:
	  i = int(re.search('view/([0-9]+)',k).groups()[0])
	except AttributeError:
	  print "no valid book key in %s" %k
	  continue
	try:
	  d[i] += self.hits[k]
	except KeyError:
	  d[i] = self.hits[k]
    return d
    
if __name__=='__main__':
  c = Catalog()
  c.plotcumulative()
  #f = sys.argv[1]
  #d = Stats(f).getBooks()
  #for k in d:
    #print k, d[k], d[k]/10*'|'
	