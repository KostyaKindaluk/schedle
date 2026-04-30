import random
from typing import List, Tuple

from .chromosome import Chromosome, TimeSlot


class GeneticOperators:
	def __init__(self, input_data):
		self.input_data = input_data
		self.classrooms = [c['name'] for c in input_data['classrooms']]
		self.max_daily_slots = input_data['max_daily_slots']
		self.duration_weeks = input_data['duration_weeks']
		
		self._build_teacher_indices()
	
	def _build_teacher_indices(self):
		self.lecturers_by_subject = {}
		self.practitioners_by_subject = {}
		
		for teacher in self.input_data['teachers']:
			for subj_info in teacher['subjects']:
				subject = subj_info['subject']
				
				if subj_info.get('is_lecturer', False):
					if subject not in self.lecturers_by_subject:
						self.lecturers_by_subject[subject] = []
					self.lecturers_by_subject[subject].append(teacher['name'])
				
				if subj_info.get('is_practitioner', False):
					if subject not in self.practitioners_by_subject:
						self.practitioners_by_subject[subject] = []
					self.practitioners_by_subject[subject].append(teacher['name'])
	
	def tournament_selection(self, population: List[Chromosome], 
						tournament_size: int = 3) -> Chromosome:
		tournament = random.sample(population, min(tournament_size, len(population)))
		return min(tournament, key=lambda x: x.fitness)
	
	def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Tuple[Chromosome, Chromosome]:
		child1 = parent1.copy()
		child2 = parent2.copy()
		
		for group in parent1.groups:
			crossover_point = random.randint(1, 6)
			
			for day in range(crossover_point, 7):
				for slot_idx in range(self.max_daily_slots):
					slot1 = parent1.get_slot(group, day, slot_idx)
					slot2 = parent2.get_slot(group, day, slot_idx)
					
					if not slot1.is_empty:
						new_slot1 = TimeSlot(
							group=slot1.group,
							subject=slot1.subject,
							lesson_type=slot1.lesson_type,
							teacher=slot1.teacher,
							classroom=slot1.classroom,
							is_empty=False
						)
						child2.set_slot(group, day, slot_idx, new_slot1)
					else:
						child2.set_slot(group, day, slot_idx, TimeSlot())
					
					if not slot2.is_empty:
						new_slot2 = TimeSlot(
							group=slot2.group,
							subject=slot2.subject,
							lesson_type=slot2.lesson_type,
							teacher=slot2.teacher,
							classroom=slot2.classroom,
							is_empty=False
						)
						child1.set_slot(group, day, slot_idx, new_slot2)
					else:
						child1.set_slot(group, day, slot_idx, TimeSlot())
		
		child1.fitness = None
		child2.fitness = None
		
		return child1, child2
	
	def mutate(self, chromosome: Chromosome, mutation_rate: float = 0.1):
		for group in chromosome.groups:
			if random.random() < mutation_rate:
				mutation_type = random.choice([
					'move', 'swap', 'change_teacher', 
					'change_classroom', 'add_lesson', 'remove_lesson'
				])
				
				if mutation_type == 'move':
					self._mutate_move_lesson(chromosome, group)
				elif mutation_type == 'swap':
					self._mutate_swap_lessons(chromosome, group)
				elif mutation_type == 'change_teacher':
					self._mutate_change_teacher(chromosome, group)
				elif mutation_type == 'change_classroom':
					self._mutate_change_classroom(chromosome, group)
				elif mutation_type == 'add_lesson':
					self._mutate_add_lesson(chromosome, group)
				elif mutation_type == 'remove_lesson':
					self._mutate_remove_lesson(chromosome, group)
		
		chromosome.fitness = None
	
	def _mutate_move_lesson(self, chromosome: Chromosome, group: str):
		occupied = []
		for day in range(7):
			for slot_idx in range(self.max_daily_slots):
				slot = chromosome.get_slot(group, day, slot_idx)
				if not slot.is_empty:
					occupied.append((day, slot_idx))
		
		if not occupied:
			return
		
		old_day, old_slot = random.choice(occupied)
		lesson = chromosome.get_slot(group, old_day, old_slot)
		
		attempts = 0
		while attempts < 30:
			new_day = random.randint(0, 6)
			new_slot = random.randint(0, self.max_daily_slots - 1)
			
			if chromosome.get_slot(group, new_day, new_slot).is_empty:
				new_timeslot = TimeSlot(
					group=lesson.group,
					subject=lesson.subject,
					lesson_type=lesson.lesson_type,
					teacher=lesson.teacher,
					classroom=lesson.classroom,
					is_empty=False
				)
				chromosome.set_slot(group, new_day, new_slot, new_timeslot)
				chromosome.set_slot(group, old_day, old_slot, TimeSlot())
				return
			
			attempts += 1
	
	def _mutate_swap_lessons(self, chromosome: Chromosome, group: str):
		occupied = []
		for day in range(7):
			for slot_idx in range(self.max_daily_slots):
				slot = chromosome.get_slot(group, day, slot_idx)
				if not slot.is_empty:
					occupied.append((day, slot_idx))
		
		if len(occupied) < 2:
			return
		
		pos1, pos2 = random.sample(occupied, 2)
		day1, slot1 = pos1
		day2, slot2 = pos2
		
		lesson1 = chromosome.get_slot(group, day1, slot1)
		lesson2 = chromosome.get_slot(group, day2, slot2)
		
		new_lesson1 = TimeSlot(
			group=lesson2.group,
			subject=lesson2.subject,
			lesson_type=lesson2.lesson_type,
			teacher=lesson2.teacher,
			classroom=lesson2.classroom,
			is_empty=False
		)
		new_lesson2 = TimeSlot(
			group=lesson1.group,
			subject=lesson1.subject,
			lesson_type=lesson1.lesson_type,
			teacher=lesson1.teacher,
			classroom=lesson1.classroom,
			is_empty=False
		)
		
		chromosome.set_slot(group, day1, slot1, new_lesson1)
		chromosome.set_slot(group, day2, slot2, new_lesson2)
	
	def _mutate_change_teacher(self, chromosome: Chromosome, group: str):
		occupied = []
		for day in range(7):
			for slot_idx in range(self.max_daily_slots):
				slot = chromosome.get_slot(group, day, slot_idx)
				if not slot.is_empty:
					occupied.append((day, slot_idx))
		
		if not occupied:
			return
		
		day, slot_idx = random.choice(occupied)
		lesson = chromosome.get_slot(group, day, slot_idx)
		
		if lesson.lesson_type == 'lecture':
			teachers = self.lecturers_by_subject.get(lesson.subject, [])
		else:
			teachers = self.practitioners_by_subject.get(lesson.subject, [])
		
		if teachers and len(teachers) > 1:
			new_teacher = random.choice([t for t in teachers if t != lesson.teacher])
			lesson.teacher = new_teacher
	
	def _mutate_change_classroom(self, chromosome: Chromosome, group: str):
		occupied = []
		for day in range(7):
			for slot_idx in range(self.max_daily_slots):
				slot = chromosome.get_slot(group, day, slot_idx)
				if not slot.is_empty:
					occupied.append((day, slot_idx))
		
		if not occupied:
			return
		
		day, slot_idx = random.choice(occupied)
		lesson = chromosome.get_slot(group, day, slot_idx)
		
		if self.classrooms:
			lesson.classroom = random.choice(self.classrooms)
	
	def _mutate_add_lesson(self, chromosome: Chromosome, group: str):
		group_data = None
		for g in self.input_data['groups']:
			if g['name'] == group:
				group_data = g
				break
		
		if not group_data:
			return
		
		if not group_data['subjects']:
			return
		
		subject_info = random.choice(group_data['subjects'])
		subject = subject_info['subject']
		
		lesson_type = random.choice(['lecture', 'practice'])
		
		empty_slots = []
		for day in range(7):
			for slot_idx in range(self.max_daily_slots):
				if chromosome.get_slot(group, day, slot_idx).is_empty:
					empty_slots.append((day, slot_idx))
		
		if not empty_slots:
			return
		
		day, slot_idx = random.choice(empty_slots)
		
		if lesson_type == 'lecture':
			teachers = self.lecturers_by_subject.get(subject, [])
		else:
			teachers = self.practitioners_by_subject.get(subject, [])
		
		if not teachers:
			return
		
		teacher = random.choice(teachers)
		classroom = random.choice(self.classrooms) if self.classrooms else "Аудиторія 1"
		
		new_slot = TimeSlot(
			group=group,
			subject=subject,
			lesson_type=lesson_type,
			teacher=teacher,
			classroom=classroom,
			is_empty=False
		)
		
		chromosome.set_slot(group, day, slot_idx, new_slot)
	
	def _mutate_remove_lesson(self, chromosome: Chromosome, group: str):
		occupied = []
		for day in range(7):
			for slot_idx in range(self.max_daily_slots):
				slot = chromosome.get_slot(group, day, slot_idx)
				if not slot.is_empty:
					occupied.append((day, slot_idx))
		
		if not occupied:
			return
		
		day, slot_idx = random.choice(occupied)
		chromosome.set_slot(group, day, slot_idx, TimeSlot())