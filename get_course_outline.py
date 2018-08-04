
# coding: utf-8

# Most of what I've learned about data sciences has come from the courses I've taken at [DataCamp](http://datacamp.com/). Until now, every time I take a course, I copy and paste the course outline into a Markdown file. This gives me an archive I can refer to when I face similar problems down the road. But it takes time, time I could be using to take more DataCamp courses!
# 
# It recently occurred to me that I could use what I've been learning to automate the archiving process. So after spending some quality time with the [Beautiful Soup](https://beautiful-soup-4.readthedocs.io/en/latest/) documentation, staring at the HTML for [this](https://www.datacamp.com/courses/experimental-design-in-r) DataCamp course, and [asking for advice](https://stackoverflow.com/questions/51659976/store-web-scraping-results-in-dataframe-or-dictionary) on Stack Overflow, I've come up with a solution.
# 
# First, this is what the website for a DataCamp course looks like:
# 
# ![Screenshot of DataCamp Course](/images/datacamp.png)

# And here's the code I put together:

# In[1]:


from urllib.request import urlopen
from bs4 import BeautifulSoup
from collections import OrderedDict

url = 'https://www.datacamp.com/courses/experimental-design-in-r'
html = urlopen(url)
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


# The two big things I learned here are how `Beautiful Soup` organizes the data it scrapes from a website and how you can put lists and tuples inside of dictionaries. This last one was a real sticking point as I was deciding how to structure the data.
# 
# When it's all said and done, here's the data that I'll write into a Markdown file:

# In[2]:


for chapter, lessons in chapters.items():
    print('\n# ', chapter, '\n')
    for lesson_name, lesson_link in lessons:
        print("   *", lesson_name)


# The next step will be to tweak the output to better work with my note-taking system ([Zettelkasten](https://zettelkasten.de) all the way, baby!). That should be easy. Then I'd like to iterate through each lesson and turn those into notes, too. That will be harder. 
# 
# For now, the good news is that I'm using the things I've learned to accelerate the pace at which I can learn more things. It's like compounding interest for your brain. 📈🧠 

# In[3]:


import pprint


# In[4]:


pprint.pprint(chapters)

