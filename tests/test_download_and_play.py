# Sample tests, override these with your own
# run tests with py.test
# preface test files with test_***.py (same convention as go.)
# if assert doesn't float your boat try hypothesis https://docs.python-guide.org/writing/tests/#hypothesis

import sys
import subprocess
from pytube import YouTube
from typing import Dict, Any
from termcolor import colored
import os

sys.path.append("..")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enshit import download_and_play


MIN_RES = "1080p"


def test_download_and_play():
    video_url = "https://www.youtube.com/watch?v=B_zWkHFGEiI"
    title = "Test Video"
    video = {"watched": False}

    download_and_play(video_url, title, video)
