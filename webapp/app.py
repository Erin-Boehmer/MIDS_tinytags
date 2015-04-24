from flask import Flask, render_template, request, jsonify, make_response
import solr
import random
import StringIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

# create the application object
app = Flask(__name__)

# create a connection to the solr server
s = solr.SolrConnection('http://localhost:8983/solr/TinyImages_shard2_replica1')

# use decorators to link the function to a url
@app.route('/')
@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    # create the query string for tags
    tag_lookup = {
        "airplane":"0",
        "automobile":"1",
        "bird":"2",
        "cat":"3",
        "deer":"4",
        "dog":"5",
        "frog":"6",
        "horse":"7",
        "ship":"8",
        "truck":"9" }
    tag_str = ""
    for tag in request.json['tags']:
        if(tag_str == ""):
            tag_str = tag_lookup[str(tag)]
        else:
            tag_str = "%s OR %s" % (tag_str, tag_lookup[str(tag)])
    
    # create the query string for accuracy
    low_acc = int(request.json['accuracies'][0])/10
    high_acc = int(request.json['accuracies'][1])/10
    accuracy_str = 'num_tree_i:[%d TO %d]' % (low_acc, high_acc)
    
    # create the filter query and submit to solr
    fq_str = "label_i:(%s) AND %s" % (tag_str, accuracy_str)
    response = s.query('*:*', fq=fq_str)
    
    # create the image json response 
    data = {"images": []}
    for hit in response.results:
        image = {"data":hit['data'], "label_i":hit['label_i'], "num_tree_i":hit['num_tree_i']}
        data["images"].append(image)
    return(jsonify(data))

@app.route('/plot.png')
def plot():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
 
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
 
    axis.plot(xs, ys)
    canvas = FigureCanvas(fig)
    output = StringIO.StringIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

if __name__ == '__main__':
    app.run(debug=True)
