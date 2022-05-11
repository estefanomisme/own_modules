#!/usr/bin/python3

import sys
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from datetime import timedelta, datetime


api_key = 'AIzaSyBllRsmLKbzGky00Ih3IfBkDddGbDy60Vg'
youtube = build('youtube', 'v3', developerKey=api_key)

nextPageToken = None

playlistId = sys.argv[1].replace('https://www.youtube.com/playlist?list=', '')

playlist_videoIds = []

while True:
    request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlistId,
            maxResults=50,
            pageToken=nextPageToken
    )

    try:
        response = request.execute()
    except HttpError:
        sys.stderr.write('Not a valid url\n')
        sys.exit(1)

    for item in response['items']:
        videoId = item['contentDetails']['videoId']
        playlist_videoIds.append(videoId)

    nextPageToken = response.get('nextPageToken')

    if not nextPageToken:
        break

print('All videos of the playlist have been collected')

totalDuration = timedelta()

repeatedTitle = ''
for videoId in playlist_videoIds:
    vidRequest = youtube.videos().list(
            part='contentDetails, snippet',
            id=videoId
    )

    vidResponse = vidRequest.execute()

    if vidResponse['items'] == []:
        continue

    videoTitle = vidResponse['items'][0]['snippet']['title']
    if videoTitle == repeatedTitle:
        continue
    repeatedTitle = videoTitle
    videoDuration = vidResponse['items'][0]['contentDetails']['duration']

    ftimeList = ['PT%HH%MM%SS', 'PT%MM%SS', 'PT%SS', 'PT%MM', 'PT%HH',
                 'PTPT%HH%MM', 'PT%HH%SS']
    for ftime in ftimeList:
        try:
            videoDuration = datetime.strptime(videoDuration, ftime)
            break
        except:
            continue

    hours = videoDuration.hour
    minutes = videoDuration.minute
    seconds = videoDuration.second

    videoDuration = timedelta(hours=hours, minutes=minutes, seconds=seconds)

    totalDuration += videoDuration

    print(f'{videoTitle}: {videoDuration}')

print()

print('-------------------------------------------------------------------')

print()

print(f'Total duration of the playlist: {totalDuration}')
