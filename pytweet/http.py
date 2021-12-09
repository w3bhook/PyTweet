from __future__ import annotations

import io
import logging
import sys
import time
import requests
from json import JSONDecodeError
from typing import TYPE_CHECKING, Any, Dict, List, NoReturn, Optional, Union

from .attachments import CTA, CustomProfile, File, Geo, Poll, QuickReply
from .auth import OauthSession
from .enums import ReplySetting, SpaceState
from .errors import BadRequests, Conflict, Forbidden, NotFound, NotFoundError, PytweetException, TooManyRequests, Unauthorized
from .expansions import MEDIA_FIELD, PLACE_FIELD, POLL_FIELD, SPACE_FIELD, TWEET_EXPANSION, TWEET_FIELD, USER_FIELD
from .message import DirectMessage, Message
from .parsers import EventParser
from .space import Space
from .stream import Stream
from .tweet import Tweet
from .user import User

_log = logging.getLogger(__name__)


if TYPE_CHECKING:
    RequestModel = Dict[str, Any]
    ResponseModel = Optional[Union[str, RequestModel]]


def check_200(response):
        try:
            res = response.json()
            if "errors" in res.keys():
                if res.get("errors"):
                    if "detail" in res.get("errors")[0].keys():
                        detail = res["errors"][0]["detail"]
                        if detail.startswith("Could not find"):
                            raise NotFoundError(response)
                    elif "details" in res.get("errors")[0].keys():
                        detail = res["errors"][0]["details"][0]
                        if detail.startswith("Cannot parse rule"):
                            _log.warning(
                                f"Invalid stream rule! Rules Info: 'created': {res['meta']['summary'].get('created')}, 'not_created': {res['meta']['summary'].get('not_created')}, 'valid': {res['meta']['summary'].get('valid')}, 'invalid': {res['meta']['summary'].get('invalid')}"
                            )
                            raise SyntaxError(detail)
            


                else:
                    raise PytweetException(response, res["errors"][0]["detail"])
        except (JSONDecodeError, KeyError) as e:
            if isinstance(e, KeyError):
                raise PytweetException(res)
            return

def check_error(response: requests.models.Response) -> NoReturn:
    code = response.status_code
    if code == 200:
        try:
            res = response.json()
            if "errors" in res.keys():
                if res.get("errors"):
                    if "detail" in res.get("errors")[0].keys():
                        detail = res["errors"][0]["detail"]
                        if detail.startswith("Could not find"):
                            raise NotFoundError(response)
                    elif "details" in res.get("errors")[0].keys():
                        detail = res["errors"][0]["details"][0]
                        if detail.startswith("Cannot parse rule"):
                            _log.warning(
                                f"Invalid stream rule! Rules Info: 'created': {res['meta']['summary'].get('created')}, 'not_created': {res['meta']['summary'].get('not_created')}, 'valid': {res['meta']['summary'].get('valid')}, 'invalid': {res['meta']['summary'].get('invalid')}"
                            )
                            raise SyntaxError(detail)
            


                else:
                    raise PytweetException(response, res["errors"][0]["detail"])
        except (JSONDecodeError, KeyError) as e:
            if isinstance(e, KeyError):
                raise PytweetException(res)
            return

    elif code in (201, 202, 204):
        pass

    elif code == 400:
        raise BadRequests(response)

    elif code == 401:
        raise Unauthorized(response)

    elif code == 403:
        raise Forbidden(response)

    elif code == 404:
        raise NotFound(response)

    elif code == 409:
        raise Conflict(response)

    elif code == 429:
        remaining = int(response.headers["x-rate-limit-reset"])
        sleep_for = (remaining - int(time.time())) + 1
        _log.warn(f"Client has been ratelimited. Sleeping for {sleep_for}")
        time.sleep(sleep_for)


    else:
        raise PytweetException(
            f"Unknown exception raised (status code: {response.status_code}): Open an issue in github or go to the support server to report this unknown exception!"
        )




