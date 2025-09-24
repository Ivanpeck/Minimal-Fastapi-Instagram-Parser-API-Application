from datetime import datetime, timedelta
from typing import Dict, Any


# Кэш для хранения популярных данных
class PopularUsernameCache:
    def __init__(self, ttl_minutes: int = 5):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        self.access_count: Dict[str, int] = {}
        self.popular_threshold = 3  # Порог популярности

    def get(self, username: str) -> Dict[str, Any] | None:
        """Получить данные из кэша, если они еще актуальны"""
        if username in self.cache:
            cached_data = self.cache[username]
            if datetime.now() - cached_data['timestamp'] < self.ttl:
                return cached_data['data']
            else:
                # Удаляем просроченные данные
                del self.cache[username]
        return None

    def set(self, username: str, data: Dict[str, Any]):
        """Сохранить данные в кэш"""
        self.cache[username] = {
            'data': data,
            'timestamp': datetime.now()
        }

    def increment_access(self, username: str):
        """Увеличить счетчик обращений к username"""
        self.access_count[username] = self.access_count.get(username, 0) + 1

    def is_popular(self, username: str) -> bool:
        """Проверить, является ли username популярным"""
        return self.access_count.get(username, 0) >= self.popular_threshold
