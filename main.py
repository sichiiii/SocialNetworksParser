from typing import final
import urllib
import requests, json, os
from bs4 import BeautifulSoup
from instaloader import Instaloader, Profile, load_structure_from_file
from app_logger import get_logger

L = Instaloader()
logger = get_logger(__name__)

try:
    with open("/home/jabka/python/SocialNetworksParserWithAddLinks/input.txt") as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]

    final_arr = []
except Exception as ex:
    logger.error(str(ex))

additional_links = ['', 'help', 'contact', 'contacts']

for i in lines:
    access = None
    for j in additional_links:
        try:
            if i[:-1] == '/':
                edited_link = i + j
            else:
                edited_link = i + '/' + j
            print(edited_link)
            if ('http:' in edited_link.split('/')) or ('https:' in edited_link.split('/')):
                r = requests.get(edited_link, timeout=(8, 10), verify=False)
                if r.status_code == 200:
                        access = True
            else:
                try:
                    r = requests.get('https://' + edited_link, timeout=(8, 10), verify=False)
                    if r.status_code == 200:
                        access = True
                except:
                    r = requests.get('http://' + edited_link, timeout=(8, 10), verify=False)
                    if r.status_code == 200:
                        access = True
            code = r.status_code
            sm_sites = ['instagram.com', 'youtube.com', 'twitter.com', 'facebook.com']
            sm_sites_present = {}
            sm_sites_present[edited_link] = []
            soup = BeautifulSoup(r.content, 'html5lib')
            
            all_links = soup.find_all('a', href = True)
            for sm_site in sm_sites:
                for link in all_links:
                    if sm_site in link.attrs['href']:
                        if link.attrs['href'] not in sm_sites_present[edited_link]: 
                            sm_sites_present[edited_link].append(link.attrs['href'])
                        
            final_arr.append(sm_sites_present)
        except Exception as ex: 
            print(str(ex))
        try:
            if access == True:
                f = open("/home/jabka/python/SocialNetworksParserWithAddLinks/output.txt","a")
                print(len(final_arr))
                f.write(str(sm_sites_present)[:-1]+", 'status_code' : '" + str(code) + "'" + ", 'followers' : [") 
                print(sm_sites_present[list(sm_sites_present.keys())[0]])
                inst_followers = None
                social = None
                for j in sm_sites_present[list(sm_sites_present.keys())[0]]:
                    try:
                        if ('www.instagram.com' in j.split('/')):
                            username_inst = j.split("https://www.instagram.com/",1)[1]
                            profile = Profile.from_username(L.context, username_inst[:-1])
                            inst_followers = profile.followers
                    except Exception as ex:
                        logger.error(str(ex))
                if inst_followers != None:
                    social = True
                    f.write("'instagram_followers' : '" + str(inst_followers) + "', ")

                youtube_followers = None 

                for j in sm_sites_present[list(sm_sites_present.keys())[0]]:
                    try:
                        if ('www.youtube.com' in j.split('/')):
                            username_youtube = j.split("https://www.youtube.com/",1)[1]
                            key = 'AIzaSyCk-2ZWAzbuuD2BRixR9Sp47h6zilrNDAI'
                            username_arr = username_youtube.split('/')
                            if 'channel' in username_arr:
                                data = urllib.request.urlopen('https://www.googleapis.com/youtube/v3/channels?part=statistics&id='+ username_arr[1] + '&key='+key).read()
                            else:
                                data = urllib.request.urlopen('https://www.googleapis.com/youtube/v3/channels?part=statistics&forUsername='+ username_arr[1] + '&key='+key).read()
                            subs = json.loads(data)['items'][0]['statistics']['subscriberCount']
                            youtube_followers = subs
                    except Exception as ex:
                        logger.error(str(ex))
                if youtube_followers != None:
                    print('yesy')
                    social = True
                    f.write("'youtube followers' : '" + str(youtube_followers) + "', ")

                twitter_followers = None
                for j in sm_sites_present[list(sm_sites_present.keys())[0]]:
                    try:
                        if ('twitter.com' in j.split('/')):
                            username_twitter = j.split("https://twitter.com/",1)[1]
                            r = requests.get("https://cdn.syndication.twimg.com/widgets/followbutton/info.json?screen_names=" +username_twitter).json()
                            twitter_followers = r[0]['followers_count']
                    except Exception as ex:
                        logger.error(str(ex))
                if twitter_followers != None:
                    print('yest')
                    social = True
                    f.write("'twitter_followers' : '" + str(twitter_followers) + "'")
                
                f.write("]}\n")
                f.close()
        except Exception as ex:
            logger.error(str(ex))
