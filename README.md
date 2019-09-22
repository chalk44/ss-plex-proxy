# ss-plex-proxy
A small Flask app meant to be used together with Plex Live TV & DVR feature.
## Configure ss-plex-proxy
Copy `ss-plex-proxy.default_settings` to `ss-plex-proxy.custom_settings` and edit appropriately.
## Configure Plex Live TV & DVR
[Setup Plex TV & DVR](https://support.plex.tv/articles/225877347-live-tv-dvr/) and opt to manually enter a network address for a HDHomeRun device. Use `http://192.168.1.132:5004/hdhomerun/` and click through the wizard until you define an electronic guide. Click 'Have an XML guide on your server? Click here to use that instead' and use `http://192.168.1.132:5004/guide` as the path to the XMLTV Guide. Click through the rest of the wizard.
## Running manually
Install the necessary requirements with `pip install -r requirements.txt` and invoke via `python3 ss-plex-proxy.py`.
## Docker
Build the image with `docker build -t ss-plex-proxy:latest .` Run with `docker run -p 5004:5004 ss-plex-proxy`. 
