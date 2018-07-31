import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
import subprocess
from subprocess import Popen, PIPE, STDOUT

def get_instructions(url):
	'''Accepts URL of DC lesson and returns list'''
    html = urlopen(url)
    soup = BeautifulSoup(html, 'lxml')
    
    title = soup.title
    intro = soup.find_all('p')[1]
    instructions = soup.find_all('li')[0]
    
    package = [title, intro, instructions]
    
    return package

 def convert_2_md(bytes):
 	'''Accepts data from BeautifulSoup hits, converts to Markdown, returns str'''
 	p = Popen(['pandoc', '-f', 'html', '-t', 'markdown', '--wrap=preserve'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
 	text = p.communicate(input=bytes.encode('utf-8'))[0]
 	text = text.decode('utf-8')
 	return text