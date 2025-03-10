from typing import Any, Dict, Optional, Tuple

from .enums import MediaType


class Media:
    """Represents a media attachment in a message."""

    __slots__ = (
        "_payload",
        "_url",
        "_preview_image_url",
        "_media_key",
        "_type",
        "_width",
        "_height",
    )

    def __init__(self, data: Dict[str, Any]):
        self._payload = data
        self._url = self._payload.get("url")
        self._preview_image_url = self._payload.get("preview_image_url")
        self._media_key = self._payload.get("media_key")
        self._type = MediaType(self._payload.get("type"))
        self._width, self._height = self._payload.get("width"), self._payload.get("height")

    @property
    def url(self) -> str:
        """:class:`str`: Returns the image's url, this method is only available if the media type is :class:`MediaType.photo`. If the media type is :class:`MediaType.video` consider using :class:`Media.preview_image_url`."""
        return self._url

    @property
    def preview_image_url(self) -> str:
        """:class:`str`: Returns the video's preview image url, This is only available when the media type is a :class:`MediaType.video` which is for video only."""
        return self._preview_image_url

    @property
    def key(self) -> str:
        """:class:`str`: Returns the media's key"""
        return self._media_key

    @property
    def type(self) -> MediaType:
        """:class:`str`: Returns the image's type in a :meth:`MediaType` object."""
        return self._type

    @property
    def width(self) -> Optional[int]:
        """Optional[:class:`int`]: Returns the image's width"""
        try:
            return int(self._width)
        except (ValueError, TypeError):
            return self._width

    @property
    def height(self) -> Optional[int]:
        """Optional[:class:`int`]: Returns the image's height"""
        try:
            return int(self._height)
        except (ValueError, TypeError):
            return self._height


class Hashtag:
    """Represents a hashtag in a message."""

    __slots__ = ("_payload", "_text", "_startpoint", "_endpoint")

    def __init__(self, data=Dict[str, Any]):
        self._payload = data
        self._text: Optional[str] = self._payload.get("text")
        self._startpoint, self._endpoint = self._payload.get("indices")

    @property
    def text(self) -> Optional[str]:
        """Optional[:class:`str`]: Returns the hashtag's text."""
        return self._text

    @property
    def points(self) -> Optional[Tuple]:
        """Optional[:class:`Tuple`]: Returns a tuple with the hashtag's startpoint and endpoint."""
        return self._startpoint, self._endpoint


class UserMention:
    """Represents a user mention in a message."""

    __slots__ = ("_payload", "_name", "_screen_name", "_id", "_startpoint", "_endpoint")

    def __init__(self, data=Dict[str, Any]):
        self._payload: Dict[str, Any] = data
        self._name: str = self._payload.get("name")
        self._screen_name: str = self._payload.get("screen_name")
        self._id: int = self._payload.get("id")
        self._startpoint, self._endpoint = self._payload.get("indices")

    @property
    def name(self) -> str:
        """:class:`str`: Returns the mention user's name."""
        return self._name

    @property
    def username(self) -> str:
        """:class:`str`: Returns the mention user's username."""
        return self._screen_name

    @property
    def id(self) -> int:
        """:class:`id`: Returns the mention user's id."""
        return int(self._id)

    @property
    def points(self) -> Optional[Tuple]:
        """Optional[:class:`Tuple`]: Returns a tuple with the mention's startpoint and endpoint."""
        return self._startpoint, self._endpoint


class Url:
    """Represents Url in a message."""

    __slots__ = (
        "_payload",
        "_url",
        "_display_url",
        "_expanded_url",
        "_startpoint",
        "_endpoint",
    )

    def __init__(self, data=Dict[str, Any]):
        self._payload: Dict[str, Any] = data
        self._url: str = self._payload.get("url")
        self._display_url: str = self._payload.get("display_url")
        self._expanded_url: str = self._payload.get("expanded_url")
        self._startpoint, self._endpoint = self._payload.get("indices")

    @property
    def url(self) -> str:
        """:class:`str`: Returns the message's url."""
        return self._url

    @property
    def display_url(self) -> str:
        """:class:`str`: Returns the message's display url"""
        return self._display_url

    @property
    def expanded_url(self) -> str:
        """:class:`str`: Returns the message's expanded url"""
        return self._expanded_url

    @property
    def points(self) -> Tuple:
        """Optional[:class:`Tuple`]: Returns a tuple with the url's startpoint and endpoint."""
        return self._startpoint, self._endpoint


class Symbol:
    """Represents a Symbol in a message."""

    __slots__ = ("_payload", "_text", "_startpoint", "_endpoint")

    def __init__(self, data=Optional[Dict[str, Any]]):
        self._payload: Dict[str, Any] = data
        self._text: str = self._payload.get("text")
        self._startpoint, self._endpoint = self._payload.get("indices")

    @property
    def text(self) -> str:
        """:class:`str`: Returns the symbol's text."""
        return self._text

    @property
    def points(self) -> Tuple:
        """Optional[:class:`Tuple`]: Returns a tuple with the url's startpoint and endpoint."""
        return self._startpoint, self._endpoint
