from flask import Flask, render_template, request, Response

app = Flask(__name__)

@app.route("/assignment_callback", methods=['POST'])
def assignment_callback():
    """Respond to assignment callbacks with empty 200 response"""

    resp = Response({}, status=200, mimetype='application/json')
    return resp
@app.route("/", methods=['GET', 'POST'])
def hello_world():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
