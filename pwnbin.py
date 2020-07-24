import time

try: 
    from urllib.request import urlopen
    from urllib.error import HTTPError, URLError
except ImportError: 
    from urllib2 import urlopen, HTTPError, URLError

import datetime
import sys, getopt
from bs4 import BeautifulSoup

try: 
    from io import StringIO
except ImportError: 
    from StringIO import StringIO

import gzip
from configparser import ConfigParser
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import platform
import requests
from pyvirtualdisplay import Display
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By

def main(argv):

    length = 0
    time_out = False
    found_keywords = []
    mailed_keywords=[]
    paste_list = set([])
    root_url = 'http://pastebin.com/'
    raw_url = 'http://pastebin.com/raw/'
    start_time = datetime.datetime.now()
    file_name, keywords, append, run_time, match_total, crawl_total, mail_conf, emails, main_loop_wait_time, use_selenium, use_virtual_display = initialize_options(argv)

    driver = None
    display = None

    if use_virtual_display:
        
        if platform.system() == "Linux" :
            print("Starting virtual display")
            display = Display(visible=0, size=(1920, 1200))  
            display.start()
        else:
            print("Virtual display is only supported on Linuxes because it uses xvfb, continuing with real display...")
    
    if use_selenium:
        
        print("Starting browser")
        # Avoid error https://bugs.chromium.org/p/chromedriver/issues/detail?id=2473
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60)

        # Minimize window if no virtual display
        if not display:
            try: driver.minimize_window()
            # Can fail if running with a virtual display
            except selenium.common.exceptions.WebDriverException: pass

    print("Crawling PasteBin... Pastes are saved to logfile %s" % (file_name))

    try:
        # Continually loop until user stops execution
        while True:

            #    Get pastebin home page html
            try:
                root_html = BeautifulSoup(fetch_page(root_url, use_selenium, driver), 'html.parser')

            #    If http request returns an error and 
            except requests.exceptions.HTTPError as err:
                if err.code == 404:
                    print("\Error 404: Root page not found!")
                    sys.exit(1)
                elif err.code == 403:
                    print("Error 403: Pastebin is mad at you!")
                    sys.exit(1)
                else:
                    print("You\'re on your own on this one! Error code %s"%err.code)
                    sys.exit(1)

            except requests.exceptions.TooManyRedirects as err:
                print("Too many redirects error loading root page")
                sys.exit(1)

            #    For each paste in the public pastes section of home page
            for paste in find_new_pastes(root_html):
                
                #    look at length of paste_list prior to new element
                length = len(paste_list)
                paste_list.add(paste)

                #    If the length has increased the paste is unique since a set has no duplicate entries
                if len(paste_list) > length:
                    
                    #    Add the pastes url to found_keywords if it contains keywords
                    raw_paste = raw_url+paste
                    try:
                        found_keywords = find_keywords(raw_paste, found_keywords, keywords, use_selenium, driver)       
                    #    If http request returns an error and 
                    except requests.exceptions.HTTPError as err:
                        if err.code == 404:
                            print("\Error 404: Paste not found! Skipping paste")
                            continue
                        elif err.code == 403:
                            print("Error 403: Pastebin is mad at you!")
                            sys.exit(1)
                        else:
                            print("You\'re on your own on this one! Error code %s"%err.code)
                            sys.exit(1)

                    except requests.exceptions.TooManyRedirects as err:
                        print("Too many redirects error loading paste. Trying to load paste from HTML textarea")
                        try:
                            found_keywords = find_keywords(root_url+paste, found_keywords, keywords, use_selenium, driver, from_textarea=True)
                        except Exception as err:
                            print("Failed: %s"%err)
                            continue

                time.sleep(2)     

            print("Crawled total of %d Pastes, Keyword matches %d" % (len(paste_list), len(found_keywords)))
            print('\n'.join(found_keywords))
            # Write paste info to file
            write_out(found_keywords, append, file_name)

            # Determine list of new found keywords and send them by email
            new_keywords = [item for item in found_keywords if item not in mailed_keywords]
            if len(new_keywords) and emails:
                # Sendmail
                mail_paste(new_keywords, mail_conf, emails)
                mailed_keywords.extend(new_keywords)

            if run_time!=None and (start_time + datetime.timedelta(seconds=run_time)) < datetime.datetime.now():
                print("Reached time limit, Found %d matches." % len(found_keywords))
                sys.exit()

            # Exit if surpassed specified match timeout 
            if match_total!=None and len(found_keywords) >= match_total:
                print("Reached match limit, Found %d matches." % len(found_keywords))
                sys.exit()

            # Exit if surpassed specified crawl total timeout 
            if crawl_total!=None and len(paste_list) >= crawl_total:
                print("Reached total crawled Pastes limit, Found %d matches." % len(found_keywords))
                sys.exit()
            
            print("Sleeping %s seconds"%(main_loop_wait_time))
            time.sleep(main_loop_wait_time)

    #     On keyboard interupt
    except KeyboardInterrupt:
        print("Interrupted")
        sys.exit(1)

    finally:
        print("Exiting")
        if driver: 
            driver.quit()
            if display: 
                display.stop()
        # Write pastes to file
        write_out(found_keywords, append, file_name)

