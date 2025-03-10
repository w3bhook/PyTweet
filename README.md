<h2 align="center">Pytweet</h2>
<div>
<img src="https://img.shields.io/pypi/v/PyTweet?logo=pypi&style=plastic">  

<img src="https://img.shields.io/badge/code%20style-black-000000.svg">  

<img alt="PyPI - License" src="https://img.shields.io/pypi/l/PyTweet">

<img alt="Total Downloads" src="https://pepy.tech/badge/pytweet">

<img src="https://img.shields.io/github/commit-activity/m/PyTweet/PyTweet?color=turquoise&logo=github&logoColor=black">


<img src="https://img.shields.io/github/issues-pr/PyTweet/PyTweet?color=yellow&label=Pull%20Requests&logo=github&logoColor=black">


<img src="https://img.shields.io/discord/858312394236624957?color=blue&label=PyTweet&logo=discord">


<img src='https://readthedocs.org/projects/py-tweet/badge/?version=latest' alt='Documentation Status' />


<img src="https://img.shields.io/endpoint?url=https%3A%2F%2Ftwbadges.glitch.me%2Fbadges%2Fstandard">


<img src="https://img.shields.io/endpoint?url=https%3A%2F%2Ftwbadges.glitch.me%2Fbadges%2Fpremium">


<img src="https://img.shields.io/endpoint?url=https%3A%2F%2Ftwbadges.glitch.me%2Fbadges%2Fv2">

</div>
<br>
<br>
<p align="center">PyTweet is a Synchronous python API wrapper for twitter's api, Its filled with rich features and is very easy to use.</p>

## Installation

### Windows

```bash
py -m pip install PyTweet
```

### Linux/MacOS

```bash
python3 -m pip install PyTweet
```

## Usage

```py
import pytweet

client = pytweet.Client(
    "Your Bearer Token Here!!!", 
    consumer_key="Your consumer_key here", 
    consumer_secret="Your consumer_secret here", 
    access_token="Your access_token here", 
    access_token_secret="Your access_token_secret here",
) #if you dont have one make an application in https://apps.twitter.com

client.tweet("Hello world, Hello twitter!")
```

You can check in `examples` directory for more example code.

# Links

- [Documentation](https://py-tweet.readthedocs.io/en/latest/)

- [Support Server](https://discord.gg/XHBhg6A4jJ)

- [github](https://github.com/PyTweet/PyTweet)

- [Pypi](https://pypi.org/project/PyTweet)

# Contribute

You can Contribute or open an issue regarding this wrapper in [github](https://github.com/PyTweet/PyTweet)!

# Licence & Copyright

All files of this repo are protected by the [MIT](https://opensource.org/licenses/MIT) license given below.

```
The MIT License (MIT)

Copyright (c) 2021-present TheFarGG & TheGenocides

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
