from contextlib import AbstractAsyncContextManager, AbstractContextManager
from dependency_injector import providers



import asyncio
import inspect
from contextvars import ContextVar
from dependency_injector import providers


class ScopedResource(providers.Resource):
    def __init__(self, provides, *args, **kwargs):
        super().__init__(provides, *args, **kwargs)
        self._scopes = ContextVar(f"scoped_resource_{id(self)}", default=None)

    def _provide(self, args, kwargs):
        resource = super()._provide(args, kwargs)
        stack = self._scopes.get() or []
        stack.append((resource, self._shutdowner))
        self._scopes.set(stack)
        
        # сбрасываем внутреннее состояние Resource, чтобы следующий вызов создал новый экземпляр
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
            obj = await resource if isinstance(resource, asyncio.Future) else resource
            if shutdowner:
                result = shutdowner(obj)
                if inspect.isawaitable(result):
                    await result
                return
            close = getattr(obj, "close", None)
            if close:
                maybe = close()
                if inspect.isawaitable(maybe):
                    await maybe

        coro = _run()
        if inspect.isawaitable(coro):
            return asyncio.create_task(coro)
        return coro