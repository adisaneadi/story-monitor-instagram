from instagrapi import Client
from instagrapi.types import StoryMention, StoryMedia, StoryLink, StoryHashtag
import json
import datetime
import requests
import time
import pytesseract as ocr
from PIL import Image
import io
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


cl = Client()
cl.login(os.environ['LOGIN_USER'], os.environ['PASSWORD'])

USERS = ["adityasanehi","vegnonveg","rise.camp.in","superkicks"]

i = 0

storiesList = []
for userno in USERS:
    storiesList.append([])
    
while True:
    print(f'[COUNTER] Cycle #{i}')
    j = 0
    for userStory in USERS:
        print(f' [CHECKING USER] - {userStory} - User #{j+1}')
        userID = cl.user_id_from_username(userStory)
        print(f'    [CHECKING USER] USER ID - {userID}')
        storiesScrape = cl.user_stories(userID) 
        userProfilePic = storiesScrape[-1].user.profile_pic_url
        storyID = storiesScrape[-1].pk
        print(f'    [CHECK] LAST STORY ID - {storyID}')
        newStory = storiesScrape[-1].thumbnail_url
        storiesList[j].append(storyID)
        if i!=0:
            if storiesList[j][i]!=storiesList[j][i-1]:
                responseImage = requests.get(newStory)

                imgRaw = Image.open(io.BytesIO(responseImage.content))

                ocrImage = ocr.image_to_string(imgRaw)

                data = {}
                data["username"] = "Instagram [Stories]"
                data["avatar_url"] = "https://i.imgur.com/NeJAV1h.jpg"
                data["embeds"] = []
                embed = {}
                embed["title"] = f'**NEW STORY** - @{userStory}'  # Item Name
                embed['url'] = f'https://www.instagram.com/{userStory}'  # Item link
                embed["image"] = {'url': newStory}  # Item image
                if storiesScrape[-1].mentions!=[]:

                    mentionsInStory = []
                    for mentionsStory in storiesScrape[-1].mentions:
                        print(mentionsStory.user.username)
                        mentionsInStory.append(f'[{mentionsStory.user.username}](https://www.instagram.com/{mentionsStory.user.username})')

                    embed["fields"] = [{'name':'Mentions:', 'value':f'{mentionsInStory}','inline':False}]
                embed["author"]= {'name': f'{userStory}','url': f'https://www.instagram.com/{userStory}', 'icon_url': f'{userProfilePic}'}
                embed["color"] = 1752220
                embed["footer"] = {'text': 'Instagram Stories | HeavyDrop Profits', 'icon_url':'https://i.imgur.com/NeJAV1h.jpg'}
                embed["timestamp"] = str(datetime.datetime.utcnow())
                data["embeds"].append(embed)

                result = requests.post(os.environ['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

                data1 = {}
                data1["username"] = "Instagram [Stories]"
                data1["avatar_url"] = "https://i.imgur.com/NeJAV1h.jpg"
                data1["embeds"] = []
                embed1 = {}
                embed1["title"] = f'**IMAGE OCR** - [{storyID}]'  # Item Name
                embed1['url'] = f'https://www.instagram.com/{userStory}'  # Item link
                embed1["fields"] = [{'name':'OCR Processed Text', 'value':f'{ocrImage.strip()}','inline':False}]
                embed1["author"]= {'name': f'{userStory}','url': f'https://www.instagram.com/{userStory}', 'icon_url': f'{userProfilePic}'}
                embed1["color"] = 1752220
                embed1["footer"] = {'text': 'Instagram Stories | HeavyDrop Profits', 'icon_url':'https://i.imgur.com/NeJAV1h.jpg'}
                embed1["timestamp"] = str(datetime.datetime.utcnow())
                data1["embeds"].append(embed1)

                result = requests.post(os.environ['WEBHOOK'], data=json.dumps(data1), headers={"Content-Type": "application/json"})
                print('    [EVENT] CHANGE DETECTED, WEBHOOK SENT!')
            else:
                print('    [EXCEPTION] LAST STORY ID IS THE SAME!')
        else:
            print(f'    [EVENT] MONITOR INITIATED FOR USER - @{userStory}!')
        j = j+1
        time.sleep(5)
    i = i+1       
    time.sleep(20)
