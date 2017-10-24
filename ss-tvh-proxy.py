import argparse

from flask import Flask, redirect, request

from AuthSign import AuthSign

VALID_SITES = ['viewms', 'view247', 'viewss', 'viewmmasr', 'viewstvn']
VALID_SERVERS = ['dAP', 'deu', 'deu.nl', 'deu.uk', 'deu.uk1', 'deu.uk2', 'deu.nl1', 'deu.nl2', 'deu.nl3',
                 'dna', 'dnae', 'dnaw', 'dnae1', 'dnae2', 'dnae3', 'dnae4', 'dnaw1', 'dnaw2']

app = Flask(__name__)


@app.route('/channels/<channel_number>')
def get_channel(channel_number):
	server = request.args.get('server')
	quality = request.args.get('quality')

	if server is None:
		return 'You must specify a server.'
	if quality is None:
		quality = 1

	channel_url = build_url(channel_number, quality, server)
	return redirect(channel_url)


@app.route('/servers')
def list_servers():
	servers = """# Servers               
#
# Asia/Oceania        Europe                     North America
# 
# 'dAP' -> All        'deu' -> Server Mix       'dna' -> US/CA Mix
#                     'deu.nl' -> NL Mix        'dnae' -> US/CA East Mix
#                     'deu.uk' -> UK Mix        'dnaw' -> US/CA West Mix
#                     'deu.uk1' -> UK1 (io)     'dnae1' -> US/CA East 1 (NJ)
#                     'deu.uk2' -> UK2 (100TB)  'dnae2' -> US/CA East 2 (VA)
#                     'deu.nl1' -> NL1 (i3d)    'dnae3' -> US/CA East 3 (MTL)
#                     'deu.nl2' -> NL2 (i3d)    'dnae4' -> US/CA East 4 (TOR)
#                     'deu.nl3' -> NL3 (Ams)    'dnaw1' -> US/CA West 1 (PHZ)
#                                               'dnaw2' -> US/CA West 2 (SJ)"""
	return servers


@app.route('/sites')
def list_sites():
	sites = """# Services
#
# MyStreams.tv: service = 'viewms'
# Live247.tv: service = 'view247'
# StarStreams: service = 'viewss'
# MMA SR+:  service = 'viewmmasr'
# StreamTVnow = 'viewstvn'"""
	return sites


def build_url(channel_number, quality, server):
	auth_sign.fetch_hash()

	url = f'https://{server}.smoothstreams.tv/{site}/ch{channel_number.zfill(2)}q{quality}.stream/playlist.m3u8?wmsAuthSign={auth_sign.hash}'
	app.logger.debug(f'Built {url}')
	return url


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('site', help='site to build links for')
	parser.add_argument('-u', '--username', help='username to authenticate with')
	parser.add_argument('-p', '--password', help='password to authenticate with')
	args = parser.parse_args()

	if None not in (args.site, args.username, args.password):
		username = args.username
		password = args.password
		site = args.site

		auth_sign = AuthSign(site=site, auth=(username, password))

		app.run()
