import io
import logging
import os
import xml.etree.ElementTree as ET

from flask import Flask, redirect, request, jsonify, Response
from flask.logging import default_handler
from pysmoothstreams import Server, Protocol, Service
from pysmoothstreams.auth import AuthSign
from pysmoothstreams.exceptions import InvalidService
from pysmoothstreams.guide import Guide

app = Flask(__name__, static_url_path='', static_folder='static')
app.config.from_pyfile('ss-plex-proxy.default_settings')
app.config.from_pyfile('ss-plex-proxy.custom_settings')


def setup_logging():
    logging.basicConfig(level=logging.DEBUG)

    for logger in (
            app.logger,
            logging.getLogger('pysmoothstreams')
    ):
        logger.propagate = False
        logger.addHandler(default_handler)


@app.route('/channels/<int:channel_number>')
@app.route('/auto/v<int:channel_number>')
def get_channel(channel_number):
    url = guide.build_stream_url(Server[server], channel_number, auth_sign, protocol=Protocol.MPEG)
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
        channels.append({'GuideNumber': str(stream['number']),
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


# We are adding the xml_declaration as some programs (Kodi) require this.
#
# ET.tostring() does not support xml_declaration in Python versions < 3.8 so
# we need to write to a bytes object and return that in order to maintain
# backwards compatibility.
def add_xml_declaration(xml):
    f = io.BytesIO()
    t = ET.ElementTree(xml)
    t.write(f, encoding='utf-8', xml_declaration=True)
    return f.getvalue()


# Used to add a 'lcn' subelement to channel elements as Plex does something
# weird where it concatenates the channel id and channel name to make the
# channel number. For fog/altepg this is needed for sane channel numbers.
# https://forums.plex.tv/t/xmltv-parsing-channel-id-and-display-name/219305/20
def add_lcn_element(xmltv):
    channel_number = 1

    tree = ET.fromstring(xmltv)
    for element in tree.iter():
        if element.tag == 'channel':
            lcn = ET.SubElement(element, 'lcn')
            lcn.text = str(channel_number)
            channel_number += 1

    return add_xml_declaration(tree)


@app.route('/guide')
def guide_data():
    guide._fetch_epg_data()
    epg_data = add_lcn_element(guide.epg_data)
    if app.config['NANOF_LOGOS']: epg_data = replace_logos(epg_data)
    return Response(epg_data.decode(), mimetype='text/xml')


def replace_logos(xmltv):
    tree = ET.fromstring(xmltv)
    for element in tree.iter():
        if element.tag == 'channel':
            channel_name = element.find('display-name').text
            logo_path = 'static/logos/' + channel_name + '.png'

            if os.path.isfile(logo_path):
                element.find('icon').attrib['src'] = request.url_root + 'logos/' + channel_name + '.png'

    return add_xml_declaration(tree)


@app.route('/playlist.m3u')
def generate_m3u_playlist():
    m3u = '#EXTM3U\n'

    for channel in guide.channels:
        clean_channel_name = channel["name"].strip()

        m3u += '#EXTINF: tvg-id="{channel_id}" tvg-name="{channel_name}" tvg-logo="{channel_icon}" tvg-chno="{channel_number}", {channel_name}\n'.format(channel_id=channel["id"],channel_name=clean_channel_name,channel_icon=channel["icon"],channel_number=channel["number"])
        m3u += '{url_root}channels/{channel_number}\n'.format(url_root=request.url_root,channel_number=str(channel["number"]))

    return Response(m3u, mimetype='audio/x-mpegurl')


if __name__ == '__main__':
    setup_logging()

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
    guide = Guide(feed="https://fast-guide.smoothstreams.tv/altepg/xmltv3.xml.gz")

    app.run(host='0.0.0.0', port=5004)
