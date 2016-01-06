from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/search/<search_term>')
def show_user_profile(search_term):
    # show the user profile for that user
    return 'result for {}'.format(search_term)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
