from flask import Flask, url_for

app = Flask(__name__)

@app.route('/blaat/<number>')
def hello_world(number):
    return str(float(number)**2)

if __name__ == '__main__':
    app.run()

