from __future__ import annotations

import io
import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional, Union, List

from .constants import (
    TWEET_EXPANSION,
    LIST_EXPANSION,
    PINNED_TWEET_EXPANSION,
    MEDIA_FIELD,
    PLACE_FIELD,
    POLL_FIELD,
    TWEET_FIELD,
    USER_FIELD,
    LIST_FIELD,
)
from .metrics import UserPublicMetrics
from .relations import RelationFollow
from .utils import time_parse_todt
from .dataclass import UserSettings, Location
from .paginations import UserPagination, TweetPagination, ListPagination
from .list import List as TwitterList
from .objects import Comparable

if TYPE_CHECKING:
    from .message import DirectMessage
    from .http import HTTPClient
    from .type import ID
    from .tweet import Tweet
    from .enums import Timezone
    from .attachments import Geo, CTA, CustomProfile, File, QuickReply


class User(Comparable):
    """Represents a user in Twitter.
    User is an identity in twitter, its very interactive. Can send message, post a tweet, and even send messages to other user through Dms.


    .. describe:: x == y

        Check if one user id is equal to another.


    .. describe:: x != y

        Check if one user id is not equal to another.


    .. describe:: str(x)

        Get the user's name.


    .. versionadded: 1.0.0
    """

    __slots__ = (
        "__original_payload",
        "_includes",
        "_payload",
        "http_client",
        "_metrics",
    )

    def __init__(self, data: Dict[str, Any], http_client: Optional[HTTPClient] = None) -> None:
        self.__original_payload = data
        self._includes = self.__original_payload.get("includes")
        self._payload = self.__original_payload.get("data") or self.__original_payload
        self.http_client = http_client
        self._metrics = UserPublicMetrics(self._payload) or self.__original_payload
        super().__init__(self.id)

    def __str__(self) -> str:
        return self.username

    def __repr__(self) -> str:
        return "User(name={0.name} username={0.username} id={0.id})".format(self)

    @property
    def name(self) -> str:
        """:class:`str`: Return the user's name.

        .. versionadded: 1.0.0
        """
        return self._payload.get("name")

    @property
    def username(self) -> str:
        """:class:`str`: Return the user's username.

        .. versionadded: 1.0.0
        """
        return self._payload.get("username")

    @property
    def id(self) -> int:
        """:class:`int`: Return the user's id.

        .. versionadded: 1.0.0
        """
        return int(self._payload.get("id"))

    @property
    def description(self) -> str:
        """:class:`str`: Return the user's description.

        .. versionadded: 1.0.0
        """
        return self._payload.get("description")

    @property
    def bio(self) -> str:
        """:class:`str`: an alias to :meth:`User.description`.

        .. versionadded: 1.0.0
        """
        return self.description

    @property
    def mention(self) -> str:
        """:class:`str`: Return the user mention format.

        .. versionadded: 1.5.0
        """
        return "@" + self.username

    @property
    def pinned_tweet(self) -> Optional[Tweet]:
        """Optional[:class:`Tweet`]: Returns the user's pinned tweet. Returns None if the user dont have one.

        .. versionadded:: 1.5.0
        """
        from .tweet import Tweet  # Avoid circular import error.

        if self._includes and self._includes.get("tweets"):
            data = {}
            data["data"] = self._includes.get("tweets")[0]
            data["includes"] = {}
            data["includes"]["users"] = [self.__original_payload]
            return Tweet(data, http_client=self.http_client)
        return None

    @property
    def url(self) -> Optional[str]:
        """:class:`str`: Return url that associated with the user profile.

        .. versionadded: 1.0.0
        """
        return self._payload.get("url", None)

    @property
    def profile_url(self) -> str:
        """:class:`str`: Return the user's profile url.

        .. versionadded: 1.0.0
        """
        return f"https://twitter.com/{self.username}"

    @property
    def profile_image_url(self) -> Optional[str]:
        """Optional[:class:`str`] Return the user profile image url.

        .. versionadded: 1.0.0
        """
        return self._payload.get("profile_image_url", None)

    @property
    def verified(self) -> bool:
        """:class:`bool`: Return True if the user is verified account, else False.

        .. versionadded: 1.0.0
        """
        return self._payload.get("verified")

    @property
    def protected(self) -> bool:
        """:class:`bool`: Return True if the user is protected, else False.

        .. versionadded: 1.0.0
        """
        return self._payload.get("protected")

    @property
    def private(self) -> bool:
        """:class:`bool`: An alias to :meth:`User.protected`.

        .. versionadded: 1.3.5
        """
        return self.protected

    @property
    def location(self) -> Optional[str]:
        """:class:`str`: Return the user's location.

        .. versionadded: 1.0.0
        """
        return self._payload.get("location", None)

    @property
    def created_at(self) -> datetime.datetime:
        """Optional[:class:`datetime.datetime`]: Returns a datetime.datetime object with the user's account date.

        .. versionadded: 1.0.0
        """
        if isinstance(self._payload.get("created_at"), str):
            return datetime.datetime.fromtimestamp(int(self._payload.get("created_at")) / 1000)
        return time_parse_todt(self._payload.get("created_at"))

    @property
    def follower_count(self) -> int:
        """:class:`int`: Return total of followers that a user has.

        .. versionadded: 1.1.0
        """
        return self._metrics.follower_count

    @property
    def following_count(self) -> int:
        """:class:`int`: Return total of following that a user has.

        .. versionadded: 1.1.0
        """
        return self._metrics.following_count

    @property
    def tweet_count(self) -> int:
        """:class:`int`: Return total of tweet that a user has.

        .. versionadded: 1.1.0
        """
        return self._metrics.tweet_count

    @property
    def listed_count(self) -> int:
        """:class:`int`: Return total of listed that a user has.

        .. versionadded: 1.1.0
        """
        return self._metrics.listed_count

    def send(
        self,
        text: str,
        *,
        file: Optional[File] = None,
        custom_profile: Optional[CustomProfile] = None,
        quick_reply: Optional[QuickReply] = None,
        cta: Optional[CTA] = None,
    ) -> DirectMessage:
        """Send a message to the user.

        Parameters
        ------------
        text: :class:`str`
            The text that will be send to that user.
        file: Optional[:class:`File`]
            Represents a single file attachment. It could be an image, gif, or video. It also have to be an instance of pytweet.File.
        custom_profile: Optional[:class:`CustomProfile`]
            The custom profile attachment.
        quick_reply: Optional[:class:`QuickReply`]
            The QuickReply attachment that will be send to a user.
        cta: Optional[:class:`CTA`]
            cta or call-to-actions is use to make an action whenever a user 'call' something, a quick example is buttons.

        Returns
        ---------
        :class:`DirectMessage`
            This method return a :class:`DirectMessage` object.


        .. versionadded:: 1.1.0
        """
        return self.http_client.send_message(
            self.id,
            text,
            file=file,
            custom_profile=custom_profile,
            quick_reply=quick_reply,
            cta=cta,
        )

    def follow(self) -> RelationFollow:
        """Follows the User.

        Returns
        ---------
        :class:`RelationFollow`
            This method return a :class:`RelationFollow` object.


        .. versionadded:: 1.1.0
        """
        my_id = self.http_client.access_token.partition("-")[0]
        res = self.http_client.request(
            "POST",
            "2",
            f"/users/{my_id}/following",
            json={"target_user_id": str(self.id)},
            auth=True,
        )
        return RelationFollow(res)

    def unfollow(self) -> RelationFollow:
        """Unfollows the User.

        Returns
        ---------
        :class:`RelationFollow`
            This method return a :class:`RelationFollow` object.


        .. versionadded:: 1.1.0
        """
        my_id = self.http_client.access_token.partition("-")[0]
        res = self.http_client.request("DELETE", "2", f"/users/{my_id}/following/{self.id}", auth=True)
        return RelationFollow(res)

    def block(self) -> None:
        """Blocks the user.

        .. versionadded:: 1.2.0
        """
        my_id = self.http_client.access_token.partition("-")[0]
        self.http_client.request(
            "POST",
            "2",
            f"/users/{my_id}/blocking",
            json={"target_user_id": str(self.id)},
            auth=True,
        )

    def unblock(self) -> None:
        """Unblocks the user.

        .. versionadded:: 1.2.0
        """
        my_id = self.http_client.access_token.partition("-")[0]
        self.http_client.request("DELETE", "2", f"/users/{my_id}/blocking/{self.id}", auth=True)

    def mute(self) -> None:
        """Mutes the user.

        .. versionadded:: 1.2.5
        """
        my_id = self.http_client.access_token.partition("-")[0]
        self.http_client.request(
            "POST",
            "2",
            f"/users/{my_id}/muting",
            json={"target_user_id": str(self.id)},
            auth=True,
        )

    def unmute(self) -> None:
        """Unmutes the user.

        .. versionadded:: 1.2.5
        """
        my_id = self.http_client.access_token.partition("-")[0]
        self.http_client.request("DELETE", "2", f"/users/{my_id}/muting/{self.id}", auth=True)

    def report(self, *, block: bool = True):
        """Reports the user as a spam account to twitter.

        Parameters
        -----------
        block: :class:`bool`
            Indicates to perform a block action to the user if set to True. Default to True.


        .. versionadded:: 1.3.5
        """
        self.http_client.request(
            "POST",
            "1.1",
            "/users/report_spam.json",
            params={"user_id": str(self.id), "perform_block": block},
        )

    def trigger_typing(self):
        """Trigger the typing animation in the user's dm. W ill stop when the client decide to send a message when the typing animation is playing or in couple of seconds.

        .. versionadded:: 1.3.5
        """
        self.http_client.request(
            "POST",
            "1.1",
            "/direct_messages/indicate_typing.json",
            params={"recipient_id": str(self.id)},
            auth=True,
        )

    def fetch_followers(self) -> Optional[UserPagination]:
        """Fetches users from the user's followers list then paginate it .

        Returns
        ---------
        Optional[:class:`UserPagination`]
            This method returns a :class:`UserPagination` object.


        .. versionadded:: 1.3.5
        """
        following = self.http_client.request(
            "GET",
            "2",
            f"/users/{self.id}/followers",
            params={
                "expansions": PINNED_TWEET_EXPANSION,
                "user.fields": USER_FIELD,
                "tweet.fields": TWEET_FIELD,
            },
        )

        if not following:
            return []

        return UserPagination(
            following,
            endpoint_request=f"/users/{self.id}/followers",
            http_client=self.http_client,
            params={
                "expansions": PINNED_TWEET_EXPANSION,
                "user.fields": USER_FIELD,
                "tweet.fields": TWEET_FIELD,
            },
        )

    def fetch_following(self) -> Optional[UserPagination]:
        """Fetches users from the user's following list then paginate it.

        Returns
        ---------
        Optional[:class:`UserPagination`]
            This method returns a :class:`UserPagination` object.


        .. versionadded:: 1.3.5
        """
        following = self.http_client.request(
            "GET",
            "2",
            f"/users/{self.id}/following",
            params={
                "expansions": PINNED_TWEET_EXPANSION,
                "user.fields": USER_FIELD,
                "tweet.fields": TWEET_FIELD,
            },
        )

        if not following:
            return []

        return UserPagination(
            following,
            endpoint_request=f"/users/{self.id}/following",
            http_client=self.http_client,
            params={
                "expansions": PINNED_TWEET_EXPANSION,
                "user.fields": USER_FIELD,
                "tweet.fields": TWEET_FIELD,
            },
        )

    def fetch_blockers(self) -> Optional[UserPagination]:
        """Fetches users from the user's block list then paginate it.

        Returns
        ---------
        Optional[:class:`UserPagination`]
            This method returns a :class:`UserPagination` object.


        .. versionadded:: 1.5.0
        """
        blockers = self.http_client.request(
            "GET",
            "2",
            f"/users/{self.id}/blocking",
            params={
                "expansions": PINNED_TWEET_EXPANSION,
                "user.fields": USER_FIELD,
                "tweet.fields": TWEET_FIELD,
            },
            auth=True,
        )

        if not blockers:
            return []

        return UserPagination(
            blockers,
            endpoint_request=f"/users/{self.id}/blocking",
            http_client=self.http_client,
            params={
                "expansions": PINNED_TWEET_EXPANSION,
                "user.fields": USER_FIELD,
                "tweet.fields": TWEET_FIELD,
            },
        )

    def fetch_muters(self) -> Optional[UserPagination]:
        """Fetches users from the user's mute list then paginate it.

        Returns
        ---------
        Optional[:class:`UserPagination`]
            This method returns a :class:`UserPagination` object.


        .. versionadded:: 1.5.0
        """
        muters = self.http_client.request(
            "GET",
            "2",
            f"/users/{self.id}/muting",
            params={
                "expansions": PINNED_TWEET_EXPANSION,
                "user.fields": USER_FIELD,
                "tweet.fields": TWEET_FIELD,
            },
            auth=True,
        )

        if not muters:
            return []

        return UserPagination(
            muters,
            endpoint_request=f"/users/{self.id}/muting",
            http_client=self.http_client,
            params={
                "expansions": PINNED_TWEET_EXPANSION,
                "user.fields": USER_FIELD,
                "tweet.fields": TWEET_FIELD,
            },
        )

    def fetch_timelines(
        self,
        *,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        since_id: Optional[ID] = None,
        until_id: Optional[ID] = None,
        mentioned: bool = False,
        exclude: Optional[str] = None,
    ) -> Union[TweetPagination, list]:
        """Fetches the user timelines, this can be timelines where the user got mention or a normal tweet timelines.

        Parameters
        ------------
        start_time: Optional[:class:`datetime.datetime`]
            This will make sure the tweets created datetime is after that specific time.
        end_time: Optional[:class:`datetime.datetime`]
            This will make sure the tweets created datetime is before that specific time.
        since_id: Optional[`ID`]
            Returns results with a Tweet ID greater than (that is, more recent than) the specified 'since' Tweet ID. Only the 3200 most recent Tweets are available. The result will exclude the since_id. If the limit of Tweets has occurred since the since_id, the since_id will be forced to the oldest ID available.
        until_id: Optional[`ID`]
            Returns results with a Tweet ID less less than (that is, older than) the specified 'until' Tweet ID. Only the 3200 most recent Tweets are available. The result will exclude the until_id. If the limit of Tweets has occurred since the until_id, the until_id will be forced to the most recent ID available.
        mentioned: :class:`bool`
            Indicates if only mentioned timelines return if set to True, else it will returns a normal tweet timelines. Default to False.
        exclude: :class:`str`
            Specified which tweet type should not be returns, you can set it to:'retweets,replies' or 'retweets' or 'replies'.

        Returns
        ---------
        Union[:class:`TweetPagination`, :class:`list`]
            This method returns a :class:`TweetPagination` objects or an empty :class:`list` if none founded.


        .. versionadded:: 1.3.5
        """
        if (
            not isinstance(start_time, datetime.datetime)
            and start_time
            or not isinstance(end_time, datetime.datetime)
            and end_time
        ):
            raise ValueError("start_time or end_time must be a datetime object!")

        params = {
            "expansions": TWEET_EXPANSION,
            "user.fields": USER_FIELD,
            "media.fields": MEDIA_FIELD,
            "place.fields": PLACE_FIELD,
            "poll.fields": POLL_FIELD,
            "tweet.fields": TWEET_FIELD,
        }

        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()
        if since_id:
            params["since_id"] = str(since_id)
        if until_id:
            params["until_id"] = str(until_id)
        if exclude:
            params["exclude"] = exclude

        res = self.http_client.request(
            "GET",
            "2",
            f"/users/{self.id}/tweets" if not mentioned else f"/users/{self.id}/mentions",
            params=params,
        )

        if not res:
            return []
        return TweetPagination(
            res,
            endpoint_request=f"/users/{self.id}/tweets" if not mentioned else f"/users/{self.id}",
            http_client=self.http_client,
            params=params,
        )

    def fetch_liked_tweets(self) -> TweetPagination:
        """Fetches tweets that's been liked by the user.

        .. versionadded:: 1.5.0
        """
        params = {
            "expansions": TWEET_EXPANSION,
            "user.fields": USER_FIELD,
            "media.fields": MEDIA_FIELD,
            "place.fields": PLACE_FIELD,
            "poll.fields": POLL_FIELD,
            "tweet.fields": TWEET_FIELD,
        }

        res = self.http_client.request(
            "GET",
            "2",
            f"/users/{self.id}/liked_tweets",
            params=params,
        )

        if not res:
            return []
        return TweetPagination(
            res,
            endpoint_request=f"/users/{self.id}/liked_tweets",
            http_client=self.http_client,
            params=params,
        )

    def fetch_pinned_tweet(self) -> Optional[Tweet]:
        """Fetches the user's pinned tweet, consider using this method if :meth:`User.pinned_tweet` returns None.

        Returns
        ---------
        Optional[:class:`Tweet`]
            This method returns a :class:`Tweet` object.


        .. versionadded: 1.1.3
        """
        id = self._payload.get(PINNED_TWEET_EXPANSION)
        return self.http_client.fetch_tweet(int(id)) if id else None

    def fetch_lists(self) -> Optional[List[TwitterList]]:
        """Fetches the user's lists

        Returns
        ---------
        Optional[List[:class:`List`]]
            This method returns a list of :class:`List` objects.


        .. versionadded:: 1.5.0
        """
        params = {
            "expansions": LIST_EXPANSION,
            "list.fields": LIST_FIELD,
            "user.fields": USER_FIELD,
        }

        res = self.http_client.request("GET", "2", f"/users/{self.id}/owned_lists", params=params)

        if not res:
            return []

        return ListPagination(
            res,
            endpoint_request=f"/users/{self.id}/owned_lists",
            http_client=self.http_client,
            params=params,
        )

    def fetch_pinned_lists(self) -> Optional[List[TwitterList]]:
        """Fetches the user's pinned lists, returns an empty list if not found

        Returns
        ---------
        Optional[List[:class:`List`]]:
            This method returns a list of :class:`List` objects.


        .. versionadded:: 1.5.0
        """
        res = self.http_client.request(
            "GET",
            "2",
            f"/users/{self.id}/pinned_lists",
            auth=True,
            params={
                "expansions": LIST_EXPANSION,
                "user.fields": USER_FIELD,
                "list.fields": LIST_FIELD,
            },
        )
        if not res:
            return None

        for data in res["data"]:
            self.http_client.payload_parser.insert_list_owner(data, self)

        return [TwitterList(data, http_client=self.http_client) for data in res["data"]]

    def fetch_list_memberships(self) -> Union[ListPagination, List]:
        """Fetches all :class:`List`s the user is a member of.

        Returns
        ---------
        Optional[List[:class:`List`]]
            This method returns a list of :class:`List` objects.


        .. versionadded:: 1.5.0
        """
        params = {
            "expansions": LIST_EXPANSION,
            "list.fields": LIST_FIELD,
            "user.fields": USER_FIELD,
        }

        res = self.http_client.request("GET", "2", f"/users/{self.id}/list_memberships", params=params)

        if not res:
            return []

        return ListPagination(
            res,
            endpoint_request=f"/users/{self.id}/list_memberships",
            http_client=self.http_client,
            params=params,
        )

    def fetch_followed_lists(self) -> Union[ListPagination, List]:
        """Fetches the user's followed lists.


        .. versionadded:: 1.5.0
        """
        params = {
            "expansions": LIST_EXPANSION,
            "list.fields": LIST_FIELD,
            "user.fields": USER_FIELD,
        }

        res = self.http_client.request("GET", "2", f"/users/{self.id}/followed_lists", params=params)

        if not res:
            return []

        return ListPagination(
            res,
            endpoint_request=f"/users/{self.id}/followed_lists",
            http_client=self.http_client,
            params=params,
        )


