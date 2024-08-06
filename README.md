# reddit video scraper
<div align="center">
  
![DescargarBot](https://www.descargarbot.com/v/download-github_reddit.png)
  
[![Reddit](https://img.shields.io/badge/on-descargarbot?logo=github&label=status&color=green
)](https://github.com/descargarbot/reddit-video-scraper/issues "Reddit")
</div>

<h2>dependencies</h2>
<code>Python 3.9+</code>
<code>requests</code>
<code>FFmpeg</code>
<br>
<br>
<h2>install dependencies</h2>
<ul>
<li><h3>requests</h3></li>
  <code>pip install requests</code><br>
  <code>pip install -U 'requests[socks]'</code>
  <br>
<li> <h3>FFmpeg </h3></li>
  <ul>
  <li> <h3> Linux </h3> </li>
  <code> sudo apt install ffmpeg </code>
  <li> <h3>MacOS</h3> </li>
    you can use this <a href="https://bbc.github.io/bbcat-orchestration-docs/installation-mac-manual/" > tutorial</a>
  <li> <h3>Windows</h3> </li>
    you can use this <a href="https://www.wikihow.com/Install-FFmpeg-on-Windows" > tutorial</a>
  </ul>
<br>
</ul>
<h2>use case example</h2>

    #import the class RedditVideoScraper
    from reddit_video_scraper import RedditVideoScraper
    
    # set reddit video url
    reddit_url = 'ur reddit video url'
    
    # create scraper video object
    reddit_video = RedditVideoScraper()

    # set the proxy (optional, u can run it with ur own ip)
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
    
<br>
<h2>online</h2>
<ul>
  ⤵
  <li> web 🤖 <a href="https://descargarbot.com" >  DescargarBot.com</a></li>
  <li> Telegram Bot 🤖 <a href="https://t.me/xDescargarBot" > DescargarBot</a></li>
</ul>
