from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from .attachments import Poll, Geo, File
from .entities import Media
from .enums import ReplySetting
from .constants import TWEET_FIELD, USER_FIELD, PINNED_TWEET_EXPANSION
from .metrics import TweetPublicMetrics
from .relations import RelationHide, RelationLike, RelationRetweet, RelationDelete
from .user import User
from .utils import time_parse_todt
from .message import Message
from .paginations import UserPagination

if TYPE_CHECKING:
    from .http import HTTPClient
    from .type import ID

__all__ = ("EmbedsImages", "Embed", "Tweet")


class EmbedsImages:
    """Represents the tweets embed images.

    .. versionadded: 1.1.3
    """

    __slots__ = "_payload"

    def __init__(self, data: Dict[str, Any]) -> None:
        self._payload = data

    def __repr__(self) -> str:
        return "EmbedsImages(url={0.url} width={0.width} height={0.height})".format(self)

    def __str__(self) -> str:
        return self.url

    @property
    def width(self) -> int:
        """:class:`int`: Return the image's width

        .. versionadded: 1.1.3
        """
        return int(self._payload.get("width"))

    @property
    def height(self) -> int:
        """:class:`int`: Return the image's height

        .. versionadded: 1.1.3
        """
        return int(self._payload.get("height"))

    @property
    def url(self) -> str:
        """:class:`str`: Return the image's url

        .. versionadded: 1.1.3
        """
        return self._payload.get("url")


class Embed:
    """Represents the embedded urls in a tweet.

    .. versionadded: 1.1.3
    """

    __slots__ = "_payload"

    def __init__(self, data: Dict[str, Any]):
        self._payload = data

    def __repr__(self) -> str:
        return "Embed(title={0.title} description={0.description} url={0.url})".format(self)

    def __str__(self) -> str:
        return self.url

    @property
    def title(self) -> str:
        """:class:`str`: Return the embed's title

        .. versionadded: 1.1.3
        """
        return self._payload.get("title")

    @property
    def description(self) -> str:
        """:class:`str`: Return the embed's description

        .. versionadded: 1.1.3
        """
        return self._payload.get("description")

    @property
    def start(self) -> int:
        """:class:`int`: Return the embed's url startpoint start

        .. versionadded: 1.1.3
        """
        return int(self._payload.get("start"))

    @property
    def end(self) -> int:
        """:class:`int`: Return the embed's url endpoint.

        .. versionadded: 1.1.3
        """
        return int(self._payload.get("end"))

    @property
    def url(self) -> str:
        """:class:`str`: Return the embed's url

        .. versionadded: 1.1.3
        """
        return self._payload.get("url")

    @property
    def expanded_url(self) -> str:
        """:class:`str`: Return the expanded url

        .. versionadded: 1.1.3
        """
        return self._payload.get("expanded_url")

    @property
    def display_url(self) -> str:
        """:class:`str`: Return the display url

        .. versionadded: 1.1.3
        """
        return self._payload.get("display_url")

    @property
    def unwound_url(self) -> str:
        """:class:`str`: Return the unwound url

        .. versionadded: 1.1.3
        """
        return self._payload.get("unwound_url")

    @property
    def images(self) -> Optional[List[EmbedsImages]]:
        """List[:class:`EmbedsImages`]: Return a list of Embed's Images

        .. versionadded:: 1.1.3
        """
        if self._payload.get("images"):
            return [EmbedsImages(data) for data in self._payload.get("images")]

        return None

    @property
    def status_code(self) -> int:
        """:class:`int`: Return the embed's url HTTP status code

        .. versionadded: 1.1.3
        """
        return int(self._payload.get("status"))


