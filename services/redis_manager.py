import json
import os

import redis


class RedisManager:

    def __init__(self):
        self.url = os.getenv(
            "REDIS_URL",
            "redis://localhost:6379/0"
        )

        self.client = redis.from_url(
            self.url,
            decode_responses=True
        )

    def ping(self):
        try:
            return self.client.ping()
        except Exception:
            return False

    def get(self, key):
        value = self.client.get(key)

        if value is None:
            return None

        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def set(self, key, value, expiration=None):
        if not isinstance(value, str):
            value = json.dumps(value)

        if expiration:
            return self.client.setex(
                key,
                expiration,
                value
            )

        return self.client.set(
            key,
            value
        )

    def delete(self, key):
        return bool(
            self.client.delete(key)
        )

    def exists(self, key):
        return bool(
            self.client.exists(key)
        )

    def increment(self, key, amount=1):
        return self.client.incrby(
            key,
            amount
        )

    def set_pixel_cooldown(
        self,
        room_code,
        user_id,
        seconds
    ):
        key = (
            f"cooldown:"
            f"{room_code}:"
            f"{user_id}"
        )

        return self.client.setex(
            key,
            seconds,
            "1"
        )

    def pixel_on_cooldown(
        self,
        room_code,
        user_id
    ):
        key = (
            f"cooldown:"
            f"{room_code}:"
            f"{user_id}"
        )

        return self.exists(key)

    def publish(self, channel, data):
        if not isinstance(data, str):
            data = json.dumps(data)

        return self.client.publish(
            channel,
            data
        )

    def room_key(self, room_code):
        return f"room:{room_code}"

    def players_key(self, room_code):
        return f"room:{room_code}:players"

    def get_room(self, room_code):
        return self.get(
            self.room_key(room_code)
        )

    def save_room(
        self,
        room_code,
        room
    ):
        return self.set(
            self.room_key(room_code),
            room
        )

    def delete_room(self, room_code):
        self.delete(
            self.room_key(room_code)
        )

        self.delete(
            self.players_key(room_code)
        )

    def add_player(
        self,
        room_code,
        user_id
    ):
        return self.client.sadd(
            self.players_key(room_code),
            str(user_id)
        )

    def remove_player(
        self,
        room_code,
        user_id
    ):
        return self.client.srem(
            self.players_key(room_code),
            str(user_id)
        )

    def player_count(self, room_code):
        return self.client.scard(
            self.players_key(room_code)
        )

    def player_exists(
        self,
        room_code,
        user_id
    ):
        return bool(
            self.client.sismember(
                self.players_key(room_code),
                str(user_id)
            )
        )


redis_manager = RedisManager()