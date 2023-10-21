import sys
import os

sys.path.append("..")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enshit import download_and_play


def test_download_and_play():
    video_url = "https://www.youtube.com/watch?v=B_zWkHFGEiI"
    title = "Test Video"
    video = {"watched": False}

    download_and_play(video_url, title, video)
