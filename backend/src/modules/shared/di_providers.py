import asyncio
import inspect
from contextvars import ContextVar
from dependency_injector import providers


class ScopedResource(providers.Resource):
    def __init__(self, provides: object | None = None, *args, **kwargs):
        super().__init__(provides, *args, **kwargs)
        self._scopes = ContextVar(f"scoped_resource_{id(self)}", default=None)
        self._current_shutdowner = None  # Добавляем свой атрибут для хранения shutdowner

    def _provide(self, args, kwargs):
        # Вызываем родительский метод для получения ресурса и shutdowner
        resource = super()._provide(args, kwargs)

        # Сохраняем shutdowner перед сбросом
        self._current_shutdowner = getattr(self, '_shutdowner', None)

        stack = self._scopes.get() or []
        stack.append((resource, self._current_shutdowner))
        self._scopes.set(stack)

        # Сбрасываем внутреннее состояние Resource
        self._resource = None
        self._shutdowner = None
        self._initialized = False

        return resource

    def shutdown(self):
        stack = self._scopes.get()
        if not stack:
            return

        resource, shutdowner = stack.pop()
        self._scopes.set(stack)

        async def _run():
            # Если ресурс - Future, ждем его завершения
            if isinstance(resource, asyncio.Future):
                obj = await resource
            else:
                obj = resource

            if shutdowner:
                result = shutdowner(obj)
                if inspect.isawaitable(result):
                    await result
                return

            # Если нет shutdowner, пробуем вызвать close
            close = getattr(obj, "close", None)
            if close:
                maybe = close()
                if inspect.isawaitable(maybe):
                    await maybe

        coro = _run()
        if inspect.isawaitable(coro):
            return asyncio.create_task(coro)
        return coro