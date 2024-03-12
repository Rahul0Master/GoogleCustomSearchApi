from flask import Flask, render_template, request
import requests
import gspread
from google.oauth2 import service_account

app = Flask(__name__)


# Google Custom Search API key, search engine ID, spreadsheet ID, and credentials file
API_KEY = "AIzaSyCdMd_0QvOpHkb7YgeHSkI6lDxnrtkS2hI"
SEARCH_ENGINE_ID = "b1bfff91dfbd64555"
SPREADSHEET_ID = "1WsQVo5tP7Jgzt04smcu-DB5HpPXGM5t17Zi6cB-rjO8"
CREDENTIALS_FILE = "credentials.json"


# Load Google Sheets credentials from the credentials file
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets'])



"""
    Get search results from the Google Custom Search API.

    Parameters:
    - country_code (str): Country code for country-specific search.
    - search_query (str): The query to search for.

    Returns:
    - List of dictionaries containing search results.
"""

def get_search_results(country_code, search_query):
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'q': search_query,
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'cr': country_code,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        results = response.json().get('items', [])
        return [{'rank': index + 1, 'link': item.get('link', ''), 'title': item.get('title', '')} for index, item in enumerate(results)]
    else:
        return None



"""
    Write search results to a Google Sheets spreadsheet.

    Parameters:
    - results (list): List of dictionaries containing search results.
"""

def write_to_google_sheets(results):
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(SPREADSHEET_ID)
    worksheet = sh.get_worksheet(0)

    #worksheet.clear()

    
    header_row = ["Rank", "Link", "Title"]
    worksheet.append_row(header_row)

    
    for result in results:
        row_data = [result['rank'], result['link'], result['title']]
        worksheet.append_row(row_data)

    #worksheet.clear()


"""
    Main route for the web application.

    Handles both GET and POST requests.
    If the form is submitted, it retrieves search results and displays them.

    Returns:
    - Rendered HTML template with search results.
"""
@app.route('/', methods=['GET', 'POST'])
def index():

    default_country_code = 'countryIN'
    if request.method == 'POST':
        country_code = request.form.get('country_code', default_country_code)
        search_query = request.form['search_query']

        results = get_search_results(country_code, search_query)

        if results:
            write_to_google_sheets(results)           

        return render_template('index.html', results=results)

    return render_template('index.html', results=None)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')