def write_out(found_keywords, append, file_name):
    #     if pastes with keywords have been found
    if len(found_keywords):

        #    Write or Append out urls of keyword pastes to file specified
        if append:
            f = open(file_name, 'a')
        else:
            f = open(file_name, 'w')

        for paste in found_keywords:
            f.write(paste+'\n')

def find_new_pastes(root_html):
    new_pastes = []
    
    ul = None
    div = root_html.find('div', {'id': 'menu_2'})

    # Fixed AttributeError: 'NoneType' object has no attribute 'find' in new pastebin HTML
    if div:
        ul = div.find('ul', {'class': 'right_menu'})
    else:
        ul = root_html.find('ul', {'class': 'sidebar__menu'})

    if not ul:
        raise ValueError("Could not find new pastes list in root page HTML: \n%s"%root_html)

    for li in ul.findChildren():
        if li.find('a'):
            new_pastes.append(str(li.find('a').get('href')).replace("/", ""))

    return new_pastes

def find_keywords(url, found_keywords, keywords, use_selenium=False, driver=None, from_textarea=False):
    if from_textarea:
        soup = BeautifulSoup(fetch_page(url, use_selenium, driver))
        paste = soup.find('textarea').getText()
    else:
        paste = fetch_page(url, use_selenium, driver, raw=True)

    #    Todo: Add in functionality to rank hit based on how many of the keywords it contains
    for keyword in keywords:
        if paste.find(keyword.encode()) != -1:
            found_keywords.append("found " + keyword + " in " + url)
            break

    return found_keywords

def fetch_page(page, use_selenium=False, driver=None, raw=False):
    
    if use_selenium and driver:
        print("Fetching %s with Selenium"%(page))
        driver.get(page)
        html = driver.page_source
        try: 
            driver.find_element_by_id("challenge-form")
            raise ValueError("Pastebin is asking for a CAPTCHA!")
        except selenium.common.exceptions.NoSuchElementException:
            pass
        if raw:
            return driver.find_element_by_tag_name('body').text.encode()
        else:
            return html

    else:
        print("Fetching %s"%(page))
        response = requests.get(page)
        response.raise_for_status()
        return response.text.encode()

def initialize_options(argv):
    keywords = ['ssh', 'pass', 'key', 'token']
    file_name = 'log.txt'
    append = False
    run_time = None
    match_total = None
    crawl_total = None
    mail_conf = None
    emails = None
    main_loop_wait_time = 30
    use_selenium = False
    use_virtual_display = False

    try:
        opts, args = getopt.getopt(argv,"h:k:o:t:n:m:ac:e:w:sv")
    except getopt.GetoptError:
        print('Basic usage: pwnbin.py -k <keyword1>,<keyword2>,<keyword3>... -o <outputfile>\nVisit https://github.com/kahunalu/pwnbin for more informations.')
        sys.exit(2)

    for opt, arg in opts:

        if opt == '-h':
            print('Basic usage: pwnbin.py -k <keyword1>,<keyword2>,<keyword3>... -o <outputfile>\nVisit https://github.com/kahunalu/pwnbin for more informations.')
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
                print("Time must be an integer representation of seconds.")
                sys.exit()
        elif opt == '-m':
            try:
                match_total = int(arg)
            except ValueError:
                print("Number of matches must be an integer.")
                sys.exit()

        elif opt == '-n':
            try:
                crawl_total = int(arg)
            except ValueError:
                print ("Number of total crawled pastes must be an integer.")
                sys.exit()

        elif opt == "-c":
            config=ConfigParser()
            config.read_file(open(arg, 'r'))
            mail_conf=dict(config['pwnbin-mail-alerts'])

        elif opt == "-e":
            emails = list(arg.split(","))
        
        elif opt == "-w":
            main_loop_wait_time = int(arg)

        elif opt == "-s":
            use_selenium = True

        elif opt == "-v":
            use_virtual_display = True
            use_selenium = True

    if emails and not mail_conf:
        print("You must set mail configuration with -c <file> to send paste alerts by emails.")
        sys.exit()

    return file_name, keywords, append, run_time, match_total, crawl_total, mail_conf, emails, main_loop_wait_time, use_selenium, use_virtual_display

def mail_paste(found_keywords, mail_conf, emails):
    print("Sending an email alert to %s for new paste %s"%(emails, found_keywords))

    # Building message
    message = MIMEMultipart("html")
    message['Subject'] = 'pwnbin ALERT : keyword found in new paste'
    message['From'] = mail_conf['fromaddr']
    message['To'] = ','.join(emails)
    body = '\n'.join(found_keywords)
    body += '\n\nThis is an automated message, please do not reply.\n--\npwnbin'
    message.attach(MIMEText(body))

    # Sendmail
    server = smtplib.SMTP(mail_conf['smtp_server'])
    server.ehlo_or_helo_if_needed()
    if mail_conf['smtp_ssl'] : server.starttls()
    if mail_conf['smtp_auth'] : server.login(mail_conf['smtp_username'], mail_conf['smtp_password'] )
    server.sendmail(mail_conf['fromaddr'] , ','.join(emails), message.as_string())
    server.quit()

if __name__ == "__main__":
    main(sys.argv[1:])
