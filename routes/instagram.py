from fastapi import FastAPI, HTTPException, Request

import uvicorn

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime

from utils.cache import PopularUsernameCache
from services.parser import username_data, UserNotFound, UserPrivate, ResourceBlocked

# Инициализация кэша
cache = PopularUsernameCache(ttl_minutes=5)  # TTL 5 минут

# Лимитер
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
limit_count = 10


@app.get('/api/instagram/{username}')
@limiter.limit(f"{limit_count}/minute")
def get_username_data(request: Request,username: str):
    print(f"{datetime.now()}: Запрос на поиск аккаунта: {username}")
    try:
        cache.increment_access(username)
        # Проверяем, популярен ли username и есть ли данные в кэше
        if cache.is_popular(username):
            cached_data = cache.get(username)
            if cached_data:
                print(f"{datetime.now()}: {username} находится в кэше. Выгружаем")
                return cached_data

        data = username_data(username)
        if cache.is_popular(username):
            print(f"{datetime.now()}: {username} добавлен в кэш")
            cache.set(username, data)
        else:
            print(f"{datetime.now()}: Парсим аккаунт {username}")

        return data

    except RateLimitExceeded as e:
        raise HTTPException(status_code=429, detail={"error": str(e)})

    except UserNotFound as e:
        print(f"{datetime.now()}: Ошибка: {e}")
        raise HTTPException(status_code=404, detail={"error": str(e)})

    except UserPrivate as e:
        print(f"{datetime.now()}: Ошибка: {e}")
        raise HTTPException(status_code=403, detail={"error": str(e)})

    except ResourceBlocked as e:
        print(f"{datetime.now()}: Ошибка: {e}")
        raise HTTPException(status_code=451, detail={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run("instagram:app", reload=True)