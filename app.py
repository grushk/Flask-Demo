from flask import Flask, render_template, request, redirect
import requests, pandas, simplejson
from bokeh.plotting import figure
from bokeh.embed import components


app = Flask(__name__)


@app.route('/')
def main():
	return redirect('/index')


@app.route('/index')
def index():
	return render_template('index.html')


@app.route('/index')
def plotchart():
	stock = request.form['ticker'].upper()
	closing = request.form['closing']
	opening = request.form['opening']
	high = request.form['high']
	low = request.form['low']

	api_url = 'https://www.quandl.com/api/v1/datasets/WIKI/%s.json' % stock
	session = requests.Session()
	session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
	raw_data = session.get(api_url)
	raw_df = pandas.DataFrame(raw_data.json())
	df = pandas.DataFrame(raw_df.ix['data', 'dataset'], columns=raw_df.ix['column_names', 'dataset'])
	df = df.set_index(['Date'])
	df.index = pandas.to_datetime(df.index)

	plot = figure(tools=TOOLS,
				title='Data from Quandle WIKI set',
				x_axis_label='date',
				x_axis_type='datetime')
	script, div = components(plot)
	return render_template('index.html', script=script, div=div)

if __name__ == '__main__':
	app.run(port=33507)
