import enum
import logging
from typing import Dict

from pygame import Surface

from justkeepswimming.systems.clock import TickContext
from justkeepswimming.utilities.image import Frame, Image
from justkeepswimming.utilities.signal import Signal


class Keyframe:
    def __init__(self, timestamp: float, region: Frame) -> None:
        self.timestamp = timestamp
        self.region = region


class AnimationPriority(enum.Enum):
    RESERVED = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    NONE = 0


class KeyframeSequence:
    def __init__(self, keyframes: list[Keyframe]) -> None:
        self.keyframes = sorted(keyframes, key=lambda k: k.timestamp)
        self.duration = max(k.timestamp for k in self.keyframes)

    def reverse(self) -> "KeyframeSequence":
        return KeyframeSequence(
            [
                Keyframe(self.duration - k.timestamp, k.region)
                for k in reversed(self.keyframes)
            ]
        )


class Animation:
    def __init__(
        self,
        image: Image,
        priority: AnimationPriority,
        looped: bool,
        speed: float,
        sequence: KeyframeSequence,
    ) -> None:
        self.image = image
        self.priority = priority
        self.looped = looped
        self.speed = speed
        self.sequence = sequence


class AnimationType(enum.Enum):
    IDLE = enum.auto()
    WALK = enum.auto()
    REVERSE_WALK = enum.auto()
    ATTACK = enum.auto()
    HURT = enum.auto()
    DEATH = enum.auto()


class AnimationTrackState(enum.Enum):
    STOPPED = enum.auto()
    PLAYING = enum.auto()
    PAUSED = enum.auto()
    FINISHED = enum.auto()
    CANCELLED = enum.auto()


class AnimationTrack:
    def __init__(self, animator: "Animator", animation: Animation) -> None:
        self.animator = animator
        self.animation = animation

        self.priority = animation.priority
        self.looped = animation.looped
        self.speed = animation.speed

        self.state = AnimationTrackState.STOPPED
        self.time = 0.0

        self.frames: Dict[float, Surface] = {}

        self.on_playing = Signal()
        self.on_looped = Signal()
        self.on_finished = Signal()

        self.logger = logging.getLogger("AnimationTrack")

    async def load(self) -> None:
        for keyframe in self.animation.sequence.keyframes:
            surface = await keyframe.region.slice(self.animation.image)
            self.frames[keyframe.timestamp] = surface
            self.logger.debug(
                f"Loaded {surface.get_size()} frame at timestamp {keyframe.timestamp}"
            )

    async def play(self) -> None:
        if self.state == AnimationTrackState.PLAYING:
            return
        self.state = AnimationTrackState.PLAYING
        self.time = 0.0
        await self.on_playing.emit(self)

    async def stop(self) -> None:
        if self.state == AnimationTrackState.STOPPED:
            return
        self.state = AnimationTrackState.STOPPED
        self.time = 0.0

    async def update(self, delta_time: float) -> None:
        if self.state != AnimationTrackState.PLAYING:
            return

        self.time += delta_time * self.speed

        if self.time >= self.animation.sequence.duration:
            if self.looped:
                self.time %= self.animation.sequence.duration
                await self.on_looped.emit(self)
            else:
                self.time = self.animation.sequence.duration
                self.state = AnimationTrackState.FINISHED
                await self.on_finished.emit(self)

    async def get_current_frame(self) -> Surface | None:
        if not self.frames:
            return None

        keyframes = self.animation.sequence.keyframes
        for i in range(len(keyframes) - 1):
            if keyframes[i].timestamp <= self.time < keyframes[i + 1].timestamp:
                return self.frames[keyframes[i].timestamp]

        return self.frames[keyframes[-1].timestamp]


class Animator:
    def __init__(self) -> None:
        self.tracks: Dict[Animation, AnimationTrack] = {}
        self.animations: Dict[AnimationType, Animation] = {}
        self.logger = logging.getLogger("Animator")

    async def load_animation(
        self,
        animation_type: AnimationType,
        animation: Animation,
    ) -> AnimationTrack:
        if animation in self.tracks:
            return self.tracks[animation]

        track = AnimationTrack(self, animation)
        self.logger.debug(f"Loading animation track for {animation_type}")
        await track.load()

        self.animations[animation_type] = animation
        self.tracks[animation] = track
        return track

    async def get_active_track(self) -> AnimationTrack | None:
        playing = [
            t for t in self.tracks.values() if t.state == AnimationTrackState.PLAYING
        ]
        if not playing:
            return None
        return max(playing, key=lambda t: t.priority.value)

    async def get_current_frame(self) -> Surface | None:
        track = await self.get_active_track()
        if track is None:
            return None
        return await track.get_current_frame()

    async def update(self, tick: TickContext) -> None:
        for track in self.tracks.values():
            await track.update(tick.delta_time)
