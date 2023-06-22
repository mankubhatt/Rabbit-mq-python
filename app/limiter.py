from flask_limiter import Limiter, util

limiter = Limiter(key_func=util.get_remote_address)
