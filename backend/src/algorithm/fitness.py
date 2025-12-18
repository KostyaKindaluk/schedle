from typing import Dict
import math

from .chromosome import Chromosome


class FitnessEvaluator:
	UNDER_SCHEDULED_WEIGHT = 10.0
	OVER_SCHEDULED_WEIGHT = 5.0
	TEACHER_CONFLICT_BASE = 50.0
	CLASSROOM_CONFLICT_BASE = 40.0
	DAYS_MISMATCH_WEIGHT = 15.0
	WINDOW_BASE_WEIGHT = 8.0
	TEACHER_CONSISTENCY_WEIGHT = 30.0
	
	def __init__(self, input_data: Dict):
		self.groups_data = input_data['groups']
		self.desired_days = input_data['desired_days_count']
		self.max_daily_slots = input_data['max_daily_slots']
		self.duration_weeks = input_data['duration_weeks']
		
		self.required_lessons = {}
		for group in self.groups_data:
			self.required_lessons[group['name']] = {}
			for subj in group['subjects']:
				total_lectures = subj.get('lectures', 0)
				total_practices = subj.get('practices', 0)
				
				lectures_per_week = total_lectures / self.duration_weeks
				practices_per_week = total_practices / self.duration_weeks
				
				self.required_lessons[group['name']][subj['subject']] = {
					'lectures_min': math.floor(lectures_per_week),
					'lectures_max': math.ceil(lectures_per_week),
					'lectures_ideal': lectures_per_week,
					'practices_min': math.floor(practices_per_week),
					'practices_max': math.ceil(practices_per_week),
					'practices_ideal': practices_per_week,
				}
	
	def evaluate(self, chromosome: Chromosome) -> float:
		penalty = 0.0
		
		penalty += self._evaluate_lesson_counts(chromosome)
		penalty += self._evaluate_teacher_conflicts(chromosome)
		penalty += self._evaluate_classroom_conflicts(chromosome)
		penalty += self._evaluate_days_count(chromosome)
		penalty += self._evaluate_windows(chromosome)
		penalty += self._evaluate_teacher_consistency(chromosome)
		
		return penalty
	
	def _evaluate_lesson_counts(self, chromosome: Chromosome) -> float:
		penalty = 0.0
		
		weekly_lessons = chromosome.count_lessons()
		
		for group in chromosome.groups:
			if group not in self.required_lessons:
				continue
			for subject, required in self.required_lessons[group].items():
				weekly = weekly_lessons.get(group, {}).get(subject, {'lectures': 0, 'practices': 0})
				
				actual_lectures = weekly['lectures']
				if actual_lectures < required['lectures_min']:
					shortage = required['lectures_min'] - actual_lectures
					penalty += self.UNDER_SCHEDULED_WEIGHT * shortage
				elif actual_lectures > required['lectures_max']:
					excess = actual_lectures - required['lectures_max']
					penalty += self.OVER_SCHEDULED_WEIGHT * excess
				else:
					deviation = abs(actual_lectures - required['lectures_ideal'])
					if deviation > 0.5:
						penalty += 1.0 * deviation
				
				actual_practices = weekly['practices']
				if actual_practices < required['practices_min']:
					shortage = required['practices_min'] - actual_practices
					penalty += self.UNDER_SCHEDULED_WEIGHT * shortage
				elif actual_practices > required['practices_max']:
					excess = actual_practices - required['practices_max']
					penalty += self.OVER_SCHEDULED_WEIGHT * excess
				else:
					deviation = abs(actual_practices - required['practices_ideal'])
					if deviation > 0.5:
						penalty += 1.0 * deviation
		
		return penalty
	
	def _evaluate_teacher_conflicts(self, chromosome: Chromosome) -> float:
		penalty = 0.0
		
		for day in range(7):
			for slot_idx in range(self.max_daily_slots):
				teacher_load = {}
				
				for group in chromosome.groups:
					slot = chromosome.get_slot(group, day, slot_idx)
					if not slot.is_empty and slot.teacher:
						teacher_load[slot.teacher] = teacher_load.get(slot.teacher, 0) + 1
				
				for teacher, count in teacher_load.items():
					if count > 1:
						penalty += self.TEACHER_CONFLICT_BASE * (count - 1) ** 2
		
		return penalty
	
	def _evaluate_classroom_conflicts(self, chromosome: Chromosome) -> float:
		penalty = 0.0
		
		for day in range(7):
			for slot_idx in range(self.max_daily_slots):
				classroom_load = {}
				
				for group in chromosome.groups:
					slot = chromosome.get_slot(group, day, slot_idx)
					if not slot.is_empty and slot.classroom:
						classroom_load[slot.classroom] = classroom_load.get(slot.classroom, 0) + 1
				
				for classroom, count in classroom_load.items():
					if count > 1:
						penalty += self.CLASSROOM_CONFLICT_BASE * (count - 1) ** 2
		
		return penalty
	
	def _evaluate_days_count(self, chromosome: Chromosome) -> float:
		penalty = 0.0
		
		for group in chromosome.groups:
			active_days = set()
			
			for day in range(7):
				for slot_idx in range(self.max_daily_slots):
					slot = chromosome.get_slot(group, day, slot_idx)
					if not slot.is_empty:
						active_days.add(day)
						break
			
			actual_days = len(active_days)
			days_diff = abs(actual_days - self.desired_days)
			penalty += self.DAYS_MISMATCH_WEIGHT * days_diff
		
		return penalty
	
	def _evaluate_windows(self, chromosome: Chromosome) -> float:
		penalty = 0.0
		
		for group in chromosome.groups:
			for day in range(7):
				first_slot = None
				last_slot = None
				occupied_slots = []
				
				for slot_idx in range(self.max_daily_slots):
					slot = chromosome.get_slot(group, day, slot_idx)
					if not slot.is_empty:
						occupied_slots.append(slot_idx)
						if first_slot is None:
							first_slot = slot_idx
						last_slot = slot_idx
				
				if first_slot is not None and last_slot is not None and first_slot != last_slot:
					for slot_idx in range(first_slot, last_slot + 1):
						if slot_idx not in occupied_slots:
							penalty += self.WINDOW_BASE_WEIGHT
		
		return penalty
	
	def _evaluate_teacher_consistency(self, chromosome: Chromosome) -> float:
		penalty = 0.0
		
		for group in chromosome.groups:
			subject_teachers = {}
			
			for day in range(7):
				for slot_idx in range(self.max_daily_slots):
					slot = chromosome.get_slot(group, day, slot_idx)
					if not slot.is_empty:
						if slot.subject not in subject_teachers:
							subject_teachers[slot.subject] = {'lecture': set(), 'practice': set()}
						
						subject_teachers[slot.subject][slot.lesson_type].add(slot.teacher)
			
			for subject, types in subject_teachers.items():
				for lesson_type, teachers in types.items():
					if len(teachers) > 1:
						penalty += self.TEACHER_CONSISTENCY_WEIGHT * (len(teachers) - 1)
		
		return penalty