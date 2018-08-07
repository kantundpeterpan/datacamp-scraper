from bs4 import BeautifulSoup              #For parsing the HTML
from collections import OrderedDict        #For storing chapter and lesson info
from subprocess import Popen, PIPE, STDOUT #For accessing pandoc
from urllib.request import urlopen         #For fetching the webpage
import json                                #For dealing with website data that comes in JSON
import pandas as pd                        #For create Zettelkasten-style filenames
import re  import subprocess               #For accessing pandoc

def get_whole_course(dictionary):
	'''Work in progress. Putting everything together.'''
    z_list = make_z_string(len(dictionary.items()))
    for chapter, lesson in dictionary.items():
        z_index = list(dictionary.keys()).index(chapter)
        print (z_list[z_index], chapter)
        print (dictionary[chapter][0][1])

def make_z_string(num):
    '''Takes int and returns a list of unique, 14-digit numbers. Only goes to 99.'''
    assert num < 100, 'Enter an int that is less than 100. Max list size is 99.'
    string_list = []
    z_index = 0
    for x in range(num):
        z_string = pd.to_datetime('now').strftime('%Y%m%d%H%M')
        z_string = z_string + '{0:0>2}'.format(z_index)
        string_list.append(z_string)
        z_index += 1
    return string_list

def get_course_outline(link):
	'''Receives link to course landing page. Returns ordered dict of chapters with lessons.'''

    html = urlopen(link)
    soup = BeautifulSoup(html, 'lxml')

    lesson_outline = soup.find_all(['h4', 'li'])

    chapters = OrderedDict()   # {chapter: [(lesson_name, lesson_link), ...], ...}

    for item in lesson_outline:
        attributes = item.attrs
        try:
            class_type = attributes['class'][0]
            if class_type == 'chapter__title':
                chapter = item.text.strip()
                chapters[chapter] = []
            if class_type == 'chapter__exercise':
                lesson_name = item.find('h5').text
                lesson_link = item.find('a').attrs['href']
                chapters[chapter].append((lesson_name, lesson_link))
        except KeyError:
            pass

    return(chapters)

def NormalExercise_print(json, f):
    '''Works with make_chapter_notes. Parses NormalExercise type lessons and prints them in 
    markdown to file.'''
    with open(f, 'a') as f:
        print('#', json['title'], '\n', file=f)
        print('## Exercise\n', file=f)
        print(convert_2_md(json['assignment']), file=f)
        print('## Instructions\n', file=f)
        print(convert_2_md(json['instructions'][:-2]), file=f)
        print('## Code\n', file=f)
        print('```\n' + convert_2_md(json['sample_code']).replace('\\', ''),'\n```\n', file=f)
        print('```\n' + convert_2_md(json['solution']).replace('\\', ''),'\n```\n', file=f)
        print(get_success_msg(json['sct']) + '\n', file=f)

def BulletExercise_print(json, f):
    '''Works with make_chapter_notes. Parses BulletExercises type lessons and prints them in 
    markdown to file.'''
    with open(f, 'a') as f:
        print('# ' + json['title'], '\n', file=f)
        print('## Exercise\n', file=f)
        print(convert_2_md(json['assignment']), file=f)
        print('## Instructions & Code \n', file=f)  
        for item in json['subexercises']:
            print(convert_2_md(item['instructions']), file=f)
            print('```\n' + item['sample_code'] + '\n```\n', file=f)
            print('```\n' + item['solution']    + '\n```', file=f)
            print(get_success_msg(item['sct']) + '\n', file=f)

def MultipleChoiceExercise_print(json, f):
    '''Works with make_chapter_notes. Parses MultipleChoice type lessons and prints them in 
    markdown to file.'''
    with open(f, 'a') as f:
        print('# ' + json['title'], '\n', file=f)
        print('## Exercise\n', file=f)
        print(convert_2_md(json['assignment']), file=f)
        print("## Choices\n", file=f)
        for choice in json['instructions']:
            print('* ' + choice, file=f)
        print('\n**Correct answer: ' + get_correct_mc(json['sct']) + '**\n', file=f)
        print(get_success_msg(json['sct']) + '\n', file=f)

def convert_2_md(string):
    '''Receives a string of HTML and use Pandoc to return string in Markdown.'''
    p = Popen(['pandoc', '-f', 'html', '-t', 'markdown', '--wrap=preserve'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    text = p.communicate(input=string.encode('utf-8'))[0]
    text = text.decode('utf-8')
    return text

def get_success_msg(string):
    '''Parses text from DataCamp `sct` JSON and returns the success message as a string.'''
    match = re.search(r'success_msg\("(.*?)"\)', string)
    if match != None:
        message = match.group(1)
        return message
    else:
        return ''

def get_correct_mc(string):
    '''Parses text from DataCamp `sct` JSON and correct answer for MultipleChoice type lessons. Works with MultipleChoiceExercise_print'''
    match = re.search(r'test_mc\(correct = (\d),', string)
    if match != None:
        message = match.group(1)
        return message
    else:
        return ''

def make_chapter_notes(filename, link):
    '''Creates text file in Markdown syntax for entire chapter of DataCamp course.
    Takes name of file to be created and link/location of lesson in chapter.'''
    html = urlopen(link)
    soup = BeautifulSoup(html, 'lxml')
    string = soup.find_all('script')[3].string
    json_text = string.strip('window.PRELOADED_STATE=')[:-1]
    lesson_json = json.loads(json_text)
    
    for item in lesson_json['exercises']['all']:
        if item['type'] == 'VideoExercise':
            pass
        elif item['type'] == 'NormalExercise':
            NormalExercise_print(item, filename)
        elif item['type'] == 'BulletExercise':
            BulletExercise_print(item, filename)
        elif item['type'] == 'MultipleChoiceExercise':
            MultipleChoiceExercise_print(item, filename)