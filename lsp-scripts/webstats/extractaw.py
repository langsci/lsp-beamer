import glob
import re 
import os
import BeautifulSoup
import sys
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mplcolors

  
class Catalog():
  def __init__(self, books='books.tsv'):
    #read ID and title of books from file
    self.books = dict([l.strip().split('\t') for l in open(books).read().decode('iso-8859-1').split('\n')]) 
    #collect all directories with access information
    self.dirs = glob.glob('webreport_langsci-press.org_catalog_20[0-9][0-9]_[01][0-9]')
    #extract access data from all log files
    self.monthstats = dict([(d[-7:],Stats(os.path.join(d,'awstats.langsci-press.org.urldetail.html')).getBooks()) for d in self.dirs]) 
    self.countrystats = dict([(d[-7:],CountryStats(os.path.join(d,'awstats.langsci-press.org.alldomains.html')).getCountries()) for d in self.dirs]) 
    #print self.countrystats
  
  def plotall(self): 
    for month in self.monthstats: 
      for book in self.monthstats[month]:
	self.plot(book, self.monthstats[month][book]) 
	
  def plotaggregate(self):
    """ compute totals for books and print out """
    
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
    """ compute totals for books per month and print out """
    
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
    """print to standard out"""
    
    print hits, hits/20*'|', self.books[str(book)]
    
  def matplotcumulative(self,ID=False, legend=True, fontsizetotal=15, threshold=99):
    """
    produce cumulative graph
    
    Aggregate cumulative data for time sequence.
    Plot this data with matplotlib.
    """
    
    #sort the keys so we get them in temporal order
    labels = sorted(self.monthstats.keys())   
    
    #setup matplot 
    fig = plt.figure()
    #use a wide picture
    fig.set_figwidth(12)
    ax = plt.subplot(111)
    #fig.add_subplot(ax)
     
    plt.rc('legend',**{'fontsize':9}) 
    #fig.patch.set_visible(False)
    #ax.axis('off')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_ylabel('downloads')
    ax.set_xlabel('months')   
    #setup colors and shapes to select from
    colors = plt.cm.Set1(np.linspace(0, 1, 45)) 
    #colors = 'bgrcmyk'
    shapes = 'v^osp*D'
    
    #store data to plot here so we can sort before plotting
    plots = []
    for book in self.books:
      if ID and book!=str(ID):
	#print 'skipping', repr(ID), repr(book)
	continue
      print book,':',
      tmp = 0 
      #initialize axes
      x = range(len(labels)+1)
      y = [None for i in range(len(labels))]
      #update values for axes
      for i,month in enumerate(labels):	 
	try:
	  y[i] = tmp+self.monthstats[month][int(book)]
	  tmp = y[i]
	except KeyError:#no downloads this month
	  y[i] = tmp  
      for i,j in enumerate(y):
	if i == 0:#avoid IndexError when subtracting
	  continue
	if y[i]!=None and y[i]<threshold:
	  y[i-1]=None
      #if total is lower than threshold, do not display at all
      if y[-1]<threshold:
	y[-1] = None
      #reserve space for labels
      y.append(None)
      print y
      #colors and shapes for lines should be identical for 
      #a book across several graphics, but different for 
      #different books. Use a hash function to assign colors
      #and shapes
      seed = hash(book)
      c = colors[seed%len(colors)]
      s = shapes[seed%len(shapes)]
      #store plot data for future usage
      plots.append([x,y,c,s,self.books[book]]) 
    #sort plot data according to highest total downloads
    #Then plot the plots
    n = 0	
    origlabels = labels
    for plot in sorted(plots, key=lambda k: k[1][-2],reverse=True): 
      #print plot
      if plot[1][-2]<30: #make sure no test or bogus data are displayed
	continue
      #print labels
      if ID!=False:
	n = 0	
	for t in y:
	  if t==None:
	    n += 1
	plot[0] = plot[0][n-1:]
	plot[1] = plot[1][n-1:]
	labels = labels[n:] 
      #plot line
      ax.plot(plot[0],plot[1] ,color=plot[2],linewidth=1.5)
      #ax.plot((1,2,3),(4,5,6) ,color=plot[2],linewidth=1.5)
      #plot marks
      ax.plot(plot[0],plot[1],plot[3],color=plot[2],label=plot[4]) 
      ax.text(len(origlabels)-1, plot[1][-2], '  %s'%plot[1][-2], fontsize=fontsizetotal) 
    #plot x-axis labels
    plt.xticks(x[n:], [l[-5:].replace('_','/') for l in labels], fontsize = 10) 
    #position legend box
    if legend:
      box = ax.get_position()
      ax.set_position([box.x0, box.y0, box.width * 0.66, box.height]) 
      ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False,numpoints=1) 
    #else:
      #ax.legend_.remove()
    #save file
    if ID:
      plt.savefig('%s.svg'%ID)
      plt.savefig('%s.png'%ID)
    else:
      plt.savefig('cumulativeall.svg')
      plt.savefig('cumulativeall.png')
   
  def plotCountries(self,threshold=12):
    d = {}
    for m in self.countrystats:
      md = self.countrystats[m]
      for c in md:
	try:
	  d[c] += int(md[c].replace(',',''))
	except KeyError:
	  d[c] = int(md[c].replace(',',''))
	      
    for k in d:
      print k, d[k]
    l = [(k,d[k]) for k in d]        
    l.sort(key=lambda x: x[1], reverse=True) 
    values = [t[1] for t in l][:threshold]+[sum([t[1] for t in l][threshold:])]  
    labels = ['%s: %s'%t for t in l][:threshold]+['Other:%s'%values[-1]]
    for i in range(threshold+1,len(labels)):
      labels[i]=''
    print labels, values
    cmap = plt.get_cmap('Paired')
    colors = [cmap(i) for i in np.linspace(0, 1, threshold+1)]
    #setup matplot 
    fig = plt.figure()
    plt.axis("equal") 
    fig.set_figwidth(12)
    ax = plt.subplot(111)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.66, box.height]) 
    plt.pie(values, labels=labels, colors=colors, labeldistance=1.4)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False,numpoints=1) 
    plt.savefig('countries.png') 
    plt.savefig('countries.svg') 
	  
      
     
    
