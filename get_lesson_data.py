
# coding: utf-8

# ## Structure of DataCamp Lessons
# 
# Before we get into the code, I want to look at how DataCamp courses are structured and what is the information I want to store in my notes.
# 
# Courses are divided in to **chapters**. Each chapter is comprised of several **lessons**.
# 
# ![](/images/datacamp.png)
# 
# For each lesson, there's (1) a description of the exercises, (2) instructions, (3) starter code, and (4) a success message that appears once you've submitted the (5) correct code.
# 
# ![](/images/dc_lesson_start.png)
# 
# ![](/images/dc_lesson_finish.png)
# 
# In my previous post, I showed how I was able to iterate through all the chapters and lessons from the course landing page. In this post, I'll focus on how I extracted all the lesson info.

# ## Extracting Lesson Info
# 
# First, I import the relevant packages.

# In[1]:


from urllib.request import urlopen         #For fetching the webpage
from bs4 import BeautifulSoup              #For parsing the HTML
import json                                #For dealing with website data that comes in JSON
import subprocess                          #For accessing pandoc
from subprocess import Popen, PIPE, STDOUT #For accessing pandoc
import re                                  #For regex searching
import pprint                              #For reading through JSONs


# Next, I get the website and turn it into a `BeautifulSoup` object. (In order to do this, I drew on [this blogpost](https://www.datacamp.com/community/tutorials/web-scraping-using-python) and the [package documentation](https://beautiful-soup-4.readthedocs.io/en/latest/).)

# In[2]:


url = 'https://campus.datacamp.com/courses/experimental-design-in-r/introduction-to-experimental-design?ex=2'
html = urlopen(url)
soup = BeautifulSoup(html, 'lxml')


# After noodling around in the HTML for a while, I figured out that the data I needed to access was in a JSON. That JSON was nested in a text string that itself was nested in a `<script>` tag. So I needed to extract the string from the `<script>`, and the JSON from the string.

# In[3]:


string = soup.find_all('script')[3].string
json_text = string.strip('window.PRELOADED_STATE=')[:-1]
lesson_json = json.loads(json_text)


# With the JSON in hand, I started looking through the keys. I won't show it here, but [`pprint`](https://docs.python.org/3/library/pprint.html) was *extremely* helpful in wading through the JSON code in order to figure out which keys were important. In the end, I drilled down to `'all'`. It turned out that all the information for all the lessons in the chapter was on this one page, in a list of dictionary through which I could iterate. Sweet!

# In[4]:


print(lesson_json.keys())


# In[5]:


print(lesson_json['exercises'].keys())


# In[6]:


print(type(lesson_json['exercises']['all']))


# In[7]:


print(lesson_json['exercises']['all'][1].keys())


# In DataCamp courses, there are different types of lessons (free coding, multiple-choice, etc), and that information is stored in `'type'`.

# In[8]:


for item in lesson_json['exercises']['all']:
    print(item['type'], ':', item['title'])


# I could skip video exercises because there was no text to capture. However, normal, bullet and multiple-choice exercises each required slightly different treatments. So I made functions for each of them.

# In[9]:


def NormalExercise_print(json):
    print('#', json['title'], '\n')
    print('## Exercise\n')
    print(convert_2_md(json['assignment']))
    print('## Instructions\n')
    print(convert_2_md(json['instructions']))
    print('## Code\n')
    print('```\n' + convert_2_md(json['sample_code']).replace('\\', ''),'\n```')
    print('```\n' + convert_2_md(json['solution']).replace('\\', ''),'\n```')
    print(get_success_msg(json['sct']) + '\n')


# In[10]:


def BulletExercise_print(json):
    print('# ' + json['title'], '\n')
    print('## Exercise\n')
    print(convert_2_md(json['assignment']))
    print('## Instructions & Code \n')  
    for item in json['subexercises']:
        print(convert_2_md(item['instructions']))
        print('```\n' + item['sample_code'] + '\n```')
        print('```\n' + item['solution']    + '\n```')
        print(get_success_msg(item['sct']) + '\n')


# In[11]:


def MultipleChoiceExercise_print(json):
    print('# ' + json['title'], '\n')
    print('## Exercise\n')
    print(convert_2_md(json['assignment']))
    print("## Choices\n")
    for choice in json['instructions']:
        print('* ' + choice)
    print('\n**Correct answer: ' + get_correct_mc(json['sct']) + '**\n')
    print(get_success_msg(json['sct']) + '\n')


# In order to make these functions easier to work with (and to follow some of the coding practices I learned as part of my [Carpentry](https://carpentries.org) certification, I created a few sub-functions. The most interesting of these was `convert_2_md()`, which converts HTML syntax to Markdown using [`pandoc`](http://pandoc.org). In order to do that, I had to learn a little bit about the `subprocess` package. [This blog post](http://www.practicallyefficient.com/2016/12/04/pandoc-and-python.html) by [Eddie Smith](https://twitter.com/eddie_smith) was a big help. Here's what I ended up with:

# In[12]:


def convert_2_md(string):
    p = Popen(['pandoc', '-f', 'html', '-t', 'markdown', '--wrap=preserve'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    text = p.communicate(input=string.encode('utf-8'))[0]
    text = text.decode('utf-8')
    return text


# I also needed a function to pull out the message you get from a DataCamp lesson when you submit the correct answer. This is where regex expressions came in with `re`.

# In[13]:


def get_success_msg(string):
    match = re.search(r'success_msg\("(.*?)"\)', string)
    if match != None:
        message = match.group(1)
        return message
    else:
        return ''


# And while we're at it, why not one for finding the correct answer in multiple-choice lessons?

# In[14]:


def get_correct_mc(string):
    match = re.search(r'test_mc\(correct = (\d),', string)
    if match != None:
        message = match.group(1)
        return message
    else:
        return ''


# ## The Payoff
# 
# At this point, I would like to thank you for getting this far into the post (most likely because you're a member of my family or a super nerd). Either way, you've made it to the good stuff. Here's the function that brings everything together. It looks at the type of lesson, parses it accordingly, and prints everything out in Markdown.

# In[15]:


for item in lesson_json['exercises']['all']:
    if item['type'] == 'VideoExercise':
        pass
    elif item['type'] == 'NormalExercise':
        NormalExercise_print(item)
    elif item['type'] == 'BulletExercise':
        BulletExercise_print(item)
    elif item['type'] == 'MultipleChoiceExercise':
        MultipleChoiceExercise_print(item)


# I didn't include the full output here, but you get the idea. All the info I need is in Markdown format for my notes. All that time I would've wasted on copying and pasting can now be spent on moving quickly through the lesson.
# 
# The next step will be to put this and the previous post together to iterate through the whole course and build several Markdown documents at once: A table of contents and a file for each chapter. Can't wait to put it all together!
