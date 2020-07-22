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

def main(argv):

    length = 0
    time_out = False
    found_keywords = []
    mailed_keywords=[]
    paste_list = set([])
    root_url = 'http://pastebin.com'
    raw_url = 'http://pastebin.com/raw/'
    start_time = datetime.datetime.now()
    file_name, keywords, append, run_time, match_total, crawl_total, mail_conf, emails, main_loop_wait_time, use_selenium, use_virtual_display = initialize_options(argv)

    driver = None
    display = None

    if use_virtual_display:
        from pyvirtualdisplay import Display
        if platform.system() == "Linux" :
            print("Starting virtual display")
            display = Display(visible=0, size=(1920, 1200))  
            display.start()
        else:
            print("Virtual display is only supported on Linuxes because it uses xvfb, continuing with real display...")
    
    if use_selenium:
        import selenium
        from selenium import webdriver
        print("Starting browser")
        # Avoid error https://bugs.chromium.org/p/chromedriver/issues/detail?id=2473
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60)

    print("Crawling %s Press Ctrl+C to quit and save logfile to %s" % (root_url, file_name))

    try:
        # Continually loop until user stops execution
        while True:

            #    Get pastebin home page html
            root_html = BeautifulSoup(fetch_page(root_url, use_selenium, driver), 'html.parser')
            
            #    For each paste in the public pastes section of home page
            for paste in find_new_pastes(root_html):
                
                #    look at length of paste_list prior to new element
                length = len(paste_list)
                paste_list.add(paste)

                #    If the length has increased the paste is unique since a set has no duplicate entries
                if len(paste_list) > length:
                    
                    #    Add the pastes url to found_keywords if it contains keywords
                    raw_paste = raw_url+paste
                    found_keywords = find_keywords(raw_paste, found_keywords, keywords)       

                time.sleep(2)     

            print("Crawled total of %d Pastes, Keyword matches %d" % (len(paste_list), len(found_keywords)))
            
            # Determine list of new found keywords and send them by email
            new_keywords = [item for item in found_keywords if item not in mailed_keywords]
            if len(new_keywords) and emails:

                mail_paste(new_keywords, mail_conf, emails)
                mailed_keywords.extend(new_keywords)

            if run_time and (start_time + datetime.timedelta(seconds=run_time)) < datetime.datetime.now():
                print("\n\nReached time limit, Found %d matches." % len(found_keywords))
                write_out(found_keywords, append, file_name)
                sys.exit()

            # Exit if surpassed specified match timeout 
            if match_total and len(found_keywords) >= match_total:
                print("\n\nReached match limit, Found %d matches." % len(found_keywords))
                write_out(found_keywords, append, file_name)
                sys.exit()

            # Exit if surpassed specified crawl total timeout 
            if crawl_total and len(paste_list) >= crawl_total:
                print("\n\nReached total crawled Pastes limit, Found %d matches." % len(found_keywords))
                write_out(found_keywords, append, file_name)
                sys.exit()
            
            print("Sleeping %s seconds"%(main_loop_wait_time))
            time.sleep(main_loop_wait_time)

    #     On keyboard interupt
    except KeyboardInterrupt:
        write_out(found_keywords, append, file_name)

    #    If http request returns an error and 
    except HTTPError as err:
        if err.code == 404:
            print("\n\nError 404: Pastes not found!")
        elif err.code == 403:
            print("\n\nError 403: Pastebin is mad at you!")
        else:
            print("\n\nYou\'re on your own on this one! Error code ", err.code)
        write_out(found_keywords, append, file_name)

    #    If http request returns an error and 
    except URLError as err:
        print ("\n\nYou\'re on your own on this one! Error code ", err)
        write_out(found_keywords, append, file_name)

    finally:
        if driver: 
            driver.quit()
            if display: 
                display.stop()

def write_out(found_keywords, append, file_name):
    #     if pastes with keywords have been found
    if len(found_keywords):

        #    Write or Append out urls of keyword pastes to file specified
        if append:
            f = open(file_name, 'a')
        else:
            f = open(file_name, 'w')

        for paste in found_keywords:
            f.write(paste)
        print ("\n")
    else:
        print ("\n\nNo relevant pastes found, exiting\n\n")

def find_new_pastes(root_html):
    new_pastes = []

    div = root_html.find('div', {'id': 'menu_2'})
    ul = div.find('ul', {'class': 'right_menu'})
    
    for li in ul.findChildren():
        if li.find('a'):
            new_pastes.append(str(li.find('a').get('href')).replace("/", ""))

    return new_pastes

def find_keywords(raw_url, found_keywords, keywords):
    paste = fetch_page(raw_url, use_selenium=False)
    #    Todo: Add in functionality to rank hit based on how many of the keywords it contains
    for keyword in keywords:
        if paste.find(keyword.encode()) != -1:
            found_keywords.append("found " + keyword + " in " + raw_url + "\n")
            break

    return found_keywords

def fetch_page(page, use_selenium, driver=None):
    if use_selenium and driver:
        driver.get(page)
        html = driver.page_source
        if 'complete a CAPTCHA' in html:
            raise HTTPError(page, 403, "Pastebin is asking for a CAPTCHA", None, None)
        return str(html)

    else:
        response = urlopen(page)
        if response.info().get('Content-Encoding') == 'gzip':
            response_buffer = StringIO(response.read())
            unzipped_content = gzip.GzipFile(fileobj=response_buffer)
            return unzipped_content.read()
        else:
            return response.read()

def initialize_options(argv):
    keywords = ['ssh', 'pass', 'key', 'token']
    file_name = 'log.txt'
    append = False
    run_time = 0
    match_total = None
    crawl_total = None
    mail_conf = None
    emails = None
    main_loop_wait_time = 2
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
    body = '\n\n'.join(found_keywords)
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
