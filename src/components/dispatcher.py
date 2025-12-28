import logging
from pygame import Event as PygameEvent
import pygame

from src.utilities.signal import Signal

type EventType = int

class CustomEvent:
    def __init__(self, event_type: int) -> None:
        self.logger = logging.getLogger(__name__ + ".CustomEvent")
        self.event_type: EventType = event_type

    def dispatch(self) -> None:
        self.logger.info(f"Dispatching custom event: {self.event_type}")
        pygame.event.post(pygame.event.Event(self.event_type))

class Dispatcher:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__ + ".Dispatcher")
        self.event_signals: dict[EventType, Signal[PygameEvent]] = dict()
        self._custom_event_type_ptr: int = pygame.USEREVENT + 1

    def create_event(self) -> CustomEvent:
        event_type: EventType = self._custom_event_type_ptr
        self._custom_event_type_ptr += 1
        self.logger.info(f"Creating custom event type: {event_type}")
        return CustomEvent(event_type)

    def get_signal_for(self, event_type: EventType) -> Signal[PygameEvent]:
        signal = self.event_signals.get(event_type)
        if signal is None:
            self.logger.debug(f"Creating signal for event type: {event_type}")
            signal = Signal[PygameEvent]()
            self.event_signals[event_type] = signal
        return self.event_signals[event_type]

    async def _dispatch_event(self, event: PygameEvent) -> None:
        if event.type in self.event_signals:
            signal = self.event_signals[event.type]
            self.logger.debug(f"Dispatching {event} to {len(signal.connections)} connections.")
            await signal.emit(event)

    async def process_events(self) -> None:
        for event in pygame.event.get():
            await self._dispatch_event(event)
