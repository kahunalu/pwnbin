import time
import urllib2
import datetime
import sys, getopt
from bs4 import BeautifulSoup
from StringIO import StringIO
import gzip

def main(argv):

	length 									= 0
	time_out 								= False
	found_keywords							= []
	paste_list 								= set([])
	root_url 								= 'http://pastebin.com'
	raw_url 								= 'http://pastebin.com/raw/'
	start_time								= datetime.datetime.now()
	file_name, keywords, append, run_time, match_total, crawl_total = initialize_options(argv)

	print "\nCrawling %s Press ctrl+c to save file to %s" % (root_url, file_name)

	try:
		# Continually loop until user stops execution
		while True:

			#	Get pastebin home page html
			root_html = BeautifulSoup(fetch_page(root_url), 'html.parser')
			
			#	For each paste in the public pastes section of home page
			for paste in find_new_pastes(root_html):
				
				#	look at length of paste_list prior to new element
				length = len(paste_list)
				paste_list.add(paste)

				#	If the length has increased the paste is unique since a set has no duplicate entries
				if len(paste_list) > length:
					
					#	Add the pastes url to found_keywords if it contains keywords
					raw_paste = raw_url+paste
					found_keywords = find_keywords(raw_paste, found_keywords, keywords)

				else:

					#	If keywords are not found enter time_out
					time_out = True

			# Enter the timeout if no new pastes have been found
			if time_out:
				time.sleep(2)

			sys.stdout.write("\rCrawled total of %d Pastes, Keyword matches %d" % (len(paste_list), len(found_keywords)))
			sys.stdout.flush()

			if run_time and (start_time + datetime.timedelta(seconds=run_time)) < datetime.datetime.now():
				sys.stdout.write("\n\nReached time limit, Found %d matches." % len(found_keywords))
				write_out(found_keywords, append, file_name)
				sys.exit()

			# Exit if surpassed specified match timeout 
			if match_total and len(found_keywords) >= match_total:
				sys.stdout.write("\n\nReached match limit, Found %d matches." % len(found_keywords))
				write_out(found_keywords, append, file_name)
				sys.exit()

			# Exit if surpassed specified crawl total timeout 
			if crawl_total and len(paste_list) >= crawl_total:
				sys.stdout.write("\n\nReached total crawled Pastes limit, Found %d matches." % len(found_keywords))
				write_out(found_keywords, append, file_name)
				sys.exit()

	# 	On keyboard interupt
	except KeyboardInterrupt:
		write_out(found_keywords, append, file_name)

	#	If http request returns an error and 
	except urllib2.HTTPError, err:
		if err.code == 404:
			print "\n\nError 404: Pastes not found!"
		elif err.code == 403:
			print "\n\nError 403: Pastebin is mad at you!"
		else:
			print "\n\nYou\'re on your own on this one! Error code ", err.code
		write_out(found_keywords, append, file_name)

	#	If http request returns an error and 
	except urllib2.URLError, err:
		print "\n\nYou\'re on your own on this one! Error code ", err
		write_out(found_keywords, append, file_name)


def write_out(found_keywords, append, file_name):
	# 	if pastes with keywords have been found
	if len(found_keywords):

		#	Write or Append out urls of keyword pastes to file specified
		if append:
			f = open(file_name, 'a')
		else:
			f = open(file_name, 'w')

		for paste in found_keywords:
			f.write(paste)
		print "\n"
	else:
		print "\n\nNo relevant pastes found, exiting\n\n"

def find_new_pastes(root_html):
	new_pastes = []

	div = root_html.find('div', {'id': 'menu_2'})
	ul = div.find('ul', {'class': 'right_menu'})
	
	for li in ul.findChildren():
		if li.find('a'):
			new_pastes.append(str(li.find('a').get('href')).replace("/", ""))

	return new_pastes

def find_keywords(raw_url, found_keywords, keywords):
	paste = fetch_page(raw_url)

	#	Todo: Add in functionality to rank hit based on how many of the keywords it contains
	for keyword in keywords:
		if paste.find(keyword) != -1:
			found_keywords.append("found " + keyword + " in " + raw_url + "\n")
			break

	return found_keywords

def fetch_page(page):
	response = urllib2.urlopen(page)
	if response.info().get('Content-Encoding') == 'gzip':
		response_buffer = StringIO(response.read())
		unzipped_content = gzip.GzipFile(fileobj=response_buffer)
		return unzipped_content.read()
	else:
		return response.read()

def initialize_options(argv):
	keywords 			= ['ssh', 'pass', 'key', 'token']
	file_name 			= 'log.txt'
	append 				= False
	run_time 			= 0
	match_total			= None
	crawl_total	 		= None

	try:
		opts, args = getopt.getopt(argv,"h:k:o:t:n:m:a")
	except getopt.GetoptError:
		print 'pwnbin.py -k <keyword1>,<keyword2>,<keyword3>..... -o <outputfile>'
		sys.exit(2)

	for opt, arg in opts:

		if opt == '-h':
			print 'pwnbin.py -k <keyword1>,<keyword2>,<keyword3>..... -o <outputfile>'
			sys.exit()
		elif opt == '-a':
			append = True
		elif opt == "-k":
			keywords = set(arg.split(","))
		elif opt == "-o":
			file_name = arg
		elif opt == "-t":
			try:
				run_time = int(arg)
			except ValueError:
				print "Time must be an integer representation of seconds."
				sys.exit()
		elif opt == '-m':
			try:
				match_total = int(arg)
			except ValueError:
				print "Number of matches must be an integer."
				sys.exit()

		elif opt == '-n':
			try:
				crawl_total = int(arg)
			except ValueError:
				print "Number of total crawled pastes must be an integer."
				sys.exit()

	return file_name, keywords, append, run_time, match_total, crawl_total

if __name__ == "__main__":
	main(sys.argv[1:])
