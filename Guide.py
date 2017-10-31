import json
import urllib.request
from enum import Enum

class Feed(Enum):
	SmoothStreams = 'https://guide.smoothstreams.tv/feed.json'
	Fog = 'http://sstv.fog.pt/feed5.json'


class Guide:
	def __init__(self, feed=Feed.SmoothStreams):
		self.channels = []
		self.expires = None

		self.url = feed.value
		self._parse_feed()

	def _parse_feed(self):
		with urllib.request.urlopen(self.url) as response:
			self.expires = response.info()['Expires']
			# print(self.expires)

			try:
				as_json = json.loads(response.read())
				self.channels = []

				for x in range(1, len(as_json) + 1):
					channel = as_json[str(x)]

					c = {'number': channel['channel_id'],
					     'name': channel['name'],
					     'icon': channel['img']}

					self.channels.append(c)


			except Exception as e:
				print(e.with_traceback())
