import ast
import json
import time
import threading
from nltk.stem import PorterStemmer
from flask import Flask, request, render_template

app = Flask(__name__)

def get_postings(token):
    ''' takes a token, and will try to find that token's inverted index postings in the index_postings file '''
    ''' we open a new fp everytime because seek(0,0) may not be thread friendly '''
  
    d = open('index_postings.txt','r') 
    try:
        for k_index in range(ip_loc[token]):
            line = d.readline()
        k = ast.literal_eval(line)
        values[token] = k
    except:
        pass
    d.close()

def create_threads(query_list):
    ''' Creates threads for each individual token in the query '''
    threads = []
    for query in query_list:
        threads.append(threading.Thread(target=get_postings,args=(query,)))
    return threads

def _list_doc_ids(postings: list):
    ''' Get doc_ids [x,x2,...] from posting list [[x,y],[x2,y2],...] '''
    doc_ids = []
    for posting in postings:
        doc_ids.append(posting[0])
    return doc_ids


def show_urls():
    ''' Prints the top 5 urls from the search (AND only) '''
    global values, doc_ids

    postings = []
    # --- Get all posting lists for each token. Store in postings list --- #
    for token in values:
        L = sorted(values[token], key=lambda item: item[1], reverse=True) # Sort postings by term frequency
        postings.append(_list_doc_ids(L))
        
    try:
        # --- AND documents that query tokens appear in --- #
        intersected = postings[0]
        if (len(postings) > 1):
            for posting in postings[1:]:
                intersected = set(intersected).intersection(posting)
        result_list = list(intersected)[:5]
        # --- Print urls --- #
        if len(result_list) == 0:
            return None
        else:
            result = []
            for item in result_list:
                result.append(doc_ids[str(item)])
            return result

    except IndexError:
        # --- If no URLs from retrieval and/or intersection --- #
        return None

def _render_response(result: list):
    ''' Formats top 5 urls for page render '''

    # --- Format the urls as html list --- #
    if result == None:
        html_result = "<h3>No search results found</h3>"
    else:
        html_result = '<div><ol class="results">'
        for i in range(len(result)):
            html_result += '<li><a href={}>{}</a></li>'.format(result[i], result[i])
        html_result += '</ol></div>'

    # --- Unlike React, rewrite html template itself LOL --- # (index.html includes results.html)
    result_file = open('templates/results.html','w')
    result_file.write(html_result)
    result_file.close()

@app.route('/')
def main():
    result_file = open('templates/results.html','w')
    result_file.write('')
    result_file.close()
    return render_template('index.html')

@app.route('/', methods=['POST'])
def run_search():
    #search_query = input("Search for: ").lower()
    user_query = request.form['search']
    search_query = user_query.lower()
    search_query = search_query.split()
    search_query = [ps.stem(item) for item in search_query]
    values.clear()
    start = time.time()

    threads = create_threads(search_query)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
        
    _render_response(show_urls())
    runtime = (time.time() - start) * 1000
    timestamp = 'Retrieved in {} ms.'.format(runtime)

    return render_template('index.html', query=user_query, time=timestamp)
    # values will hold our data

if __name__ == '__main__':
    f = open('index_posting_location.txt','r')                        
    ip_loc = json.load(f)        # load the index of tokens mapped to the file's line; so we dont load the entire index into memory
    values = {}
    f.close()
    ps = PorterStemmer()
    doc_ids_file = open('doc-ids.txt','r')
    doc_ids = json.load(doc_ids_file)
    doc_ids_file.close()

    app.run(debug=True)