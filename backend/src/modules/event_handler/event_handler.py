import inspect
import logging
import types

logger = logging.getLogger(__name__)

class EventHandler:

    class Exceptions:
        """Custom error classes definition."""

        class EventNotAllowedError(Exception):
            """Will raise when tries to link a callback to unexistent event."""
            pass

    def __init__(self, *event_names, verbose=False, tolerate_callbacks_exceptions=False):
        """EventHandler initiazition recibes a list of allowed event names as arguments.

        Args:
            *event_names (str): Events names.
            verbose (bool): Set True to output warning messages.
            stream_output (IoStream): Set to send the output to specfic IO Stream object.
            tolerate_callbacks_exceptions (bool):
                False will raise any callback exception, stopping the execution.
                True will ignore any callbacks exceptions.
        """
        self.__events = {}
        self.verbose = verbose
        self.tolerate_exceptions = tolerate_callbacks_exceptions

        if event_names:
            for event in event_names:
                self.register_event(str(event))  # cast as str to be safe

        logger.info(f'{self.__str__()} has been init.') if self.verbose else None

    @property
    def events(self) -> dict:
        """Return events as dict."""
        return self.__events

    def clear_events(self) -> bool:
        """Clear all events."""
        self.__events = {}
        return True

    @property
    def event_list(self) -> set[str]:
        """Retun  list of regitered events."""
        return self.__events.keys()

    @property
    def count_events(self) -> int:
        """Return number of registered events."""
        return len(self.event_list)

    def is_event_registered(self, event_name: str) -> bool:
        """Return if an event is current registered.

        Args:
            event_name (str): The event you want to consult.
        """
        return event_name in self.__events

    def register_event(self, event_name: str) -> bool:
        """Register an event name.

        Args:
            event_name (str): Event name as string.
        """
        # logger.info('registering event %s %s', event_name, self.events)
        if self.is_event_registered(event_name):
            logger.info(f'Omiting event {event_name} registration, already implemented') if self.verbose else None
            return False

        self.__events[event_name] = []
        return True

    def unregister_event(self, event_name: str) -> bool:
        """Unregister an event name.

        Args:
            event_name (str): Remove an event from events dict.
        """
        if event_name in self.__events:
            del self.__events[event_name]
            return True
        logger.info(f'Omiting unregister_event. {event_name} is not implemented.') if self.verbose else None
        return False

    @staticmethod
    def is_callable(func: any) -> bool:
        """Return true if func is a callable variable.

        Args:
            func (callable): Object to validates as a callable.
        """
        return isinstance(func,
                          (types.FunctionType, types.BuiltinFunctionType, types.MethodType, types.BuiltinMethodType))

    def is_callback_in_event(self, event_name: str, callback: callable) -> bool:
        """Return if a given callback is already registered on the events dict.

        Args:
            event_name (str): The event name to look up for the callback inside.
            callback (callable): The callback function to check.
        """
        return callback in self.__events[event_name]

    def link(self, callback: callable, event_name: str) -> bool:
        """Link a callback to be executed on fired event..

        Args:
            callback (callable): function to link.
            event_name (str): The event that will trigger the callback execution.
        """

        if not self.is_callable(callback):
            logger.info(f'Callback not registered. Type {type(callback)} is not a callable function.') if self.verbose else None
            return False

        if not self.is_event_registered(event_name):
            raise CustomEventHandler.Exceptions.EventNotAllowedError(
                f'Can not link event {event_name}, not registered. Registered events are:'
                f' {", ".join(self.__events.keys())}. Please register event {event_name} before link callbacks.')

        if callback not in self.__events[event_name]:
            self.__events[event_name].append(callback)
            return True

        logger.info(f'Can not link callback {str(callback.__name__)}, already registered in {event_name} event.') if self.verbose else None
        return False

    def unlink(self, callback: callable, event_name: str) -> bool:
        """Unlink a callback execution fro especific event.

        Args:
            callback (callable): function to link.
            event_name (str): The event that will trigger the callback execution.
        """
        if not self.is_event_registered(event_name):
            logger.info(f'Can not unlink event {event_name}, not registered. Registered events '
                  f'are: {", ".join(self.__events.keys())}. '
                  f'Please register event {event_name} before unlink callbacks.')
            return False

        if callback in self.__events[event_name]:
            self.__events[event_name].remove(callback)
            return True

        logger.info(f'Can not unlink callback {str(callback.__name__)}, is not registered in '
              f'{event_name} event.') if self.verbose else None

        return False

    def __str__(self) -> str:
        """Return a string representation."""

        mem_address = str(hex(id(self)))

        event_related = \
            [f"{event}:[{', '.join([callback.__name__ for callback in self.__events[event]])}]" for event in
             self.__events]

        return f'<class {self.__class__.__name__} at ' \
            f'{mem_address}: {", ".join(event_related)}, verbose={self.verbose}, ' \
            f'tolerate_exceptions={self.tolerate_exceptions}>'

    def __repr__(self) -> str:
        """Return python object representation."""
        return self.__str__()

    async def fire(self, event_name: str, *args, **kwargs) -> bool:
        """Triggers all callbacks executions linked to given event."""
        all_ok = True
        for callback in self.__events.get(event_name, []):
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(*args, **kwargs)
                else:
                    callable(callback(*args, **kwargs))
            except Exception as e:
                if not self.tolerate_exceptions:
                    raise e
                else:
                    if self.verbose:
                        logger.info(f'WARNING: {str(callback.__name__)} produces an exception error.')
                        logger.info('Arguments')
                        logger.info(e)
                    all_ok = False
                    continue

        return all_ok
