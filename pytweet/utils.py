from __future__ import annotations

import datetime
from typing import Any, Optional, Iterable, TYPE_CHECKING
from dateutil import parser

if TYPE_CHECKING:
    from .type import ID


def time_parse_todt(date: Optional[Any]) -> datetime.datetime:
    """Parse time return from twitter to datetime object!

    Returns
    ---------
    :class:`datetime.datetime`


    .. versionadded: 1.1.3
    """
    date = str(parser.parse(date))
    y, mo, d = date.split("-")
    h, mi, s = date.split(" ")[1].split("+")[0].split(":")

    return datetime.datetime(
        year=int(y),
        month=int(mo),
        day=int(d.split(" ")[0]),
        hour=int(h),
        minute=int(mi),
        second=int(s),
    )


def compose_tweet(text: Optional[str] = None) -> str:
    """Make a link that let's you compose a tweet

    Parameters
    ------------
    text: :class:`str`
        The pre-populated text in the tweet. If none specified the user has to write their own message.


    Returns
    ---------
    :class:`str`


    .. versionadded: 1.3.5
    """
    if text:
        text = text.replace(" ", "%20")
    return (
        "https://twitter.com/intent/tweet"
        if not text
        else f"https://twitter.com/intent/tweet" + f"?text={text}"
        if text
        else f"https://twitter.com/intent/tweet"
    )


def compose_user_action(user_id: str, action: str, text: str = None):
    """Make a link that let's you interact with a user with certain actions.

    Parameters
    ------------
    user_id: :class:`str`
        The user's id.
    action: :class:`str`
        The action you are going to perform to the user.
    text: :class:`str`
        The pre-populated text for the dm action.


    Returns
    ---------
    :class:`str`


    .. versionadded: 1.3.5
    """
    if action.lower() not in ("follow", "dm"):
        return TypeError("Action must be either 'follow' or 'dm'")
    if text:
        text = text.replace(" ", "%20")
    return (
        f"https://twitter.com/intent/user?user_id={user_id}"
        if action.lower() == "follow"
        else f"https://twitter.com/messages/compose?recipient_id={user_id}" + f"?text={text}"
        if text
        else f"https://twitter.com/messages/compose?recipient_id={user_id}"
    )


def compose_tweet_action(tweet_id: ID, action: str = None):
    """Make a link that let's you interact with a tweet with certain actions.

    Parameters
    ------------
    tweet_id: `ID`
        The tweet id you want to compose.
    action: :class:`str`
        The action that's going to get perform when you click the link.

    Returns
    ---------
    :class:`str`


    .. versionadded: 1.3.5
    """
    if action.lower() not in ("retweet", "like", "reply"):
        return TypeError("Action must be either 'retweet', 'like', or 'reply'")
    return (
        f"https://twitter.com/intent/{action}?tweet_id={tweet_id}"
        if action != "reply"
        else f"https://twitter.com/intent/tweet?in_reply_to={tweet_id}"
    )


def sift(iterable: Iterable, **conditions: Any):
    results = []
    for item in iterable:
        for condition, value in conditions.items():
            real_condition = condition.replace("_", "", 1)
            if condition.startswith("_") and not condition.startswith("__"):
                result = getattr(item, real_condition, None)
                if result:
                    result = result()
            else:
                result = getattr(item, condition, None)

            if not result:
                raise AttributeError(f"'{item.__class__.__name__}' object has no attribute '{real_condition}'")

            if result == value:
                results.append(result)

    return results
