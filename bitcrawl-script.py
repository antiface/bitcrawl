#!/usr/bin/python
"""Crawls the web looking for quantitative information about bitcoin popularity.

	Examples (require Internet connection):
	>>> bitcrawl

	MtGox price is $4.79240
	
	Standard Module Dependencies:
		argparse	ArgumentParser
		urllib  	urlencode, urlopen,...
		urllib2 	HTTPRedirectHandler, HTTPCookieProcessor, ...
		time    	sleep
		datetime	now()
		httplib 	IncompleteRead
	Nonstandard Module Dependencies:
		tz      	Local

	TODO:
	1. deal with csv: http://www.google.com/trends/?q=bitcoin&ctab=0&geo=us&date=ytd&sort=0 , 
	      <a href='/trends/viz?q=bitcoin&date=ytd&geo=us&graph=all_csv&sort=0&scale=1&sa=N'>
	      other examples in comments below
	2. poll domain name registries to determine the number of domain names with "bitcoin" in them or beginning with "bit" or having "bit" and "coin" in them 
	3. build website and REST to share bitcoin trend info, several domain names saved at bustaname under shopper@tg username 
	      pairbit, bitpair, coinpair, paircoin, coorbit, bitcorr, bitcoinarbitrage, etc
	4. generalize the search with AI and ML to identify good and bad trends for all common proper names--stock symbols, etc
	   a) write research paper to prove it does as good a job as a human stock analyst at predicting future price movements
	   b) write a browser plugin that allows a human to supervise the machine learning and identify useful/relevant quantitative data
	5. implement the indexer and search engine for the double-star question 3 in CS101 and get quant data directly from the index
	6. implement the levetshire distance algorithm from the CS101 exam for use in word-stemming and search term similarity estimate

	:copyright: 2012 by Hobson Lane (hobson@totalgood.com), see AUTHORS for details
	:license:   Creative Commons BY-NC-SA, see LICENSE for details"""

import bitcrawl as bc
from argparse import ArgumentParser
from warnings import warn

def parse_args():
	"""Parse the command line arguments

		TODO:
			allow user to input a number format and prefix in some form other than python regexes
			add options or dictionary members to hold patterns for "unit-of-measure" and "suffix"
			generalize the format to allow user to ask the miner to count links at the url, rather than just extracting a literal value
	"""

	p = ArgumentParser(description=__doc__.strip())
	p.add_argument(
		'-b','--bitfloor','--bf',
		type    = int,
		nargs   = '?',
		default = 0,
		help    = 'Retrieve this number of prices from the order book at bitfloor (TBD volume).',
		)
	p.add_argument(
		'-g','--graph','--plot',
		nargs = '*',
		default = ['mtgox.average', 'mtgox.last','mtgox.low', 'mtgox.high', 'shop.visits','bitcoin.visits','wikipedia_view_rate_Bitcoin.view_rate_Bitcoin', 'mtgox.wikipedia_view_rate_Bitcoin.view_rate_Bitcoin', 'wikipedia_view_rate_James_Surowiecki.view_rate_James_Surowiecki'],
		help    = 'List of values to plot.',
		)
	p.add_argument(
		'-u','--urls','--url',
		type    = str,
		nargs   = '*',
		default = bc.URLs,
		help    = 'URL to mine data. OR. List of dict of dict [{{,,},{,,,}},{{,,},{,,,}},,,] defining regexs and URLs to extract data.',
		)
	p.add_argument(
		'-p','--prefix',
		type    = str,
		nargs   = '*',
		default = '', 
		help    = 'HTML that preceeds the desired numerical text.',
		)
	p.add_argument(
		'-r','--regex','--regexp','--re',
		type    = str,
		nargs   = '*',
		default = '',
		help    = 'Python/Perl regular expression to capture numerical string only.',
		)
	p.add_argument(
		'-v','--verbose',
		action  = 'store_true',
		default = False,
		help    = 'Print out (to stdout) progress messages.',
		)
	p.add_argument(
		'-q','--quiet',
		action  = 'store_true',
		default = False,
		help    = "Don't output anything to stdout, not even the numerical values minded. Overrides verbose setting.",
		)
	p.add_argument(
		'-n','--no-mine','--no-mining','--no-data','--no-datamining','--no-crawl','--no-crawling',
		dest    = 'nomine',
		action  = 'store_true',
		default = False,
		help    = "Don't crawl the internet for numerical data.",
		)
	p.add_argument(
		'-f','--path','--filename',
		type    = str,
		#nargs  = '*', # other options '*','+', 2
		default = bc.FILENAME,
		help    = 'File to append the numerical data to (after converting to a string).',
		)
	return p.parse_args()

