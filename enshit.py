from typing import List, Dict, Any
from pytube import YouTube
from termcolor import colored
import google_auth_oauthlib.flow
import googleapiclient.discovery
import json
import os
import subprocess
from datetime import datetime, timedelta

MAX_VID_AGE = timedelta(weeks=2)
MAX_VIDS_TO_PULL = 1
MIN_RES = "1080p"


class Channel:
    def __init__(self, title: str, channel_id: str, youtube) -> None:
        self.title = title
        self.channel_id = channel_id
        self.videos = self.get_recent_videos(youtube)

    def get_recent_videos(self, youtube) -> List[Dict[str, Any]]:
        request = youtube.search().list(
            part="snippet",
            channelId=self.channel_id,
            maxResults=MAX_VIDS_TO_PULL,
            order="date",
            type="video",
        )
        response = request.execute()
        current_date = datetime.utcnow()
        videos = [
            {
                "title": item["snippet"]["title"],
                "videoId": item["id"]["videoId"],
                "publishedAt": item["snippet"]["publishedAt"],
                "watched": False,
            }
            for item in response.get("items", [])
            if current_date
            - datetime.strptime(item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
            <= MAX_VID_AGE
        ]

        return videos

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "channelId": self.channel_id,
            "videos": self.videos,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], youtube) -> "Channel":
        channel = cls(data["title"], data["channelId"], youtube)
        channel.videos = data["videos"]
        return channel


def get_youtube_service():
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "client_secret.json", scopes
    )
    credentials = flow.run_local_server()
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    return youtube


def get_subscribed_channels(youtube):
    channels = []
    request = youtube.subscriptions().list(
        part="snippet,contentDetails",
        mine=True,
        maxResults=5000,  # This is the maximum allowed value
    )

    print(request.json())

    while request is not None:
        response = request.execute()
        channels.extend(
            [
                Channel(
                    item["snippet"]["title"],
                    item["snippet"]["resourceId"]["channelId"],
                    youtube,
                )
                for item in response.get("items", [])
            ]
        )

        # Get the next page token
        request = youtube.subscriptions().list_next(request, response)

    return channels


def save_channels_to_json(channels: List[Channel]) -> None:
    channels_data = [channel.to_dict() for channel in channels]
    with open("enshittification.json", "w") as file:
        json.dump(channels_data, file, indent=4)


def download_and_play(video_url: str, title: str, video: Dict[str, Any]) -> None:
    yt = YouTube(video_url)
    video_stream = (
        yt.streams.filter(file_extension="mp4", res=MIN_RES).first()
        or yt.streams.filter(file_extension="mp4").get_highest_resolution()
    )

    if video_stream:
        audio_stream = yt.streams.filter(only_audio=True).first()
        if audio_stream:
            print(f"Downloading {title}...")
            video_filename = video_stream.download(filename="video", skip_existing=True)
            audio_filename = audio_stream.download(filename="audio", skip_existing=True)
            final_filename = f"{title}.mp4"

            print("Merging video and audio...")
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    video_filename,
                    "-i",
                    audio_filename,
                    "-c",
                    "copy",
                    final_filename,
                ]
            )

            print(f"Playing {title} with VLC...")
            subprocess.run(["vlc", final_filename])
            video["watched"] = True
        else:
            print(colored("Audio stream not found", "red"))
    else:
        print(colored("Video unavailable in sufficiently high quality", "red"))


def offer_video_download(channels: List[Channel]) -> None:
    os.system("clear" if os.name == "posix" else "cls")  # Clear terminal

    for channel in channels:
        print(f"Channel: {channel.title}")
        for video in channel.videos:
            if video["watched"]:
                continue

            title = video["title"]
            video_url = f"https://www.youtube.com/watch?v={video['videoId']}"
            choice = input(
                f"Do you want to download and play '{title}'? (yes/no/next): "
            ).lower()

            if choice == "yes":
                download_and_play(video_url, title, video)
                save_channels_to_json(channels)  # Update JSON after watching a video
            elif choice == "no":
                continue
            elif choice == "next":
                break
            else:
                print("Invalid option. Please enter 'yes', 'no', or 'next'.")
