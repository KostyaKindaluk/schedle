import random
from typing import List, Dict, Optional


class TimeSlot:
	def __init__(self, group=None, subject=None, lesson_type=None, 
				teacher=None, classroom=None, is_empty=True):
		self.group = group
		self.subject = subject
		self.lesson_type = lesson_type
		self.teacher = teacher
		self.classroom = classroom
		self.is_empty = is_empty
	
	def to_dict(self):
		if self.is_empty:
			return {'is_empty': True}
		return {
			'is_empty': False,
			'group': self.group,
			'subject': self.subject,
			'lesson_type': self.lesson_type,
			'teacher': self.teacher,
			'classroom': self.classroom,
		}
	
	@classmethod
	def from_dict(cls, data):
		if data.get('is_empty', True):
			return cls()
		return cls(
			group=data['group'],
			subject=data['subject'],
			lesson_type=data['lesson_type'],
			teacher=data['teacher'],
			classroom=data['classroom'],
			is_empty=False
		)

class Chromosome:
	def __init__(self, groups: List[str], max_daily_slots: int):
		self.groups = groups
		self.max_daily_slots = max_daily_slots
		self.timetables = {
			group: [[TimeSlot() for _ in range(max_daily_slots)] for _ in range(7)]
			for group in groups
		}
		self.fitness = None
	
	def to_dict(self):
		return {
			'groups': self.groups,
			'max_daily_slots': self.max_daily_slots,
			'timetables': {
				group: [
					[slot.to_dict() for slot in day]
					for day in timetable
				]
				for group, timetable in self.timetables.items()
			},
			'fitness': self.fitness
		}
	
	@classmethod
	def from_dict(cls, data):
		chromosome = cls(data['groups'], data['max_daily_slots'])
		chromosome.timetables = {
			group: [
				[TimeSlot.from_dict(slot_data) for slot_data in day]
				for day in timetable
			]
			for group, timetable in data['timetables'].items()
		}
		chromosome.fitness = data.get('fitness')
		return chromosome
	
	def get_slot(self, group: str, day: int, slot: int) -> TimeSlot:
		return self.timetables[group][day][slot]
	
	def set_slot(self, group: str, day: int, slot: int, timeslot: TimeSlot):
		self.timetables[group][day][slot] = timeslot
	
	def get_all_slots(self):
		slots = []
		for group in self.groups:
			for day_idx in range(7):
				for slot_idx in range(self.max_daily_slots):
					slot = self.get_slot(group, day_idx, slot_idx)
					if not slot.is_empty:
						slots.append((group, day_idx, slot_idx, slot))
		return slots
	
	def count_lessons(self):
		lessons = {}
		
		for group in self.groups:
			lessons[group] = {}
			for day in range(7):
				for slot_idx in range(self.max_daily_slots):
					slot = self.get_slot(group, day, slot_idx)
					if not slot.is_empty:
						if slot.subject not in lessons[group]:
							lessons[group][slot.subject] = {'lectures': 0, 'practices': 0}
						
						if slot.lesson_type == 'lecture':
							lessons[group][slot.subject]['lectures'] += 1
						elif slot.lesson_type == 'practice':
							lessons[group][slot.subject]['practices'] += 1
		
		return lessons
	
	def copy(self):
		new_chromosome = Chromosome(self.groups, self.max_daily_slots)
		for group in self.groups:
			for day in range(7):
				for slot_idx in range(self.max_daily_slots):
					original_slot = self.get_slot(group, day, slot_idx)
					if not original_slot.is_empty:
						new_slot = TimeSlot(
							group=original_slot.group,
							subject=original_slot.subject,
							lesson_type=original_slot.lesson_type,
							teacher=original_slot.teacher,
							classroom=original_slot.classroom,
							is_empty=False
						)
						new_chromosome.set_slot(group, day, slot_idx, new_slot)
		new_chromosome.fitness = self.fitness
		return new_chromosome