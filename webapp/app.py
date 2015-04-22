# import the Flask class from the flask module
from flask import Flask, render_template, request, jsonify

# create the application object
app = Flask(__name__)

# use decorators to link the function to a url
@app.route('/')
@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    query = ""
    print request.json["accuracies"]
    print request.json["tags"]
    return(jsonify(request.json))

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
