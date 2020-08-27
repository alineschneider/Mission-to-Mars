# Import Splinter, BeautifulSoup and Pandas
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import traceback

def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path=r'C:\Users\aline\Projects\UC_Berkeley\Mission-to-Mars\apps\chromedriver', headless=True)
    news_title, news_paragraph = mars_news(browser)
    cerberus_title, schiaparelli_title, syrtis_title, valles_title, cerberus_url, schiaparelli_url, syrtis_url, valles_url = hemispheres(browser)
    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "cerberus_title": cerberus_title,
      "schiaparelli_title": schiaparelli_title,
      "syrtis_title": syrtis_title,
      "valles_title": valles_title,
      "cerberus_image": cerberus_url,
      "schiaparelli_image": schiaparelli_url,
      "syrtis_image": syrtis_url,
      "valles_image": valles_url,
      "last_modified": dt.datetime.now()
    }
    browser.quit()
    return data

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Set up the HTML parser
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    
    # Add try/except for error handling
    try:
        # Assign "slide_elem" as the variable to look for the <ul> tag and its descendent, and other <li> tags
        # 'slide_elem' is the parent element
        slide_elem = news_soup.select_one('ul.item_list li.slide')

        # Scrape the title
        slide_elem.find("div", class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

# Featured Images

def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url
    


def mars_facts():
    try:
        # Use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        traceback.print_exc()
        return None
        
    # Assign columns and set index of dataframe
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)

    # Convert the DataFrame back to html form
    return df.to_html(classes="table table-striped")


def hemispheres(browser):
    # Visit URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("a.itemLink h3", wait_time=1)

    #Create empty list to hold hemisphere dictionaries, holding url & title for each one
    hemisphere_urls_titles = []

    # list of hemispheres to loop through
    links = browser.find_by_css("a.itemLink h3")

    # Loop through each hemisphere, click, get title and large image url
    for i in range(len(links)):
        hemisphere = {}
        browser.find_by_css("a.itemLink h3")[i].click()
        # Get the url for image
        sample_img = browser.links.find_by_text('Sample')
        hemisphere['img_url'] = sample_img['href']
        # Get the Hemisphere title
        hemisphere['title'] = browser.find_by_css("h2.title").text
        # Append hemisphere object to list
        hemisphere_urls_titles.append(hemisphere)
        # Finally, we navigate backwards
        browser.back()
    
    hemisphere_titles = [element['title'] for element in hemisphere_urls_titles]
    hemisphere_urls = [element['img_url'] for element in hemisphere_urls_titles]

    cerberus_title = hemisphere_titles[0]
    schiaparelli_title = hemisphere_titles[1]
    syrtis_title = hemisphere_titles[2]
    valles_title = hemisphere_titles[3]

    cerberus_url = hemisphere_urls[0]
    schiaparelli_url = hemisphere_urls[1]
    syrtis_url = hemisphere_urls[2]
    valles_url = hemisphere_urls[3]

    return cerberus_title, schiaparelli_title, syrtis_title, valles_title, cerberus_url, schiaparelli_url, syrtis_url, valles_url


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())

