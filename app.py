
from __future__ import print_function

import flask

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
import requests
import pandas

app = flask.Flask(__name__)


def getitem(obj, item, default):
	if item not in obj:
		return default
	else:
		return obj[item]


@app.route("/")
def plotstock():
	# Grab the inputs arguments from the URL
	args = flask.request.args

	# Get all the form arguments in the url with defaults
	stock = getitem(args, 'ticker', '')
	closing = int(getitem(args, 'close', 0))
	opening = int(getitem(args, 'open', 0))
	high = int(getitem(args, 'high', 0))
	low = int(getitem(args, 'low', 0))

	js_resources = INLINE.render_js()
	css_resources = INLINE.render_css()

	# Get stock info
	api_url = 'https://www.quandl.com/api/v1/datasets/WIKI/%s.json' % stock
	session = requests.Session()
	session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
	raw_data = session.get(api_url)
	raw_json = raw_data.json()
	if stock == "":
		html = flask.render_template(
			'index.html',
			plot_script="",
			plot_div="",
			js_resources=js_resources,
			css_resources=css_resources
		)
	elif 'error' in raw_json and raw_json['error'] == 'Unknown api route.':
		html = flask.render_template(
			'index.html',
			plot_script="",
			plot_div="",
			js_resources=js_resources,
			css_resources=css_resources
		)
	elif 'error' in raw_json and raw_json['error'] == 'Requested entity does not exist.':
		html = flask.render_template(
			'index.html',
			plot_script="",
			plot_div="Stock ticker not found, please try again.",
			js_resources=js_resources,
			css_resources=css_resources
		)
	else:
		df = pandas.DataFrame(raw_json['data'], columns=raw_json['column_names'])
		df = df.set_index(['Date'])
		df.index = pandas.to_datetime(df.index)
		name = raw_json['name']

		# Create Stock Chart
		p = figure(title=name, x_axis_type="datetime")
		if closing == 1:
			p.line(df.index, df['Close'], color='blue', legend='Closing Price')
		if opening == 1:
			p.line(df.index, df['Open'], color='green', legend='Opening Price')
		if high == 1:
			p.line(df.index, df['High'], color='red', legend='Highest Price')
		if low == 1:
			p.line(df.index, df['Low'], color='orange', legend='Lowest Price')

		script, div = components(p)
		html = flask.render_template(
			'index.html',
			plot_script=script,
			plot_div=div,
			js_resources=js_resources,
			css_resources=css_resources
		)
		return encode_utf8(html)


@app.route('/')
def main():
	return flask.redirect('/index')


@app.route('/index')
def index():
	return flask.render_template('index.html')


if __name__ == "__main__":
	print(__doc__)
	app.run()
