import requests
from bs4 import BeautifulSoup
import os

def scrape(act):
    os.mkdir(act)

    url = "https://lex.bg/bg/laws/tree/" + act
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("div", class_="boxi boxinb") # Find and write all divs with the selected class

    links = []
    for result in results: # Iterate between the items found
        hrefs = result.find_all("a", class_=act) # Iterate through all items with 'a' attribute with the defined class 
        for href in hrefs:
            links.append(href["href"])

    print('\nLinks scraped: ' + str(len(links)))

    for link in links:
        doc = requests.get(link) # Iterate through the found pages
        soup = BeautifulSoup(doc.content, "html.parser")
        content = soup.find("div", class_="boxi boxinb") # Extract the div where the meaningful text is 
        title = content.find("div", id="DocumentTitle") # Get the title    
        if title:
            print(title.text)
            
            unwanted = content.find("div", 
                style="background:#cbcbcb; color:#323476; height:25px; width:180px; font-weight:bold; font-size:11px; text-align:center; ") # Find and remove unwanted text
            unwanted.extract()
            unwanted = content.find("div", id="tl", style="margin: 0 auto;") # Find and remove flash player message
            unwanted.extract()

            f = open(act + "/" + title.text + ".txt", "x", encoding="utf-8") # Create a file as title
            f.write(content.text.strip())
            f.close()

acts = ["code", "ords", "laws", "regs", "reg_laws", "lastdv"]
for act in acts:
    scrape(act)
