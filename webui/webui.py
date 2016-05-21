from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
import os
import re
import pickle
import subprocess
app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/search/<search_term>')
def show_search(search_term):
    # show the user profile for that user
    return 'result for {}'.format(search_term)

@app.route('/new_search/<search_term>')
def show_news(search_term):
    process = subprocess.Popen(['grep', '-Rl', search_term, '/news'], stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    # import ipdb; ipdb.set_trace()

    results_html = ""
    for result in str(stdout).split("\\n"):
        results_html += "<tr><td>{}</td></tr>".format(result)
    return """<link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" rel="stylesheet"><div class="container"><h2>results</h2><table class="table"> <thead> <tr> <th>File</th> </tr> </thead> <tbody> """ + results_html + """</tbody></table></div>"""


def grep(path, needle):
    res = []
    for root, dirs, fnames in os.walk(path):
        for fname in fnames:
            fpath = os.path.join(root, fname)
            file_text = pickle.load(open(fpath))
            if needle in file_text:
                res.append(fpath)
    return res

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=443, debug=True)