class ClientAccount(User):
    """Represents the client's account. This inherits :class:`User` object. This class unlocks methods that you can only use for the authenticated user (the client).

    .. versionadded:: 1.5.0
    """

    def update_setting(
        self,
        *,
        lang: Optional[str] = None,
        enabled_sleep_time: Optional[bool] = None,
        start_sleep_time: Optional[datetime.datetime] = None,
        end_sleep_time: Optional[datetime.datetime] = None,
        timezone: Optional[Timezone] = None,
        location: Optional[Location, int] = None,
    ):
        """Updates the user settings.

        Parameters
        ------------
        lang: Optional[:class:`str`]
            The new language replacing the old one.
        enabled_sleep_time: Optional[:class:`bool`]
            Indicates to enabled sleep time.
        start_sleep_time: Optional[:class:`int`]
            The hour that sleep time should begin if it is enabled. Must be an instance of datetime.datetime.
        end_sleep_time: Optional[:class:`int`]
            The hour that sleep time should end if it is enabled. Must be an instance of datetime.datetime.
        timezone: Optional[:class:`Timezone`]
            The new timezone replacing the old one. Must be an instance of :class:`Timezone` (e.g :attr:`Timezone.jakarta` or :attr:`Timezone.paris`)
        location: Optional[:class:`Location`, :class:`int`]
            The Yahoo! Where On Earth ID to use as the user's default trend location. Global information is available by using 1 as the WOEID. Must be an instance of :class:`Location` or the woeid in :class:`int`.


        .. versionadded:: 1.5.0
        """
        res = self.http_client.request(
            "POST",
            "1.1",
            "/account/settings.json",
            params={
                "sleep_time_enabled": enabled_sleep_time,
                "start_sleep_time": start_sleep_time,
                "end_sleep_time": end_sleep_time,
                "time_zone": timezone.value if isinstance(timezone, Timezone) else timezone,
                "trend_location_woeid": location.woeid if isinstance(location, Location) else location,
                "lang": lang,
            },
            auth=True,
        )
        if res.get("sleep_time"):
            self.http_client.payload_parser.parse_sleep_time_payload(res)

        if res.get("location"):
            self.http_client.payload_parser.parse_trend_location_payload(res)

        if res.get("time_zone"):
            self.http_client.payload_parser.parse_time_zone_payload(res)

        return UserSettings(**res)

    def fetch_settings(self):
        """Fetches the user settings.


        .. versionadded:: 1.5.0
        """
        res = self.http_client.request("GET", "1.1", "/account/settings.json", auth=True)
        if res.get("sleep_time"):
            self.http_client.payload_parser.parse_sleep_time_payload(res)

        if res.get("location"):
            self.http_client.payload_parser.parse_trend_location_payload(res)

        if res.get("time_zone"):
            self.http_client.payload_parser.parse_time_zone_payload(res)

        return UserSettings(**res)

    def update_profile(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        image: Optional[File] = None,
        location: Optional[Union[Geo, str]] = None,
        profile_url: Optional[str] = None,
        profile_link_color: Optional[ID] = None,
    ) -> ClientAccount:
        """Updates the client profile information from the given arguments.

        Parameters
        ------------
        name: Optional[:class:`str`]
            The new name replacing the client's oldname. Note that this isn't going to update the username.
        description: Optional[:class:`str`]
            The new description that you want to replace with the old version.
        image: Optional[:class:`File`]
            The new profile image that you want to replace with the old version. Must be an instance of :class:`File`.
        location: Optional[:class:`Geo`]
            The new location you want to replace with the old version. Must be an instance of :class:`Geo` or the fullname of geo. You use :meth:`Geo.fullname` to get the fullname.
        profile_url: Optional[:class:`str`]
            URL associated with the profile. Will be prepended with http:// if not present.
        profile_link_color: Optional[:class:`str`]
            Sets a hex value that controls the color scheme of links used on the authenticating user's profile page on twitter.com. This must be a valid hexadecimal value, and may be either three or six characters (ex: F00 or FF0000 in string). If you specified integer instead of string, the process will use hex() function to change the int value to a hex value.

        Returns
        ---------
        :class:`ClientAccount`
            Returns a updated client's account object.


        .. versionadded:: 1.5.0
        """
        if image:
            path = image.path
            if isinstance(path, io.IOBase):
                self.http_client.request(
                    "POST",
                    "1.1",
                    "/account/update_profile_image.json",
                    files={"image": path.read(4 * 1024 * 1024)},
                    auth=True,
                )
            else:
                self.http_client.request(
                    "POST",
                    "1.1",
                    "/account/update_profile_image.json",
                    files={"image": open(path, "rb").read(4 * 1024 * 1024)},
                    auth=True,
                )

        if isinstance(profile_link_color, int):
            profile_link_color = hex(profile_link_color).replace("0x", "", 1)

        res = self.http_client.request(
            "POST",
            "1.1",
            "/account/update_profile.json",
            params={
                "name": name,
                "description": description,
                "location": location.fullname if isinstance(location, Geo) else location,
                "url": profile_url,
                "profile_link_color": str(profile_link_color),
            },
            auth=True,
        )
        data = self.http_client.payload_parser.parse_user_payload(res)
        updated_account = ClientAccount(data, http_client=self.http_client)
        self = updated_account
        return self

    def update_profile_banner(
        self,
        *,
        banner: File,
        width: int = 0,
        height: int = 0,
        offset_left: int = 0,
        offset_top: int = 0,
    ) -> None:
        """Updates the profile banner.

        Parameters
        ------------
        banner: :class:`File`
            The new banner to replace the old one. Must be an instance of :class:`File`.
        width: :class:`int`
            The width of the preferred section of the image being uploaded in pixels. Use with height , offset_left , and offset_top to select the desired region of the image to use.
        height: :class:`int`
            The height of the preferred section of the image being uploaded in pixels. Use with width , offset_left , and offset_top to select the desired region of the image to use.
        offset_left: :class:`int`
            The number of pixels by which to offset the uploaded image from the left. Use with height , width , and offset_top to select the desired region of the image to use.
        offset_top: :class:`int`
            The number of pixels by which to offset the uploaded image from the top. Use with height , width , and offset_left to select the desired region of the image to use.


        .. versionadded:: 1.5.0
        """
        path = banner.path

        if isinstance(path, io.IOBase):
            self.http_client.request(
                "POST",
                "1.1",
                "/account/update_profile_banner.json",
                params={
                    "width": width,
                    "height": height,
                    "offset_left": offset_left,
                    "offset_top": offset_top,
                },
                files={"banner": path.read(4 * 1024 * 1024)},
                auth=True,
            )
        else:
            self.http_client.request(
                "POST",
                "1.1",
                "/account/update_profile_banner.json",
                params={
                    "width": width,
                    "height": height,
                    "offset_left": offset_left,
                    "offset_top": offset_top,
                },
                files={"banner": open(path, "rb").read(4 * 1024 * 1024)},
                auth=True,
            )
        return None

    def remove_profile_banner(self):
        """Remove the user profile banner.


        .. versionadded:: 1.5.0
        """
        self.http_client.request("POST", "1.1", "/account/remove_profile_banner.json", auth=True)

    def fetch_message_history(self):
        """Returns all Direct Messages (both sent and received) within the last 30 days. Sorted in chronological order.


        .. versionadded:: 1.5.0
        """
        # TODO return a pagination object.
        from .message import DirectMessage  # Avoid circular import error.

        res = self.http_client.request("GET", "1.1", "/direct_messages/events/list.json", auth=True)

        updated_res = self.http_client.payload_parser.parse_message_to_pagination_data(res, None, self)

        return [DirectMessage(data, http_client=self.http_client) for data in updated_res.get("events")]
