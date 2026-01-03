from contextlib import AbstractAsyncContextManager, AbstractContextManager
from dependency_injector import providers

class ScopedResource(providers.Provider):
    class _Handle(AbstractContextManager, AbstractAsyncContextManager):
        def __init__(self, factory, args, kwargs):
          self._factory = factory
          self._args = args
          self._kwargs = kwargs
          self._ctx = None
        
        def __enter__(self):
          self._ctx = self._factory(*self._args, **self._kwargs)
          if hasattr(self._ctx, "__enter__"):
              return self._ctx.__enter__()
          return self._ctx
        
        def __exit__(self, exc_type, exc, tb):
          if hasattr(self._ctx, "__exit__"):
              return self._ctx.__exit__(exc_type, exc, tb)
        
        async def __aenter__(self):
          self._ctx = self._factory(*self._args, **self._kwargs)
          if hasattr(self._ctx, "__aenter__"):
              return await self._ctx.__aenter__()
          return self._ctx
        
        async def __aexit__(self, exc_type, exc, tb):
          if hasattr(self._ctx, "__aexit__"):
              return await self._ctx.__aexit__(exc_type, exc, tb)

    def __init__(self, factory, *args, **kwargs):
      super().__init__()
      self._factory = providers.DelegatedFactory(factory, *args, **kwargs)
    
    def __call__(self, *args, **kwargs):
      return self._Handle(self._factory, args, kwargs)