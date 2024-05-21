import requests
from bs4 import BeautifulSoup # type: ignore
import re
import subprocess
import shlex
from config import Config
import json

def fetch_news_links():
    response = requests.get(Config.NEWS_URL)

    if response.status_code != 200:
        return "Error: Unable to fetch the webpage."

    soup = BeautifulSoup(response.text, 'html.parser')

    news_container = soup.find('div', class_=Config.NEWS_CONTAINER_CLASS)
    if not news_container:
        return "Error: News container not found."

    news_links = []
    news_items = news_container.find_all('div', class_=Config.NEWS_ITEM_CLASS)
    for item in news_items:
        link_container = item.find('div', class_=Config.LINK_CONTAINER_CLASS)
        if link_container:
            a_tag = link_container.find('a')
            if a_tag and a_tag.has_attr('href'):
                news_links.append({
                    'text': a_tag.text,
                    'url': a_tag['href']
                })

    return news_links

def convert_to_markdown(element):
    if element.name == 'p':
        return f"{element.text}\n"
    elif element.name == 'a':
        return f"[{element.text}]({element['href']})"
    elif element.name == 'figure':
        twitter_link = element.find('a', href=re.compile(r'https?://twitter\.com'))
        if twitter_link:
            return f"[Tweet]({twitter_link['href']})\n"
        caption = element.find('figcaption')
        if caption:
            return f"![]({element.find('img')['src']})\n*{caption.text}*\n"
    return ""

def fetch_new_item(url):
    print('fetch_new_item()')
    cookie = Config.COOKIE

    curl_command = f"""
    curl '{url}' \
        -H 'Cookie: {cookie}'
    """

    args = shlex.split(curl_command)
    process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = process.stdout
    errors = process.stderr

    if process.returncode == 0:
        soup = BeautifulSoup(output, 'html.parser')
        title_element = soup.find('h1', class_='sc-4984dd93-0 cECJcb')
        title = title_element.get_text(strip=True) if title_element else "No title found"
        image_element = soup.find('img', class_='coverImage')
        image_url = image_element['src'] if image_element else "No image found"
        script_tag = soup.find('script', {'id': '__NEXT_DATA__'})

        if script_tag:
            json_data = script_tag.string.strip()
            data_dict = json.loads(json_data)
            article_content = data_dict['props']['pageProps']['article']['content']
        else:
            article_content = "No JSON data found"
        soup = BeautifulSoup(article_content, 'html.parser')

        content = ""
        for child in soup.find_all(['p', 'a', 'figure']):
            content += convert_to_markdown(child)

        return {'title': title, 'image_url': image_url, 'content': content}
    else:
        print("CURL Failed:")
        print(errors)
        return {'error': 'Failed to fetch the webpage'}
