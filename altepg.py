import urllib.request
import xml.etree.ElementTree as ET


def altepg():
	xml = urllib.request.urlopen('https://fast-guide.smoothstreams.tv/altepg/xmltv1.xml').read().decode('utf-8')
	rewritten_epg = rewrite_channel_ids(xml)
	return rewritten_epg


def get_channel_numbers_from_ids(xmltv):
	tree = ET.fromstring(xmltv)
	mappings = []

	for element in tree.iter():
		mapping = {}
		if element.tag == 'channel':
			mapping['channel_id'] = element.attrib['id']

			for child in element.iter('display-name'):
				if child.text[0].isdigit():
					mapping['channel_number'] = child.text.split(' ')[0]

			mappings.append(mapping)

	return mappings


def rewrite_channel_ids(epg_data):
	mappings = get_channel_numbers_from_ids(epg_data)

	for mapping in mappings:
		epg_data = epg_data.replace(mapping['channel_id'], mapping['channel_number'])

	return epg_data
