from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import json
import re
import shlex
import subprocess

load_dotenv()
app = Flask(__name__)

@app.route('/fetch-news', methods=['GET'])
def fetch_news():
    url = 'https://coinmarketcap.com/headlines/news/'
    newsContainerClass = 'infinite-scroll-component'
    newsItemClass = 'sc-aef7b723-0 sc-b1d35755-0 cGYUCj'
    linkContainerClass = 'sc-aef7b723-0 coCmGz'

    def fetch_news_links(url):
        response = requests.get(url)

        if response.status_code != 200:
            return "Error: Unable to fetch the webpage."

        soup = BeautifulSoup(response.text, 'html.parser')

        news_container = soup.find('div', class_=newsContainerClass)
        if not news_container:
            return "Error: News container not found."

        news_links = []
        news_items = news_container.find_all('div', class_=newsItemClass)
        for item in news_items:
            link_container = item.find('div', class_=linkContainerClass)
            if link_container:
                a_tag = link_container.find('a')
                if a_tag and a_tag.has_attr('href'):
                    news_links.append({
                        'text': a_tag.text,
                        'url': a_tag['href']
                    })

        return news_links

    result = fetch_news_links(url)
    if isinstance(result, list):
        return jsonify(result)
    else:
        return jsonify({'error': result}), 500

@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing URL parameter'}), 400

    cookie = os.getenv('COOKIE')

    curl_command = f"""
    curl '{url}' \
        -H '{cookie}' \
    """

    args = shlex.split(curl_command)
    process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = process.stdout
    print('process = ', process)
    errors = process.stderr

    if process.returncode == 0:
        soup = BeautifulSoup(output, 'html.parser')
        print(soup)
        title_element = soup.find('h1', class_='sc-4984dd93-0 cECJcb')
        title = title_element.get_text(strip=True) if title_element else "No title found"
        print(title)
        image_element = soup.find('img', class_='coverImage')
        image_url = image_element['src'] if image_element else "No image found"
        print(image_url)
        script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
        print(script_tag)

        if script_tag:
            json_data = script_tag.string.strip()
            data_dict = json.loads(json_data)
            article_content = data_dict['props']['pageProps']['article']['content']
        else:
            article_content = "No JSON data found"
        soup = BeautifulSoup(article_content, 'html.parser')

        markdown_output = ""
        for child in soup.find_all(['p', 'a', 'figure']):
            markdown_output += convert_to_markdown(child)

        return jsonify({'title': title, 'image_url': image_url, 'markdown_output': markdown_output})
    else:
        print("CURL Failed:")
        print(errors)
        return jsonify({'error': 'Failed to fetch the webpage'}), 500

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

if __name__ == '__main__':
    app.run(debug=True)
