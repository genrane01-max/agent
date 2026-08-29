from flask import Flask

app = Flask(__name__)

@app.route("/")
def dashboard():
    return "<h1>Bot Expert
Dashboard</h1><p>Status: Online</p>"

if __name__=="__main__":
    app.run(debug=True)

