import requests
from bs4 import BeautifulSoup
import os
import shutil
import re

def scrape(act, page_number):
    url = "https://lex.bg/bg/laws/tree/" + act + "/" + page_number
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("div", class_="boxi boxinb") # Find and write all divs with the selected class

    links = []
    for result in results: # Iterate between the items found
        if act == "ords" or act == "laws": 
            act_class = "law" 
        else: 
            act_class = act
        hrefs = result.find_all("a", class_=act_class) # Iterate through all items with 'a' attribute with the defined class 
        for href in hrefs:
            links.append(href["href"])

    print('\nLinks scraped: ' + str(len(links)))

    same_title_counter = 1 # Some laws have the same titles; this helps increment an int, which is then appended to the end of the filename

    for link in links:
        doc = requests.get(link) # Iterate through the found pages
        soup = BeautifulSoup(doc.content, "html.parser")
        content = soup.find("div", class_="boxi boxinb") # Extract the div where the meaningful text is 
        title = content.find("div", id="DocumentTitle") # Get the title object
        if title:
            print(title.text + " : " + str(len(title.text))) # Print count of characters in the title 
            trimmed_title = trim_title(title.text) # Trim the title if it's too long as it is used for filenames
            unwanted = content.find("div", 
                style="background:#cbcbcb; color:#323476; height:25px; width:180px; font-weight:bold; font-size:11px; text-align:center; ") # Find and remove unwanted text
            if unwanted is not None: unwanted.extract()
            unwanted = content.find("div", id="tl", style="margin: 0 auto;") # Find and remove flash player message
            if unwanted is not None: unwanted.extract()
            if not trimmed_title.isalnum(): # Remove special characters characters from title 
                final_title = re.sub('[()//\"]', "", trimmed_title)    
            else:
                final_title = trimmed_title
            print("Final title: " + final_title)
            try:
                write_to_file(act, final_title, content)
            except FileExistsError:
                same_title_counter += 1 # increment the value
                final_title = final_title + str(same_title_counter) # Append the counter, to ensure no files have the same name
                write_to_file(act, final_title, content)

def write_to_file(act, final_title, content):
    f = open("docs/" + act + "/" + final_title + ".txt", "x", encoding="utf-8") # Create a file as title
    f.write(content.text.strip())
    f.close()

def trim_title(title): # This checks if title is long and trims it to be used as filename
    if len(title) > 99: 
        trimmed_title = title[0:98]
    else:
        trimmed_title = title
    return trimmed_title

acts = {"code": 1, "ords": 70, "laws": 12, "regs": 15, "reg_laws": 2} # "code": 1, "ords": 70, "laws": 12, "regs": 15, "reg_laws": 2
for act, pages in acts.items():
    path = "docs/" + act
    try:
        os.mkdir(path)
    except FileExistsError:
        shutil.rmtree(path)
        os.mkdir(path)
        pass
    for page_number in range(pages):
        scrape(act, str(page_number))