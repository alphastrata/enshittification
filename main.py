from enshit import (
    get_youtube_service,
    get_subscribed_channels,
    offer_video_download,
    save_channels_to_json,
    Channel,
)
import os
import json


def main() -> None:
    youtube = get_youtube_service()

    if os.path.exists("enshittification.json"):
        with open("enshittification.json", "r") as file:
            channels_data = json.load(file)
            channels = [Channel.from_dict(data, youtube) for data in channels_data]
    else:
        channels = get_subscribed_channels(youtube)
        save_channels_to_json(channels)

    offer_video_download(channels)


if __name__ == "__main__":
    main()
