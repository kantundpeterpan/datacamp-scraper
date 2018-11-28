from bs4 import BeautifulSoup                    #For parsing the HTML
from collections import OrderedDict              #For storing chapter and lesson info
from subprocess import Popen, PIPE, STDOUT       #For accessing pandoc
from urllib.request import urlopen, urlretrieve  #For fetching the webpage, downloading PDF of slides
import json                                      #For dealing with website data that comes in JSON
import pandas as pd                              #For create Zettelkasten-style filenames
import re                                        #For regex parsing of `sct`
import subprocess                                #For accessing pandoc
import pprint                                    #For troubleshooting, looking through webpages, dictionaries, etc

