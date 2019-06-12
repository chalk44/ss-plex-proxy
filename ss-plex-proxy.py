import argparse

from flask import Flask, redirect, request, jsonify
from pysmoothstreams import LIVE247, Feed, Server, Quality, Protocol
from pysmoothstreams.auth import AuthSign
from pysmoothstreams.guide import Guide

app = Flask(__name__)


@app.route('/channels/<int:channel_number>')
@app.route('/auto/v<int:channel_number>')
def get_channel(channel_number):
    url = guide.generate_streams(Server[server], Quality[quality], auth_sign, protocol=Protocol.MPEG)[channel_number - 1][
        'url']
    return redirect(url)


@app.route('/servers')
def list_servers():
    return jsonify({'servers': [e.name for e in Server]})


@app.route('/hdhomerun/discover.json')
def discover():
    data = {
        'FriendlyName': 'proxy',
        'Manufacturer': 'Silicondust',
        'ModelNumber': 'HDTC-2US',
        'FirmwareName': 'hdhomeruntc_atsc',
        'TunerCount': 6,
        'FirmwareVersion': '20150826',
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('service', help='service to build links for')

    parser.add_argument('-u', '--username', help='username to authenticate with')
    parser.add_argument('-p', '--password', help='password to authenticate with')
    parser.add_argument('-s', '--server', help='server to stream from')
    parser.add_argument('-q', '--quality', help='desired quality')
    args = parser.parse_args()

    if None not in (args.service, args.username, args.password):
        username = args.username
        password = args.password
        service = args.service

        server = args.server
        quality = args.quality


        # TODO: Make it work with other services
        auth_sign = AuthSign(service=LIVE247, auth=(username, password))
        guide = Guide(Feed.SMOOTHSTREAMS)

        app.run(host='0.0.0.0', port=5004)