class Tweet(Message):
    """Represents a tweet message from Twitter.
    A Tweet is any message posted to Twitter which may contain photos, videos, links, and text.

    .. describe:: x == y

        Check if one tweet id is equal to another.


    .. describe:: x != y

        Check if one tweet id is not equal to another.


    .. describe:: str(x)

        Get the Tweet's text.


    .. versionadded:: 1.0.0
    """

    __slots__ = (
        "__original_payload",
        "_payload",
        "_includes",
        "tweet_metrics",
        "http_client",
        "deleted_timestamp",
    )

    def __init__(
        self,
        data: Dict[str, Any],
        *,
        deleted_timestamp: Optional[int] = None,
        http_client: Optional[HTTPClient] = None,
    ) -> None:
        self.__original_payload = data
        self._payload = data.get("data") or data
        self._includes = self.__original_payload.get("includes")
        self.tweet_metrics = TweetPublicMetrics(self._payload)
        self.http_client = http_client
        self.deleted_timestamp = deleted_timestamp
        super().__init__(self._payload.get("text"), self._payload.get("id"), 1)

    def __repr__(self) -> str:
        return "Tweet(text={0.text} id={0.id} author={0.author!r})".format(self)

    @property
    def author(self) -> Optional[User]:
        """Optional[:class:`User`]: Return a user (object) who posted the tweet.

        .. versionadded: 1.0.0
        """
        if self._includes and self._includes.get("users"):
            return User(self._includes.get("users")[0], http_client=self.http_client)
        return None

    @property
    def possibly_sensitive(self) -> bool:
        """:class`bool`: Return True if the tweet is possible sensitive to some users, else False.

        .. versionadded: 1.0.0
        """
        return self._payload.get("possibly_sensitive")

    @property
    def sensitive(self) -> bool:
        """:class`bool`: An alias to :meth:`Tweet.possibly_sensitive`.

        .. versionadded: 1.5.0
        """
        return self.possibly_sensitive

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Return a :class:`datetime.datetime` object when the tweet was created.

        .. versionadded: 1.0.0
        """
        if self._payload.get("timestamp", None):
            return datetime.datetime.fromtimestamp(int(self._payload.get("timestamp", None)) / 1000)
        return time_parse_todt(self._payload.get("created_at"))

    @property
    def deleted_at(self) -> Optional[datetime.datetime]:
        """Optional[:class:`datetime.datetime`]: Return a :class:`datetime.datetime` object when the tweet was deleted. Returns None when the tweet is not deleted.

        .. note::
            This property can only returns :class:`datetime.datetime` object through a tweet object from `on_tweet_delete` event.

        .. versionadded: 1.5.0
        """
        if not self.deleted_timestamp:
            return None
        return datetime.datetime.fromtimestamp(self.deleted_timestamp / 1000)

    @property
    def source(self) -> str:
        """:class:`str`: Return the source of the tweet. e.g if you post a tweet from a website, the source is gonna be 'Twitter Web App'

        .. versionadded: 1.0.0
        """
        return self._payload.get("source")

    @property
    def raw_reply_setting(self) -> str:
        """:class:`str`: Return the raw reply setting value. If everyone can replied, this method return 'Everyone'.

        .. versionadded: 1.0.0
        """
        return self._payload.get("reply_settings")

    @property
    def reply_setting(self) -> ReplySetting:
        """:class:`ReplySetting`: Return a :class:`ReplySetting` object with the tweet's reply setting. If everyone can reply, this method return :class:`replySetting.everyone`.

        .. versionadded: 1.3.5
        """
        return ReplySetting(self._payload.get("reply_settings"))

    @property
    def lang(self) -> str:
        """:class:`str`: Return the tweet's lang, if its english it return en.

        .. versionadded: 1.0.0
        """
        return self._payload.get("lang")

    @property
    def conversation_id(self) -> Optional[int]:
        """Optional[:class:`int`]: All replies are bind to the original tweet, this property returns the tweet's id if the tweet is a reply tweet else it returns None.

        .. versionadded: 1.0.0
        """
        try:
            return int(self._payload.get("conversation_id"))
        except ValueError:
            return None

    @property
    def url(self) -> Optional[str]:
        """Optional[:class:`str`]: Get the tweet's url.

        .. versionadded:: 1.1.0

        .. versionchanged:: 1.5.0
            Returns None if the author is invalid or the tweet doesn't have id.
        """
        try:
            return f"https://twitter.com/{self.author.username}/status/{self.id}"
        except TypeError:
            return None

    @property
    def mentions(self) -> Optional[List[str]]:
        """Optional[List[:class:`str`]]: Return the mentioned user's username.

        .. versionadded:: 1.1.3
        """
        if self._includes and self._includes.get("mentions"):
            return [user for user in self._includes.get("mentions")]
        return None

    @property
    def poll(self) -> Optional[Poll]:
        """:class:`Poll`: Return a Poll object with the tweet's poll.

        .. versionadded:: 1.1.0
        """
        if self._includes:
            if self._includes.get("polls"):
                data = self._includes.get("polls")[0]
                poll = Poll(
                    data.get("duration_minutes"),
                    id=data.get("id"),
                    voting_status=data.get("voting_status"),
                    end_date=data.get("end_datetime"),
                )
                for option in data.get("options"):
                    poll.add_option(**option)
                return poll
        return None

    @property
    def media(self) -> Optional[Media]:
        """List[:class:`Media`]: Return a list of media(s) in a tweet.

        .. versionadded:: 1.1.0
        """
        if self._includes and self._includes.get("media"):
            return [Media(img) for img in self._includes.get("media")]
        return None

    @property
    def embeds(self) -> Optional[List[Embed]]:
        """List[:class:`Embed`]: Return a list of Embedded url from that tweet

        .. versionadded:: 1.1.3
        """
        if self._payload.get("entities") and self._payload.get("entities").get("urls"):
            return [Embed(url) for url in self._payload.get("entities").get("urls")]
        return None

    @property
    def like_count(self) -> int:
        """:class:`int`: Return the total of likes in a tweet.

        .. versionadded: 1.1.0
        """
        return self.tweet_metrics.like_count

    @property
    def retweet_count(self) -> int:
        """:class:`int`: Return the total of retweetes in a tweet.

        .. versionadded: 1.1.0
        """
        return self.tweet_metrics.retweet_count

    @property
    def reply_count(self) -> int:
        """:class:`int`: Return the total of replies in a tweet.

        .. versionadded: 1.1.0
        """
        return self.tweet_metrics.reply_count

    @property
    def quote_count(self) -> int:
        """:class:`int`: Return the total of quotes in a tweet.

        .. versionadded: 1.1.0
        """
        return self.tweet_metrics.quote_count

    def like(self) -> Optional[RelationLike]:
        """Like the tweet.

        Returns
        ---------
        Optional[:class:`RelationLike`]
            This method returns a :class:`RelationLike` object.


        .. versionadded:: 1.2.0
        """
        my_id = self.http_client.access_token.partition("-")[0]

        payload = {"tweet_id": str(self.id)}
        res = self.http_client.request("POST", "2", f"/users/{my_id}/likes", json=payload, auth=True)

        return RelationLike(res)

    def unlike(self) -> Optional[RelationLike]:
        """Unlike the tweet.

        Returns
        ---------
        :class:`RelationLike`
            This method returns a :class:`RelationLike` object.


        .. versionadded:: 1.2.0
        """
        my_id = self.http_client.access_token.partition("-")[0]

        res = self.http_client.request("DELETE", "2", f"/users/{my_id}/likes/{self.id}", auth=True)

        return RelationLike(res)

    def retweet(self) -> RelationRetweet:
        """Retweet the tweet.

        Returns
        ---------
        :class:`RelationRetweet`
            This method returns a :class:`RelationRetweet` object.


        .. versionadded:: 1.2.0
        """
        my_id = self.http_client.access_token.partition("-")[0]
        res = self.http_client.request(
            "POST",
            "2",
            f"/users/{my_id}/retweets",
            json={"tweet_id": str(self.id)},
            auth=True,
        )

        return RelationRetweet(res)

    def unretweet(self) -> RelationRetweet:
        """Unretweet the tweet.

        Returns
        ---------
        :class:`RelationRetweet`
            This method returns a :class:`RelationRetweet` object.


        .. versionadded:: 1.2.0
        """
        my_id = self.http_client.access_token.partition("-")[0]

        res = self.http_client.request("DELETE", "2", f"/users/{my_id}/retweets/{self.id}", auth=True)

        return RelationRetweet(res)

    def delete(self) -> RelationDelete:
        """Delete the client's tweet.

        .. note::
            You can only delete the client's tweet.

        .. versionadded:: 1.2.0
        """
        res = self.http_client.request("DELETE", "2", f"/tweets/{self.id}", auth=True)

        try:
            self.http_client.tweet_cache.pop(self.id)
        except KeyError:
            pass

        return RelationDelete(res)

    def reply(
        self,
        text: str = None,
        *,
        file: Optional[File] = None,
        files: Optional[List[File]] = None,
        geo: Optional[Union[Geo, str]] = None,
        direct_message_deep_link: Optional[str] = None,
        reply_setting: Optional[Union[ReplySetting, str]] = None,
        exclude_reply_users: Optional[List[User, ID]] = None,
        media_tagged_users: Optional[List[User, ID]] = None,
    ) -> Optional[Tweet]:
        """Post a tweet to reply to the tweet present by the tweet's id. Returns a :class:`Tweet` object or :class:`Message` if the tweet is not found in the cache.

        .. note::
            Note that if the tweet is a retweet you cannot reply to that tweet, it might not raise an error but it will post the tweet has a normal tweet rather then a reply tweet and it ping the :class:`Tweet.author`.

        Parameters
        ------------
        text: :class:`str`
            The tweet's text, it will show up as the main text in a tweet.
        file: Optional[:class:`File`]
            Represents a single file attachment. It could be an image, gif, or video. It also have to be an instance of pytweet.File
        files: Optional[List[:class:`File`]]
            Represents multiple file attachments in a list. It could be an image, gif, or video. the item in the list must also be an instance of pytweet.File
        geo: Optional[Union[:class:`Geo`, :class:`str`]]
            The geo attachment, you can put an object that is an instance of :class:`Geo` or the place ID in a string.
        direct_message_deep_link: Optional[:class:`str`]
            The direct message deep link, It will showup as a CTA(call-to-action) with button attachment. Example of direct message deep link:
        reply_setting: Optional[Union[:class:`ReplySetting`, :class:`str`]]
            The reply setting that you can set to minimize users that can reply. If None is specified, the default is set to 'everyone' can reply.
        exclude_reply_users: Optional[List[:class:`User`]]
            A list of users or user ids to be excluded from the reply :class:`Tweet` thus removing a user from a thread, if you dont want to mention a reply with 3 mentions, You can use this argument and provide the user id you don't want to mention.
        media_tagged_users: Optional[List[:class:`User`]]
            A list of users or user ids being tagged in the Tweet with Media. If the user you're tagging doesn't have photo-tagging enabled, their names won't show up in the list of tagged users even though the Tweet is successfully created.

        Returns
        ---------
        Union[:class:`Tweet`, :class:`Message`]
            Returns a :class:`Tweet` object or :class:`Message` object if the tweet is not found in the cache.


        .. versionadded:: 1.2.5
        """
        return self.http_client.post_tweet(
            text,
            file=file,
            files=files,
            geo=geo,
            direct_message_deep_link=direct_message_deep_link,
            reply_setting=reply_setting,
            reply_tweet=self.id,
            exclude_reply_users=exclude_reply_users,
            media_tagged_users=media_tagged_users,
        )

    def hide(self) -> RelationHide:
        """Hide a reply tweet.

        Returns
        ---------
        :class:`RelationHide`
            This method returns a :class:`RelationHide` object.


        .. versionadded:: 1.2.5
        """
        res = self.http_client.request("PUT", "2", f"/tweets/{self.id}/hidden", json={"hidden": False}, auth=True)
        return RelationHide(res)

    def unhide(self) -> RelationHide:
        """Unhide a hide reply.

        Returns
        ---------
        :class:`RelationHide`
            This method returns a :class:`RelationHide` object.


        .. versionadded:: 1.2.5
        """
        res = self.http_client.request("PUT", "2", f"/tweets/{self.id}/hidden", json={"hidden": False}, auth=True)
        return RelationHide(res)

    def fetch_retweeters(self) -> Optional[UserPagination]:
        """Return users that retweeted the tweet.

        Returns
        ---------
        Optional[:class:`UserPagination`]
            This method returns a :class:`UserPagination` object.


        .. versionadded:: 1.1.3
        """
        res = self.http_client.request(
            "GET",
            "2",
            f"/tweets/{self.id}/retweeted_by",
            params={
                "expansions": PINNED_TWEET_EXPANSION,
                "user.fields": USER_FIELD,
                "tweet.fields": TWEET_FIELD,
            },
        )
        if not res:
            return []

        return UserPagination(
            res,
            endpoint_request=f"/tweets/{self.id}/retweeted_by",
            http_client=self.http_client,
            params={
                "expansions": PINNED_TWEET_EXPANSION,
                "user.fields": USER_FIELD,
                "tweet.fields": TWEET_FIELD,
            },
        )

    def fetch_likers(self) -> Optional[UserPagination]:
        """Return users that liked the tweet.

        Returns
        ---------
        Optional[:class:`UserPagination`]
            This method returns a :class:`UserPagination` object.


        .. versionadded:: 1.1.3
        """
        res = self.http_client.request(
            "GET",
            "2",
            f"/tweets/{self.id}/liking_users",
            params={
                "expansions": PINNED_TWEET_EXPANSION,
                "user.fields": USER_FIELD,
                "tweet.fields": TWEET_FIELD,
            },
        )

        if not res:
            return []

        return UserPagination(
            res,
            endpoint_request=f"/tweets/{self.id}/liking_users",
            http_client=self.http_client,
            params={
                "expansions": PINNED_TWEET_EXPANSION,
                "user.fields": USER_FIELD,
                "tweet.fields": TWEET_FIELD,
            },
        )

    def fetch_replied_user(self) -> Optional[User]:
        """Return the user that you reply with the tweet, a tweet count as reply tweet if the tweet startswith @Username or mention a user.

        Returns
        ---------
        Optional[:class:`User`]
            This method returns a :class:`User` object or :class:`NoneType`


        .. versionadded:: 1.1.3
        """
        return (
            self.http_client.fetch_user(
                int(self._payload.get("in_reply_to_user_id")),
                http_client=self.http_client,
            )
            if self._payload.get("in_reply_to_user_id")
            else None
        )
