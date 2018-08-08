from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def home():
	return "Hello world"

@app.route('/msrit',methods=['GET','POST'])
def index():
	if request.method == "GET":
		number = request.form['number']
	return "Fetched "+number

@app.route('/form')
def details():
	return render_template('form.html')

if __name__ == "__main__":
	app.run(port=8000,debug=True)

