import os, sys
import logging
from datetime import datetime
import requests
from requests.compat import urljoin
import base64
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from twitter_client import TwitterClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)

load_dotenv()
HOST = 'http://127.0.0.1:7860'
RESOURCE = '/sdapi/v1/txt2img'
bearer = os.environ.get('TWITTER_BEARER_TOKEN')
consumer_api_key=os.environ.get('TWITTER_CONSUMER_KEY')
access_token=os.environ.get('TWITTER_ACCESS_TOKEN_KEY')
access_token_secret=os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
consumer_secret=os.environ.get('TWITTER_CONSUMER_SECRET')

SEASON = {
  1: "winter",
  2: "winter",
  3: "spring",
  4: "spring",
  5: "spring",
  6: "summer",
  7: "summer",
  8: "summer",
  9: "autumn",
  10: "autumn",
  11: "autumn",
  12: "winter",
}

TIME_FRAME = {
  0: "midnight",
  1: "night",
  2: "night",
  3: "night",
  4: "sunrise",
  5: "sunrise",
  6: "sunrise",
  7: "morning",
  8: "morning",
  9: "morning",
  10: "morning",
  11: "morning",
  12: "midday",
  13: "afternoon",
  14: "afternoon",
  15: "afternoon",
  16: "sunset",
  17: "sunset",
  18: "sunset",
  19: "night",
  20: "night",
  21: "night",
  22: "night",
  23: "night",
}

if __name__ == '__main__':
  request_url = urljoin(HOST, RESOURCE)
  logger.info('#### START')
  logger.info(f'request_url {request_url}')

  current_time = datetime.now()
  prompt = f"((masterpiece)), (((best quality))), ((ultra-detailed)), ((illustration)), a girl, 14 years old, perfect detailed face, perfect detailed drooping large glow eyes, perfect detailed above eyelashes, yellow eyebrow, (perfect detailed large blue pupils), perfect detailed nose, perfect detailed lips, perfect detailed mouth, (perfect detailed outside honeybob short cut yellow hair:1.3), neck, clavicle, bare shoulders, 2 arms, (perfect detailed (large hair white ribbon:1.2) attached headphone:1.3), (perfect intricate wearing a sailor collar white detached sleeve shirt and black short pants:1.3), (bangs hair clip:1.3), (wide shot:1.2),(dutch angle :1.3), ({SEASON[current_time.month]} {TIME_FRAME[current_time.hour]} sky:1.3)"
  logger.info(prompt)

  payload = {
    "enable_hr": "false",
    "denoising_strength": 0,
    "firstphase_width": 0,
    "firstphase_height": 0,
    "prompt": prompt,
    "styles": [
      "string"
    ],
    "seed": -1,
    "subseed": -1,
    "subseed_strength": 0,
    "seed_resize_from_h": -1,
    "seed_resize_from_w": -1,
    "batch_size": 1,
    "n_iter": 1,
    "steps": 28,
    "cfg_scale": 7,
    "width": 704,
    "height": 512,
    "restore_faces": "false",
    "tiling": "false",
    "negative_prompt": "nsfw, poorly drawn hands, poorly drawn face, weird, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digits, fewer digits, fat, (cropped), fused fingers, too many fingers, worth quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet, monochrome, bad body, bad proportions, bad face, merged leg",
    "eta": 0,
    "s_churn": 0,
    "s_tmax": 0,
    "s_tmin": 0,
    "s_noise": 1,
    "override_settings": {},
    "sampler_index": "Euler a"
  }

  response = requests.post(request_url, json=payload)
  if response:
    logger.info(f'text2image response.status_code {response.status_code}')
    if response.status_code == 200:
      base64image = response.json()['images'][0]
      if base64image:
        # with open('./output.txt', 'w') as f:
        #   f.write(base64image)
        with BytesIO(base64.b64decode(base64image)) as bio:
          img = Image.open(bio)
          file_path = './test.png'
          img.save(file_path)

          tc = TwitterClient(bearer, consumer_api_key, consumer_secret, access_token, access_token_secret)

          response = tc.tweet(f'{current_time.strftime("%Y/%m/%d %H:%M:%S")}', file_path)
          logger.info(f'Tweet Response {response}')
