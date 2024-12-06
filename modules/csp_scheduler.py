import copy
import enum
import random
from typing import Optional

import tqdm

from modules import entities


class SelectionStrategy(enum.Enum):
    GREEDY = 0
    RAIN = 1


class CSPScheduler:
    def __init__(
            self,
    ) -> None:
        pass

    def run(
            self,
            groups: list[entities.group.Group],
            rooms: list[entities.room.Room],
            teachers: list[entities.teacher.Teacher],
    ) -> entities.schedule.Schedule:
        # Unassigned variables — sessions for given subject at a given group
        unassigned_sessions = []
        for group in groups:
            for n_required, subject in group.required_subjects:
                for _ in range(n_required):
                    unassigned_sessions.append(entities.session.Session(
                        group=group,
                        subject=subject,
                    ))

        print(f'N sessions {len(unassigned_sessions)}')
        print(f'N rooms {len(rooms)}')
        print(f'N teachers {len(teachers)}')
        print(f'N groups {len(groups)}')

        schedule = self._try_fill_schedule(
            rooms=rooms,
            teachers=teachers,
            unassigned_sessions=unassigned_sessions,
            schedule_to_fill=entities.schedule.Schedule([])
        )
        assert schedule is not None
        return schedule

    def _try_fill_schedule(
            self,
            rooms: list[entities.room.Room],
            teachers: list[entities.teacher.Teacher],
            schedule_to_fill: entities.schedule.Schedule,
            unassigned_sessions: list[entities.session.Session],
    ) -> Optional[entities.schedule.Schedule]:
        if len(unassigned_sessions) == 0:
            return schedule_to_fill

        unassigned_session = unassigned_sessions[0]
        unassigned_sessions = unassigned_sessions[1:]

        def sort_teachers_for_session(teachers, inplace: bool):
            # sort according to a heuristic
            assert inplace

            def get_n_teacher_sessions(teacher: entities.teacher.Teacher) -> int:
                res = 0
                for session in schedule_to_fill.sessions:
                    if session.teacher.fullname == teacher.fullname:
                        res += 1
                return res

            teachers.sort(key=get_n_teacher_sessions)

        def sort_rooms(
                rooms: list[entities.room.Room],
                inplace: bool
        ):
            # sort according to a heuristic
            assert inplace

            def get_n_room_sessions(room: entities.room.Room) -> int:
                res = 0
                for session in schedule_to_fill.sessions:
                    if session.room.identifier == room.identifier:
                        res += 1
                return res

            rooms.sort(key=get_n_room_sessions)

        time_slots = [entities.time_slot.TimeSlot(day, time)
                      for day in [
                          entities.time_slot.TimeSlotDay.MONDAY,
                          entities.time_slot.TimeSlotDay.TUESDAY,
                          entities.time_slot.TimeSlotDay.WEDNESDAY,
                          entities.time_slot.TimeSlotDay.THURSDAY,
                          entities.time_slot.TimeSlotDay.FRIDAY,
                      ] for time in [
                          entities.time_slot.TimeSlotTime.FIRST,
                          entities.time_slot.TimeSlotTime.SECOND,
                          # entities.time_slot.TimeSlotTime.THIRD,
                          # entities.time_slot.TimeSlotTime.FOURTH,
                          # entities.time_slot.TimeSlotTime.FIFTH,
                          # entities.time_slot.TimeSlotTime.SIXTH,
                      ]]
        time_slots.sort(key=lambda x: len([s for s in schedule_to_fill.sessions if (s.time_slot.time.value, s.time_slot.day.value) == (x.time.value, x.day.value)]))

        # select a teacher
        new_session = copy.deepcopy(unassigned_session)
        sort_teachers_for_session(teachers, inplace=True)
        for teacher in teachers:
            if unassigned_session.subject.name not in [s.name for s in teacher.teachable_subjects]:
                continue
            # try to assign this teacher
            new_session.teacher = teacher
            # select time slot
            for time_slot in time_slots:
                new_session.time_slot = time_slot
                sort_rooms(rooms=rooms, inplace=True)
                for room in rooms:
                    if room.capacity < unassigned_session.group.size:
                        continue
                    new_session.room = room
                    # validate the setup
                    new_schedule = copy.deepcopy(schedule_to_fill)
                    new_schedule.sessions.append(new_session)
                    if not self._check_hard_constraints(new_schedule):
                        continue
                    # the setup is valid, recursive call
                    schedule = self._try_fill_schedule(rooms=rooms, teachers=teachers,
                                                       unassigned_sessions=unassigned_sessions,
                                                       schedule_to_fill=new_schedule)
                    if schedule is not None:
                        return schedule
        return None

    @staticmethod
    def _check_hard_constraints(schedule: entities.schedule.Schedule) -> bool:
        keys = set()
        for s in schedule.sessions:
            key = (s.time_slot.time.value, s.time_slot.day.value, s.group.name, s.room.identifier, s.teacher.fullname)
            if key in keys:
                return False
            keys.add(key)
        return True
