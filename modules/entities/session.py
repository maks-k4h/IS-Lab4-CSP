from typing import Optional

from .room import Room
from .group import Group
from .teacher import Teacher
from .subject import Subject
from .time_slot import TimeSlot


class Session:
    def __init__(
            self,
            group: Group,
            subject: Subject,
            room: Optional[Room] = None,
            teacher: Optional[Teacher] = None,
            time_slot: Optional[TimeSlot] = None,
    ) -> None:
        self._room = room
        self._group = group
        self._subject = subject
        self._teacher = teacher
        self._time_slot = time_slot

    @property
    def group(self) -> Group:
        return self._group

    @property
    def subject(self) -> Subject:
        return self._subject

    @property
    def room(self) -> Optional[Room]:
        return self._room

    @room.setter
    def room(self, room: Optional[Room]):
        self._room = room

    @property
    def teacher(self) -> Optional[Teacher]:
        return self._teacher

    @teacher.setter
    def teacher(self, teacher: Optional[Teacher]):
        self._teacher = teacher

    @property
    def time_slot(self) -> Optional[TimeSlot]:
        return self._time_slot

    @time_slot.setter
    def time_slot(self, time_slot: Optional[TimeSlot]):
        self._time_slot = time_slot