class HTTPClient:
    def __init__(
        self,
        bearer_token: str,
        *,
        consumer_key: Optional[str],
        consumer_key_secret: Optional[str],
        access_token: Optional[str],
        access_token_secret: Optional[str],
        stream: Optional[Stream] = None,
    ) -> Union[None, NoReturn]:
        self.credentials: Dict[str, Optional[str]] = {
            "bearer_token": bearer_token,
            "consumer_key": consumer_key,
            "consumer_key_secret": consumer_key_secret,
            "access_token": access_token,
            "access_token_secret": access_token_secret,
        }
        if not bearer_token:
            _log.error("bearer token is missing!")
        if not consumer_key:
            _log.warning("Consumer key is missing this is recommended to have!")
        if not access_token:
            _log.warning("Access token is missing this is recommended to have")
        if not access_token_secret:
            _log.warning("Access token secret is missing this is required if you have passed in the access_toke param.")

        for k, v in self.credentials.items():
            if not isinstance(v, str) and not isinstance(v, type(None)):
                raise Unauthorized(None, f"Wrong authorization passed for credential: {k}.")

        self.__session = requests.Session()
        self.bearer_token: Optional[str] = bearer_token
        self.consumer_key: Optional[str] = consumer_key
        self.consumer_key_secret: Optional[str] = consumer_key_secret
        self.access_token: Optional[str] = access_token
        self.access_token_secret: Optional[str] = access_token_secret
        self.stream = stream
        self.event_parser = EventParser(self)
        self.base_url = "https://api.twitter.com/"
        self.upload_url = "https://upload.twitter.com/1.1/media/upload.json"
        self._auth = None # Set in request method.
        self.message_cache = {}
        self.tweet_cache = {}
        self.user_cache = {}
        self.events = {}
        if self.stream:
            self.stream.http_client = self
            self.stream.connection.http_client = self

    def dispatch(self, event_name: str, *args: Any):
        try:
            event = self.events[event_name]
        except KeyError:
            return
        else:
            event(*args)

    def request(
        self,
        method: str,
        version: str,
        path: str,
        *,
        headers: RequestModel = {},
        params: RequestModel = {},
        json: RequestModel = {},
        data: RequestModel = {},
        files: RequestModel = {},
        auth: bool = False,
        is_json: bool = True,
        use_base_url: bool = True,
    ) -> ResponseModel:
        if use_base_url:
            url = self.base_url + version + path
        else:
            url = path
        
        if self._auth is None:
            auth_session = OauthSession(self.consumer_key, self.consumer_key_secret)
            auth_session.set_access_token(self.access_token, self.access_token_secret)
            self._auth = auth_session


        user_agent = "Py-Tweet (https://github.com/PyTweet/PyTweet/) Python/{0[0]}.{0[1]}.{0[2]} requests/{1}"
        if "Authorization" not in headers.keys():
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        headers["User-Agent"] = user_agent.format(sys.version_info, requests.__version__)

        if auth:
            for k, v in self.credentials.items():
                if v is None:
                    raise PytweetException(f"{k} is a required credential for this action.")
            auth = self._auth.oauth1

        if data:
            json = None
        if json:
            data = None
        
        method = method.upper()
        response = self.__session.request(
            method,
            url,
            headers=headers,
            params=params,
            data=data,
            json=json,
            files=files,
            auth=auth,
        )
        code = response.staus_code
        res = None

        if code == 200:
            check_200(response)
        
        elif code in {201, 202, 204}:
            return None

        elif code == 400:
           raise BadRequests(response)

        elif code == 401:
            raise Unauthorized(response)

        elif code == 403:
            raise Forbidden(response)

        elif code == 404:
            raise NotFound(response)

        elif code == 409:
            raise Conflict(response)

        elif code == 429:
            remaining = int(response.headers["x-rate-limit-reset"])
            sleep_for = (remaining - int(time.time())) + 1
            _log.warn(f"Client has been ratelimited. Sleeping for {sleep_for}")
            time.sleep(sleep_for)
            response = self.__session.request(
            method,
            url,
            headers=headers,
            params=params,
            data=data,
            json=json,
            files=files,
            auth=auth,
        )


        if is_json:
            try:
                res = response.json()
            except JSONDecodeError:
                return response.text
        else:
            return response.text

        if "meta" in res.keys():
            try:
                if res["meta"]["result_count"] == 0:
                    return []
            except KeyError:
                pass

        _log.debug(f'{method} {url} has returned {response.status_code} status code with {res}')
        return res

    def upload(self, file: File, command: str, *, media_id=None):
        assert command.upper() in ("INIT", "APPEND", "FINALIZE", "STATUS")
        auth = OauthSession(self.consumer_key, self.consumer_key_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        auth = auth.oauth1

        def CheckStatus(processing_info, media_id):
            if not processing_info:
                return

            state = processing_info["state"]
            seconds = processing_info.get("check_after_secs")
            if seconds is None:
                return None

            if state == "succeeded":
                return

            if state == "failed":
                raise PytweetException("Failed to finalize Media!")

            time.sleep(seconds)

            res = self.request(
                "GET",
                version=None,
                path=self.base_url,
                params={"command": "STATUS", "media_id": media_id},
                auth=True,
                use_base_url=False,
            )

            processing_info = res.get("processing_info", None)
            CheckStatus(processing_info, media_id)

        if command.upper() == "INIT":
            data = {
                "command": "INIT",
                "media_type": file.mimetype,
                "total_bytes": file.total_bytes,
                "media_category": file.media_category,
                "shared": file.dm_only,
            }
            res = self.request(
                "POST",
                version=None,
                path=self.upload_url,
                data=data,
                auth=True,
                use_base_url=False,
            )

            return res["media_id"]

        elif command.upper() == "APPEND":
            segment_id = 0
            bytes_sent = 0
            path = file.path
            if isinstance(path, io.IOBase):
                open_file = path
            else:
                open_file = open(file.path, "rb")

            if not media_id:
                raise ValueError("'media_id' is None! Please specified it.")

            while bytes_sent < file.total_bytes:
                res = self.request(
                    "POST",
                    version=None,
                    path=self.upload_url,
                    data={
                        "command": "APPEND",
                        "media_id": media_id,
                        "segment_index": segment_id,
                    },
                    files={"media": open_file.read(4 * 1024 * 1024)},
                    auth=True,
                    use_base_url=False,
                )

                bytes_sent = open_file.tell()
                segment_id += 1

        elif command.upper() == "FINALIZE":
            res = self.request(
                "POST",
                version=None,
                path=self.upload_url,
                data={"command": "FINALIZE", "media_id": media_id},
                auth=True,
                use_base_url=False,
            )

            CheckStatus(res.get("processing_info", None), media_id)

    def fetch_user(self, user_id: Union[str, int]) -> Optional[User]:
        try:
            int(user_id)
        except ValueError:
            raise ValueError("user_id must be an int, or a string of digits!")

        try:

            data = self.request(
                "GET",
                "2",
                f"/users/{user_id}",
                headers={"Authorization": f"Bearer {self.bearer_token}"},
                params={"user.fields": USER_FIELD},
                is_json=True,
            )

            return User(data, http_client=self)

        except NotFoundError:
            return None

    def fetch_user_byname(self, username: str) -> Optional[User]:
        if "@" in username:
            username = username.replace("@", "", 1)

        try:

            data = self.request(
                "GET",
                "2",
                f"/users/by/username/{username}",
                headers={"Authorization": f"Bearer {self.bearer_token}"},
                params={"user.fields": USER_FIELD},
                is_json=True,
            )

            return User(data, http_client=self)

        except NotFoundError:
            return None

    def fetch_tweet(self, tweet_id: Union[str, int]) -> Tweet:
        try:

            res = self.request(
                "GET",
                "2",
                f"/tweets/{tweet_id}",
                params={
                    "tweet.fields": TWEET_FIELD,
                    "user.fields": USER_FIELD,
                    "expansions": TWEET_EXPANSION,
                    "media.fields": MEDIA_FIELD,
                    "place.fields": PLACE_FIELD,
                    "poll.fields": POLL_FIELD,
                },
                auth=True,
            )

            return Tweet(res, http_client=self)

        except NotFoundError:
            return None

    def fetch_space(self, space_id: str) -> Space:
        res = self.request(
            "GET",
            "2",
            f"/spaces/{str(space_id)}",
            params={"space.fields": SPACE_FIELD},
        )
        return Space(res)

    def fetch_space_bytitle(self, title: str, state: SpaceState = SpaceState.live) -> Space:
        res = self.request(
            "GET",
            "2",
            "/spaces/search",
            params={
                "query": title,
                "state": state.value,
                "space.fields": SPACE_FIELD,
            },
        )
        return Space(res)

    def handle_events(self, payload: Dict[str, Any]):
        keys = list(payload.keys())
        if "direct_message_events" in keys:
            self.event_parser.parse_direct_message_create(payload)

        elif "follow_events" in keys:
            self.event_parser.parse_user_follow(payload)

        elif "direct_message_indicate_typing_events" in keys:
            self.event_parser.parse_direct_message_typing(payload)

    def send_message(
        self,
        user_id: Union[str, int],
        text: str,
        *,
        file: Optional[File] = None,
        custom_profile: Optional[CustomProfile] = None,
        quick_reply: Optional[QuickReply] = None,
        cta: Optional[CTA] = None,
    ) -> Optional[NoReturn]:
        data = {
            "event": {
                "type": "message_create",
                "message_create": {
                    "target": {"recipient_id": str(user_id)},
                    "message_data": {},
                },
            }
        }

        if file and (not isinstance(file, File)):
            raise PytweetException("'file' argument must be an instance of pytweet.File")

        if custom_profile and (not isinstance(custom_profile, CustomProfile)):
            raise PytweetException("'custom_profile' argument must be an instance of pytweet.CustomProfile")

        if quick_reply and (not isinstance(quick_reply, QuickReply)):
            raise PytweetException("'quick_reply' must be an instance of pytweet.QuickReply")

        if cta and (not isinstance(cta, CTA)):
            raise PytweetException("'cta' argument must be an instance of pytweet.CTA")

        message_data = data["event"]["message_create"]["message_data"]
        message_data["text"] = str(text)

        if file:
            media_id = self.upload(file, "INIT")
            self.upload(file, "APPEND", media_id=media_id)
            self.upload(file, "FINALIZE", media_id=media_id)

            message_data["attachment"] = {}
            message_data["attachment"]["type"] = "media"
            message_data["attachment"]["media"] = {}
            message_data["attachment"]["media"]["id"] = str(media_id)

        if custom_profile:
            message_data["custom_profile_id"] = str(custom_profile.id)

        if quick_reply:
            message_data["quick_reply"] = {
                "type": quick_reply.type,
                "options": quick_reply.raw_options,
            }

        if cta:
            message_data["ctas"] = cta.raw_buttons

        res = self.request(
            "POST",
            "1.1",
            "/direct_messages/events/new.json",
            json=data,
            auth=True,
        )

        message_create = res.get("event").get("message_create")
        user_id = message_create.get("target").get("recipient_id")
        user = self.fetch_user(user_id)
        res["event"]["message_create"]["target"]["recipient"] = user

        msg = DirectMessage(res, http_client=self or self)
        self.message_cache[msg.id] = msg
        return msg

    def fetch_message(self, event_id: Union[str, int]) -> Optional[DirectMessage]:
        try:
            event_id = str(event_id)
        except ValueError:
            raise ValueError("event_id must be an integer or a :class:`str`ing of digits.")

        res = self.request("GET", "1.1", f"/direct_messages/events/show.json?id={event_id}", auth=True)

        message_create = res.get("event").get("message_create")
        user_id = message_create.get("target").get("recipient_id")
        user = self.fetch_user(user_id)
        res["event"]["message_create"]["target"]["recipient"] = user

        return DirectMessage(res, http_client=self)

    def post_tweet(
        self,
        text: str = None,
        *,
        file: Optional[File] = None,
        poll: Optional[Poll] = None,
        geo: Optional[Union[Geo, str]] = None,
        quote_tweet: Optional[Union[str, int]] = None,
        direct_message_deep_link: Optional[str] = None,
        reply_setting: Optional[str] = None,
        reply_tweet: Optional[Union[str, int]] = None,
        exclude_reply_users: Optional[List[Union[str, int]]] = None,
        super_followers_only: Optional[bool] = None,
    ) -> Optional[Message]:
        payload = {}
        if text:
            payload["text"] = text

        if file:
            media_id = self.upload(file, "INIT")
            self.upload(file, "APPEND", media_id=media_id)
            self.upload(file, "FINALIZE", media_id=media_id)

            payload["media"] = {}
            payload["media"]["media_ids"] = [str(media_id)]

        if poll:
            payload["poll"] = {}
            payload["poll"]["options"] = [option.label for option in poll.options]
            payload["poll"]["duration_minutes"] = int(poll.duration)

        if geo:
            if not isinstance(geo, Geo) and not isinstance(geo, str):
                raise TypeError("'geo' must be an instance of pytweet.Geo or str")

            payload["geo"] = {}
            payload["geo"]["place_id"] = geo.id if isinstance(geo, Geo) else geo

        if quote_tweet:
            payload["quote_tweet_id"] = str(quote_tweet)

        if direct_message_deep_link:
            payload["direct_message_deep_link"] = direct_message_deep_link

        if reply_setting:
            payload["reply_settings"] = (
                reply_setting.value if isinstance(reply_setting, ReplySetting) else reply_setting
            )

        if reply_tweet or exclude_reply_users:
            if reply_tweet:
                payload["reply"] = {}
                payload["reply"]["in_reply_to_tweet_id"] = str(reply_tweet)

            if exclude_reply_users:
                if "reply" in payload.keys():
                    payload["reply"]["exclude_reply_user_ids"] = [str(id) for id in exclude_reply_users]
                else:
                    payload["reply"] = {}
                    payload["reply"]["exclude_reply_user_ids"] = [str(id) for id in exclude_reply_users]

        if super_followers_only:
            payload["for_super_followers_only"] = True

        res = self.request("POST", "2", "/tweets", json=payload, auth=True)
        data = res.get("data")
        return Message(data.get("text"), data.get("id"), 1)