if __name__ == "__main__":
	o = parse_args()
	
	data = None
	if not o.quiet or o.verbose:
		data = bc.load_json(filename=o.path,verbose='Historical data...') # verbose means the data will print out with that as the heading

	sites = []
	values = []
	if o.graph and isinstance(o.graph,list) and isinstance(o.graph[0],str):
		for u,v in [g.split('.') for g in o.graph]:
			sites.append(u)
			values.append(v)
	elif o.graph and isinstance(o.graph,str):
		u,v = g.split('.')
		sites.append(u)
		values.append(v)

	# This is the hard coded proof-of-concept forecasting algorithm
	print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
	print 'Correlation coefficient for the data series selected'
	print '("wikipedia view rates for bitcoin page" and "MtGox bitcoin average" price)'
	print ' is...'
	print bc.forecast_data(columns=None, # reload historical data and extract values listed below
							site=sites, # extract records for these websites
							value=values, # use these values from those pages
							quiet=True)
	#TODO calculate for all paramters and find the maximum
	print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'

	if o.graph and isinstance(o.graph,list) and isinstance(o.graph[0],str):
			bc.plot_data(columns=None,site=u,value=v,title=u+'--'+v)
		bc.plot_data(columns=None,site=u,value=v)

	if not o.nomine:
		# mine hard-coded urls
		d = dict()
		if type(o.urls)==dict:
			# TODO: this check and "iterification" of mine_data() should happen inside the function
			# check to see if all the dictionary keys look like urls
			if bc.are_all_urls(o.urls):
				for u,r in o.urls.items():
					d[u]=bc.mine_data(url=u, prefixes=r, verbose=not o.quiet)
			# otherwise assume the new format where each dict key is a name, and 'url' is a key of the nested dict
			else:
				for name,r in o.urls.items():
					d[name]=bc.mine_data(url=r.pop('url'), prefixes=r, verbose=not o.quiet)
		else:
			raise ValueError('Invalid URL, prefix, or regex argument.')
	
		# CRAWLING and MINING done here, data stored as a list of lists of dicts of dicts
		data=[ d,
			   bc.bitfloor_book       (            verbose=not o.quiet),
			   bc.wikipedia_view_rates(            verbose=not o.quiet),
			   bc.get_links           (max_depth=0,verbose=not o.quiet)
			 ]

		# compose a json string that can be appended to the end of a list within a json file (prefix = '')
		json_string = bc.join_json(data,prefix='',suffix='\n]\n') 

		# TODO: make writable() check for a regex match (for formating and content verificaiton)
		# TODO: make writable() write the file with acceptable initial content
		if not bc.updateable(o.path,initial_content='[\n\n]\n'): 
			print 'ERROR! Unable to log data to "'+o.path+'". Printing to stdout instead...'
			print json_string 
			raise RuntimeError('Unable to log data to "'+o.path+'".')

		# TODO: create a function in bitcrawl module for appending new json data to existing data, as this block does
		# see http://stackoverflow.com/a/1466036/623735 for definitions of file modes (write, read, update)
		#     + = update
		#    a+ = only allow you to seek and write after the end of the existing data 
		#    w+ = truncate (delete existing data) before opening and updating/writing with new data
		#    r+ = leaves existing contents in tact and allows writing, reading, seeking anywhere (random access)
		with open(o.path,'r+') as f: 
			# pointer should be at the end already due to append mode, but it's not,
			f.seek(0,2)  # go to position 0 relative to 2=EOF (1=current, 0=begin), not sure if this is required before the -3 seek
			f.seek(-3,2) # if you do this before seek(0,2) on a "a+" or "w+" file you get "[Errno 22] Invalid argument"
			if f.tell()>10: # file isn't empty
				f.write(',\n') # to allow continuation of the json array/list by overwriting the ']' that terminates the existing list
			else:
				f.write('\n') # to allow continuation of the json array/list by overwriting the ']' that terminates the existing list
			f.write(json_string)
			if not o.quiet:
				print 'Appended json records to "'+o.path+'"'
				try:
					print 'MtGox price is '+str(data[0]['mtgox']['average'])
				except KeyError:
					print 'Unable to retrieve the MtGox price. Network dropout? Format change at MtGox?'

	if o.verbose:
		'New data extracted from web pages...'
		print json_string

