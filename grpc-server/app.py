from flask import Flask, request, jsonify # type: ignore
from utilities import fetch_news_links, fetch_new_item

app = Flask(__name__)

@app.route('/fetch-news', methods=['GET'])
def fetch_news():
    result = fetch_news_links()
    if isinstance(result, list):
        return jsonify(result)
    else:
        return jsonify({'error': result}), 500

@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing URL parameter'}), 400
    result = fetch_new_item(url)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
