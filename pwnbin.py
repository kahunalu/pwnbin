from bs4 import BeautifulSoup
import urllib2
import time
import sys

keywords = ['ssh', 'pass', 'key', 'token']
root_url = 'http://pastebin.com'
raw_url = 'http://pastebin.com/raw.php?i='
has_passwords = []

def main():
	paste_list = set([])
	time_out = False
	length = 0

	initialize_keywords()

	print "\nCrawling " + root_url + " Press ctrl+c to save file to log.txt"
	try:
		while True:
			root_html = BeautifulSoup(fetch_page(root_url), 'html.parser')
			for page in find_new_pages(root_html):
				length = len(paste_list)
				paste_list.add(page)
				if len(paste_list) > length:
					find_passwords(raw_url+page)
				else:
					time_out = True

			if time_out:
				time.sleep(2)

			sys.stdout.write("\rCrawled total of %d Pastes, Keyword matches %d" % (len(paste_list), len(has_passwords)))
			sys.stdout.flush()
	except KeyboardInterrupt:
		print "\n\n"
		if len(has_passwords):
			f = open('log.txt', 'w')
			for paste in has_passwords:
				f.write(paste)
		else:
			print "No relevant pastes found, exiting\n\n"
def find_new_pages(root_html):
	new_pastes = []

	div = root_html.find('div', {'id': 'menu_2'})
	ul = div.find('ul', {'class': 'right_menu'})
	for li in ul.findChildren():
		if li.find('a'):
			new_pastes.append(str(li.find('a').get('href')).replace("/", ""))

	return new_pastes

def find_passwords(raw_url):
	paste = fetch_page(raw_url)

	for keyword in keywords:
		if keyword in paste:
			has_passwords.append("found " + keyword + " in " + raw_url + "\n")
		break

def fetch_page(page):
	response = urllib2.urlopen(page)
	return response.read()

def initialize_keywords():
	global keywords
	if len(sys.argv) is 2:
		keywords = set(sys.argv[1].replace("-k=", "").split(","))

if __name__ == "__main__":
	main()