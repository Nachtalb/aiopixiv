# AIOPixiv: Asyncio-Based Python Library for Pixiv API

> ⚠ This tool is under strong development, only a subset of it's future
> functionality has been implemented yet.

**AIOPixiv** is an asyncio-based Python library for seamless integration with
the [Pixiv API](https://pixiv.net). It draws its inspiration from the
[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
and is based on the tried-and-tested functionality of
[pixivpy3](https://github.com/upbit/pixivpy).

This library is designed for efficient handling of multiple, concurrent API
requests to boost performance and optimize resource use. It is a go-to solution
for developers needing to interact with Pixiv's API, facilitating the
development of diverse applications, ranging from fanart crawlers to
sophisticated recommendation systems. Experience the enhanced performance and
capabilities of asyncio with Pixiv's API through AIOPixiv!

Use pip for installing:

```bash
pip install aiopixiv
```

## Login with user account

Easy login with username and password is not possible anymore. Use the included
authentication helper `pixiv_auth`. It will generate a `pixiv_auth.json` file
which can be put in the working directory of your application or at
`~/.pixiv_auth`. More information about the problem can be found here:
[pixivpy#158](https://github.com/upbit/pixivpy/issues/158).

Just run the following command after installing aiopixiv:

```bash
pixiv_auth
```

## Package Publishing Instructions

Follow these simple steps to publish your Poetry package. We recommend
publishing to the [test.pypi.org](https://test.pypi.org/) instance first, to
verify everything is working as expected.

This step only has to be done once:

```sh
# Configure test.pypi.org
poetry config repositories.testpypi https://test.pypi.org/legacy/
# Configure API Keys for both PyPI and TestPyPY
poetry config pypi-token.testpypi <testpypi_api_key>
poetry config pypi-token.pypi <pypi_api_key>
```

Now publish the new version:

```sh
# Adjust the package version at the top of the "pyproject.toml" file
vim pyproject.toml
# Build python packages to dist/ folder
poetry build
# Publish package to TestPyPi
poetry publish -r testpypi
# Checkout published package in a different environment
pip install --index-url https://test.pypi.org/simple/ <your_package_name>
# Once confirmed that everything works, publish to the real PyPi
poetry publish
```

## License

[GNU Lesser General Public License v3.0](https://github.com/Nachtalb/aiopixiv/tree/master/LICENSE)
