#!/usr/bin/python

import os
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = os.environ['YOUTUBE_API_KEY']
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

class YoutubeAPI:

    def youtube_search(self, query):
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY)

        # Call the search.list method to retrieve results matching the specified
        # query term.
        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=25,
            videoEmbeddable='true',
            type='video',
        ).execute()

        search_results = search_response.get("items", [])
        videos = []

        # Add each result to the appropriate list, and then display the lists of
        # matching videos, channels, and playlists.
        for search_result in search_results:
            videos.append("%s (%s)" % (search_result["snippet"]["title"],
                search_result["id"]["videoId"]))

        # print("Videos:\n" + "\n".join(videos) + "\n")

        if videos:
            return search_result["id"]["videoId"]
        return None

if __name__ == "__main__":
    argparser.add_argument("--q", help="Search term", default="Google")
    argparser.add_argument("--max-results", help="Max results", default=25)
    args = argparser.parse_args()

    youtube = YoutubeAPI()
    try:
        url = youtube.youtube_search(args)
    except(HttpError, e):
        print("An HTTP error {:d} occurred:\n{}".format(e.resp.status, e.content))

    print(url)
