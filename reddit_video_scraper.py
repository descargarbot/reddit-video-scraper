import requests
import re
import os
import sys

##################################################################
class RedditVideoScraper:
    
    def __init__(self):
        """ Initialize """

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }

        self.proxies = {
            'http': '',
            'https': '',
        }

        self.reddit_session = requests.Session()

    
    def set_proxies(self, http_proxy: str, https_proxy: str) -> None:
        """ set proxy  """

        self.proxies['http'] = http_proxy 
        self.proxies['https'] = https_proxy


    def get_video_json_by_url(self, reddit_url: str) -> str:
        """ Get video info (json) """

        # If the url is a short url, get web url
        if 'v.redd.it' in reddit_url:
            try:
                reddit_url = self.reddit_session.get(reddit_url, headers=self.headers, proxies=self.proxies).url
            except Exception as e:
                print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
                raise SystemExit('error getting web url')            
        
        reddit_json_url = f'{reddit_url.split("?")[0]}.json'
        try:
            reddit_json_url = self.reddit_session.get(reddit_json_url, headers=self.headers, proxies=self.proxies).json()
        except Exception as e:
            print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
            raise SystemExit('error getting json info')   

        return reddit_json_url


    def reddit_video_details(self, reddit_video_info: str) -> tuple:
        """ Get video details
            video and audio urls """
            #TODO: analize the other json (gifs, multi, etc) 
        try:
            #if reddit_video_info[0]['data']['children'][0]['data']['is_reddit_media_domain'] == False:
            #    raise SystemExit('video not hosted in reedit')

            video_details = reddit_video_info[0]['data']['children'][0]['data']['secure_media']['reddit_video']
            post_url = reddit_video_info[0]['data']['children'][0]['data']['url']

            video_thumbnail = reddit_video_info[0]['data']['children'][0]['data']['thumbnail']
            video_nsfw = reddit_video_info[0]['data']['children'][0]['data']['over_18']
        except Exception as e:
            print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
            raise SystemExit('error getting video details')

        # video url
        video_url = video_details['fallback_url'].split('?')[0]
        is_gif = video_details['is_gif']

        # audio url
        # if the post contains a gif there is no audio
        audio_url = None
        if is_gif == False:

            dash_playlist_url = video_details['dash_url'].split('?')[0]
            try:
                dash_playlist = self.reddit_session.get(dash_playlist_url, headers=self.headers, proxies=self.proxies)
            except Exception as e:
                print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
                raise SystemExit('error getting audio details')

            search_audio = re.findall('<BaseURL>(.*?)</BaseURL>', dash_playlist.text, flags=re.DOTALL)
            audio_url = None

            for audio in search_audio:
                
                if 'audio' in audio.lower():
                    audio_url = f'{post_url}/{audio}' # in general last audio is the best
                  
                # if video is muted or not audio is found
                # let's treat it like a gif 
                is_gif = True if audio_url == None else False

        # if is a gif or a muted video 'audio_url' is None
        return {'video_url': video_url, 'audio_url': audio_url, 'is_gif' : is_gif}, video_thumbnail, video_nsfw

    
    def download(self, reddit_video_urls: dict) -> dict:
        """ download the video and audio files """

        # download video
        try:
            video = self.reddit_session.get(reddit_video_urls['video_url'], headers=self.headers, proxies=self.proxies, stream=True)
        except Exception as e:
            print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
            raise SystemExit('error downloading video')

        video_id = reddit_video_urls['video_url'].split('/')[-2]

        video_path_filename = f'video_{video_id}.mp4'
        try:
            with open(video_path_filename, 'wb') as f:
                for chunk in video.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
        except Exception as e:
            print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
            raise SystemExit('error writting video')

        # download audio
        audio_path_filename = None
        if reddit_video_urls['is_gif'] == False:
            try:
                audio = self.reddit_session.get(reddit_video_urls['audio_url'], headers=self.headers, proxies=self.proxies, stream=True)
            except Exception as e:
                print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
                raise SystemExit('error downloading audio')

            audio_path_filename = f'audio_{video_id}.mp4'
            try:
                with open(audio_path_filename, 'wb') as f:
                    for chunk in audio.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            f.flush()
            except Exception as e:
                print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
                raise SystemExit('error writting audio')

        return {'video_tmp': video_path_filename, 
                'audio_tmp': audio_path_filename, 
                'is_gif' : reddit_video_urls['is_gif'], 
                'video_id': video_id }


    def ffmpeg_mux(self, download_details: dict) -> list:
        """ perform mux
            join the video and audio file """

        video_tmp = download_details['video_tmp']
        audio_tmp = download_details['audio_tmp']
        video_id  = download_details['video_id']

        final_video_name = f'DescargarBot_{video_id}.mp4'

        if download_details['is_gif'] == False:
            ffmpeg_cmd = f'ffmpeg -hide_banner -loglevel panic -y -i "{video_tmp}" -i "{audio_tmp}" -vcodec copy -acodec copy "{final_video_name}"'
        else:
            ffmpeg_cmd = f'ffmpeg -hide_banner -loglevel panic -y -i "{video_tmp}" -vcodec copy "{final_video_name}"'

        try:
            # perform mux/fix
            os.system(ffmpeg_cmd)

            # delete tmp files
            os.system(f'rm {video_tmp}')
            if download_details['is_gif'] == False:
                os.system(f'rm {audio_tmp}')
            
        except Exception as e:
            print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
            raise SystemExit('error with ffmpeg')

        return [final_video_name]


    def get_video_filesize(self, video_url: str, audio_url: str) -> str:
        """ get file size of requested video """

        # get video filesize
        video_size = 0
        try:
            video_size = self.reddit_session.head(video_url, headers=self.headers, proxies=self.proxies)
        except Exception as e: 
            print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
            raise SystemExit('error getting video file size')

        video_size = int(video_size.headers['content-length'])

        # get audio filesize
        audio_size = 0
        if audio_url:
            try:
                audio_size = self.reddit_session.head(audio_url, headers=self.headers, proxies=self.proxies)
            except Exception as e: 
                print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
                raise SystemExit('error getting audio file size')

            audio_size = int(audio_size.headers['content-length'])

        return str(video_size + audio_size)       

###################################################################

if __name__ == "__main__":

    # use case example

    # set reddit video url
    reddit_url = 'your reddit video post'
    
    # create scraper video object
    reddit_video = RedditVideoScraper()

    # set the proxy (or not)
    #reddit_video.set_proxies('<your http proxy>', '<your https proxy')

    # get video info from url
    reddit_video_info = reddit_video.get_video_json_by_url(reddit_url)

    # get the video details
    reddit_video_urls, video_thumbnail, video_nsfw = reddit_video.reddit_video_details(reddit_video_info)

    # get the video filesize
    video_size = reddit_video.get_video_filesize(reddit_video_urls['video_url'], reddit_video_urls['audio_url'])
    print(f'filesize: ~{video_size} bytes')

    # download the video and audio
    download_details = reddit_video.download(reddit_video_urls)

    # join the video and audio
    # remember install ffmpeg if u dont have it
    downloaded_video_list = reddit_video.ffmpeg_mux(download_details)

    reddit_video.reddit_session.close()

