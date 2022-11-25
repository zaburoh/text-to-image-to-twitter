import os, sys, logging
import requests
from requests_oauthlib import OAuth1Session

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s][%(filename)s] %(message)s'))
handler.flush()
logger.addHandler(handler)

class TwitterClient:
    def __init__(self, bearer, consumer_key, consumer_secret, access_token, access_token_secret): 
        self.version = '2'
        self.baseURL = f'https://api.twitter.com/{self.version}'

        self.endpoint = {
            'tweets': '/tweets',
            'users': '/users',
            'by': '/by',
            'username': '/username',
            'search': '/search',
            'recent': '/recent',
            'mentions': '/mentions',
            'me': '/me',
            'trends': '/trends',
            'place': '/place',
            'media': '/media',
            'upload': '/upload',
            'likes': '/likes'
        }

        self.tweetId = '440322224407314432'
        self.userId = ''
        self.bearer = bearer
        self.consumer_key = consumer_key
        self.access_token = access_token
        self.consumer_secret = consumer_secret
        self.access_token_secret = access_token_secret

        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        self.oauth = OAuth1Session(
            self.consumer_key,
            self.consumer_secret,
            self.access_token,
            self.access_token_secret
        )

    def search_by(self, tweetId=None):
        '''
        GET /2/tweets/:tweetId
        特定のIDのツイートをログ出力する
        '''
        self.headers['Authorization'] = f'Bearer {self.bearer}'
        logger.debug(self.headers)

        if tweetId == None:
            tweetId = self.tweetId
        
        request_url = f'{self.baseURL}{self.endpoint["tweets"]}/{tweetId}'

        logger.debug(request_url)
        response = requests.get(request_url, headers=self.headers).json()

        logger.debug(response)
        logger.debug('-----')
    
    def search_text(self, query):
        '''
        GET /2/tweets/search/recent
        直近７日間のツイートを取得する
        '''
        params = { 'query': query }
        request_url = f'{self.baseURL}{self.endpoint["tweets"]}{self.endpoint["search"]}{self.endpoint["recent"]}'

        logger.debug(request_url)

        response = self.oauth.get(request_url, params=params).json()

        data = [tweet['text'] for tweet in response['data']]
        return data

    def search(self, query, max_results=10, next_token=None):
        '''
        GET /2/tweets/search/recent
        直近７日間のツイートを取得する
        search_text()より詳細
        next_tokenで次のページを検索できる
        '''
        params = { 'query': query, 'max_results': max_results, 'next_token': next_token, 'tweet.fields': ['created_at'] }
        request_url = f'{self.baseURL}{self.endpoint["tweets"]}{self.endpoint["search"]}{self.endpoint["recent"]}'

        logger.debug(request_url)

        response = self.oauth.get(request_url, params=params).json()

        if('errors' in response):
            return (response['errors'], None)
        else:
            return (response['data'], response['meta'])

    def users_by(self, username):
        '''
        GET /2/users/by/username/:username
        usernameのid,name(表示名),username(@xxxx), を取得する
        '''
        request_url = f'{self.baseURL}{self.endpoint["users"]}{self.endpoint["by"]}{self.endpoint["username"]}/{username}'

        response = self.oauth.get(request_url).json()
        return response['data']
    
    def users_mentions(self, userId):
        '''
        GET /2/users/:id/mentions
        userIdに対するメンションを取得する
        '''
        request_url = f'{self.baseURL}{self.endpoint["users"]}/{userId}{self.endpoint["mentions"]}'
        response = self.oauth.get(request_url).json()

        return response['data']

    def tweet(self, text="Hello World!", file_path = None):
        '''
        POST /2/tweets
        ツイートする
        同じ内容のツイートはエラーになる
        '''
        params = { 'text': text }

        if file_path is not None:
            media_ids = self.media_image(file_path, 'image/png')
            params['media'] = { 'media_ids': media_ids }

        request_url = f'{self.baseURL}{self.endpoint["tweets"]}'

        return self.oauth.post(request_url, json=params).json()

    def me(self):
        '''
        GET /2/users/me
        使用しているアカウントのユーザー情報を取得する
        '''
        request_url = f'{self.baseURL}{self.endpoint["users"]}{self.endpoint["me"]}'

        response = self.oauth.get(request_url).json()

        return response['data']

    def trends(self, woeId='23424856'):
        '''
        [TODO] V2アカウントでは使用不可？
        GET /1.1/trends/place.json?id={woeid}
        指定したwoeIdの地域のトレンドを取得する
        デフォルト：東京
        '''
        request_url = f'https://api.twitter.com/1.1{self.endpoint["trends"]}{self.endpoint["place"]}.json?id={woeId}'

        response = self.oauth.get(request_url).json()
        
        return response[0]['trends']

    def media_image(self, file_path, media_type='image/jpeg'):
        '''
        GET /1.1/media/upload.json?media_category=tweet_image
        tweetに添付する画像ファイルをアップロードし、medhia_idを返却する
        '''
        uploadURL = 'https://upload.twitter.com/1.1'
        total_bytes = os.path.getsize(file_path)

        with open(file_path, 'rb') as f:
            request_url = f'{uploadURL}{self.endpoint["media"]}{self.endpoint["upload"]}.json?media_category=tweet_image'
            params = { 'total_bytes': total_bytes, 'media_type': media_type }
            files = { 'media': f.read()}
            media = self.oauth.post(request_url, data=params, files=files).json()

        return [str(media['media_id'])]

    def media(self, file_path='./example.jpg'):
        '''
        TODO ちょっと使えるかわからん　試すのが面倒であれば画像アップロードはmedia_image()を使って
        POST /1.1/media

        [issue]
        https://upload.twitter.com/1.1/media/upload.json?command=INIT&total_bytes=10240&media_type=image/jpeg
        {'errors': [{'message': 'Could not authenticate you', 'code': 32}]}

        [solution]
        https://twittercommunity.com/t/1-1-media-upload-json-failing-with-error-code-32/165334/9
        '''

        uploadURL = 'https://upload.twitter.com/1.1'
        command = 'INIT'
        total_bytes = os.path.getsize(file_path)
        media_type = 'image/jpeg'

        request_url = f'{uploadURL}{self.endpoint["media"]}{self.endpoint["upload"]}.json'
        params = { 'command': command, 'total_bytes': total_bytes, 'media_type': media_type }
        logger.debug(f'[INIT PARAM] {params}')

        # {'media_id': 1556544640085803009, 'media_id_string': '1556544640085803009', 'expires_after_secs': 86400}
        media = self.oauth.post(request_url, params).json()
        logger.debug(media)
        media_id = str(media['media_id'])
        logger.debug(media_id)

        with open(file_path, 'rb') as f:
            command = 'APPEND'

            logger.debug(request_url)
            self.oauth.headers.update({ 'Content-Type': 'multipart/form-data' })
            logger.debug(self.oauth.headers)
            
            segment_index = 0
            bytes_sent = 0

            while bytes_sent < total_bytes:
                chunk = f.read(4*1024*1024)

                params = { 'command': command, 'media_id': media_id, 'segment_index': segment_index }

                files = {
                    'media': chunk
                }

                response = self.oauth.post(request_url, data=params, files=files).json()
                logger.debug(f'[APPEND]{response}')

                segment_index = segment_index + 1
                bytes_sent = f.tell()

                logger.debug('%s of %s bytes uploaded' % (str(bytes_sent), str(total_bytes)))

                if response['errors']:
                    return response

            logger.debug('Upload chunks complete.')

        command = 'FINALIZE'
        params = { 'command': command, 'media_id': media_id }
        logger.debug(f'[FINALIZE PARAM] {params}')
        media = self.oauth.post(request_url, params).json()

        return media
    
    def like(self, tweetId, userId=None) -> bool:
        '''
        POST /2/users/:id/likes
        いいねする
        '''
        if not userId is None:
            self.userId = f'{userId}'
        params = { 'tweet_id': tweetId }

        request_url = f'{self.baseURL}{self.endpoint["users"]}/{self.userId}{self.endpoint["likes"]}'
        response = self.oauth.post(request_url, json=params).json()

        logger.debug(response)
        if 'data' in response:    
            return response['data']['liked']
        else:
            return False