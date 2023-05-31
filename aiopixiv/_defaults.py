__version__ = VERSION = "0.1.0"
"""Installed version of aiopixiv"""

API_HOST = "https://app-api.pixiv.net"
"""Pixiv API host"""

AUTH_HOST = "https://oauth.secure.pixiv.net"
"""Pixiv authentication platform host"""

CLIENT_ID = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
"""Client ID representing this API client (by default sourced from IOS app)"""

CLIENT_SECRET = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"
"""Client Secret representing this API client (by default sourced from the IOS app)"""

HASH_SECRET = "28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c"
"""Hash secret representing this API client (by default sourced from the IOS app)"""

USER_AGENT = f"aiopixiv/{__version__} (https://github.com/Nachtalb/aiopixiv)"
"""User Agent we identify us when connecting to Pixiv"""

LOGIN_REDIRECT_URL = f"{API_HOST}/web/v1/users/auth/pixiv/callback"
"""OAuth callback url during login process"""

LOGIN_URL = f"{API_HOST}/web/v1/login"
"""Login UI for the user"""

AUTH_TOKEN_URL = f"{AUTH_HOST}/auth/token"
"""URL for refreshing access tokens"""