class Stats():
  def __init__(self,f):
    """
    navigate the html file to find the relevant <td>s and
    create a dictionary mapping urls to download figures
    """
    
    self.hits = dict(
		      [
			(
			  #locate key
			  tr.findAll('td')[0].text,
			  #remove thousands separator and convert value to int
			  int(tr.findAll('td')[1].text.replace(',',''))
			) for tr in BeautifulSoup.BeautifulSoup(open(f))\
				  .find('table',attrs={'class':'aws_data'})\
				  .findAll('tr')[1:]
		      ]
		  )    


    
  def getBooks(self):
    """
    analyze the access data and aggregate stats for books across publication formats
    """
    
    d = {}
    for k in self.hits:
      if 'view' in k: #ignore /download/, which is used for files other than pdf
	try:
	  #extract ID
	  i = int(re.search('view/([0-9]+)',k).groups()[0])
	except AttributeError:
	  print "no valid book key in %s" %k
	  continue
	try:
	  #accumulate figures for the various publication formats
	  d[i] += self.hits[k]
	except KeyError:
	  d[i] = self.hits[k]
    return d
    
        
  def getCountries(self):
    """
    analyze the access data and aggregate stats for countries
    """
    
    d = {}
    for k in self.hits: 
	try:
	  #accumulate figures for the various publication formats
	  d[k] += self.hits[k]
	except KeyError:
	  d[k] = self.hits[k] 
    return d
   
class CountryStats(Stats):
  def __init__(self,f):
    """
    navigate the html file to find the relevant <td>s and
    create a dictionary mapping urls to download figures
    """		  
    self.hits = dict(
		      [
			(
			  #locate key
			  tr.findAll('td')[2].text,
			  #remove thousands separator and convert value to int
			  tr.findAll('td')[4].text
			) for tr in BeautifulSoup.BeautifulSoup(open(f))\
				  .find('table',attrs={'class':'aws_data'})\
				  .findAll('tr')[1:]
		      ]
		  )  
		  
if __name__=='__main__':
  c = Catalog()
  print "country plot"
  c.plotCountries(threshold=13)
  #print 30*'-'
  #print "global plot"
  #c.matplotcumulative(fontsizetotal=7) 
  #print 30*'-'
  #print "individual plots"
  #for b in c.books: 
    #c.matplotcumulative(ID=b, legend=False)
	