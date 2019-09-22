from flask import Flask, redirect, request, jsonify, Response

from altepg import altepg
from pysmoothstreams import Feed, Server, Quality, Protocol, Service
from pysmoothstreams.auth import AuthSign
from pysmoothstreams.exceptions import InvalidService
from pysmoothstreams.guide import Guide

app = Flask(__name__)
app.config.from_pyfile('ss-plex-proxy.default_settings')
app.config.from_pyfile('ss-plex-proxy.custom_settings')


@app.route('/channels/<int:channel_number>')
@app.route('/auto/v<int:channel_number>')
def get_channel(channel_number):
	url = \
	guide.generate_streams(Server[server], Quality[quality], auth_sign, protocol=Protocol.MPEG)[channel_number - 1][
		'url']
	return redirect(url)


@app.route('/servers')
def list_servers():
	return jsonify({'servers': [e.name for e in Server]})


@app.route('/hdhomerun/discover.json')
def discover():
	data = {
		'FriendlyName': 'ss-plex-proxy',
		'Manufacturer': 'Silicondust',
		'ModelNumber': 'HDTC-2US',
		'FirmwareName': 'hdhomeruntc_atsc',
		'TunerCount': 6,
		'FirmwareVersion': '201906217',
		'DeviceID': 'xyz',
		'DeviceAuth': 'xyz',
		'BaseURL': request.url_root + 'hdhomerun',
		'LineupURL': request.url_root + 'hdhomerun/lineup.json'
	}
	return jsonify(data)


@app.route('/hdhomerun/lineup.json')
def lineup():
	channels = []

	for stream in guide.channels:
		channels.append({'GuideNumber': stream['number'],
		                 'GuideName': stream['name'],
		                 'url': request.url_root + "channels/" + str(stream['number'])})

	return jsonify(channels)


@app.route('/hdhomerun/lineup_status.json')
def lineup_status():
	return jsonify({
		'ScanInProgress': 0,
		'ScanPossible': 1,
		'Source': "Cable",
		'SourceList': ['Cable']
	})


@app.route('/guide')
def guide_data():

	if guide.url == Feed.ALTEPG.value:
		return altepg(guide.epg_data)

	return Response(guide.epg_data, mimetype='text/xml')


if __name__ == '__main__':
	if app.config['SERVICE'] == "live247":
		service = Service.LIVE247
	elif app.config['SERVICE'] == "starstreams":
		service = Service.STARSTREAMS
	elif app.config['SERVICE'] == "streamtvnow":
		service = Service.STREAMTVNOW
	elif app.config['SERVICE'] == "mmatv":
		service = Service.MMATV
	else:
		raise InvalidService

	username = app.config['USERNAME']
	password = app.config['PASSWORD']
	server = app.config['SERVER']
	quality = app.config['QUALITY']

	auth_sign = AuthSign(service=service, auth=(username, password))
	guide = Guide()

	app.run(host='0.0.0.0', port=5004)
