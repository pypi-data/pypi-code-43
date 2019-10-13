from ehelply_bootstrapper.drivers.driver import Driver
import redis


class Redis(Driver):
    def setup(self):
        from ehelply_bootstrapper.utils.state import State
        redis.Redis(host=State.config.bootstrap.redis.host,
                    db=State.config.bootstrap.redis.db,
                    port=State.config.bootstrap.redis.port)

