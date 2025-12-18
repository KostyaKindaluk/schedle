import random
from typing import List, Dict
from .chromosome import Chromosome, TimeSlot


class PopulationInitializer:
	def __init__(self, input_data: Dict):
		self.subjects = input_data['subjects']
		self.groups = input_data['groups']
		self.teachers = input_data['teachers']
		self.classrooms = input_data['classrooms']
		self.max_daily_slots = input_data['max_daily_slots']
		self.duration_weeks = input_data['duration_weeks']
		self.desired_days_count = input_data['desired_days_count']
		
		self._build_indices()
	
	def _build_indices(self):
		self.lecturers_by_subject = {}
		self.practitioners_by_subject = {}
		
		for teacher in self.teachers:
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
		
		self.classroom_names = [c['name'] for c in self.classrooms]
	
	def create_population(self, population_size: int) -> List[Chromosome]:
		population = []
		
		for _ in range(population_size):
			chromosome = self._create_random_chromosome()
			population.append(chromosome)
		
		return population
	
	def _create_random_chromosome(self) -> Chromosome:
		group_names = [g['name'] for g in self.groups]
		chromosome = Chromosome(group_names, self.max_daily_slots)
		
		for group_data in self.groups:
			group_name = group_data['name']
			
			lessons_to_schedule = []
			
			for subj_info in group_data['subjects']:
				subject = subj_info['subject']
				total_lectures = subj_info.get('lectures', 0)
				total_practices = subj_info.get('practices', 0)
				
				lectures_per_week = total_lectures / self.duration_weeks
				practices_per_week = total_practices / self.duration_weeks
				
				lectures_this_week = self._stochastic_round(lectures_per_week)
				practices_this_week = self._stochastic_round(practices_per_week)
				
				for _ in range(lectures_this_week):
					lessons_to_schedule.append({
						'subject': subject,
						'lesson_type': 'lecture'
					})
				
				for _ in range(practices_this_week):
					lessons_to_schedule.append({
						'subject': subject,
						'lesson_type': 'practice'
					})
			
			random.shuffle(lessons_to_schedule)
			
			available_days = list(range(7))
			random.shuffle(available_days)
			
			num_days = max(1, min(7, self.desired_days_count + random.randint(-1, 1)))
			selected_days = available_days[:num_days]
			selected_days.sort()
			
			day_index = 0
			for lesson in lessons_to_schedule:
				placed = False
				attempts = 0
				
				while not placed and attempts < 50:
					day = selected_days[day_index % len(selected_days)]
					slot = random.randint(0, self.max_daily_slots - 1)
					
					if chromosome.get_slot(group_name, day, slot).is_empty:
						teacher = self._select_teacher(
							lesson['subject'], 
							lesson['lesson_type']
						)
						
						classroom = random.choice(self.classroom_names)
						
						timeslot = TimeSlot(
							group=group_name,
							subject=lesson['subject'],
							lesson_type=lesson['lesson_type'],
							teacher=teacher,
							classroom=classroom,
							is_empty=False
						)
						
						chromosome.set_slot(group_name, day, slot, timeslot)
						placed = True
						day_index += 1
					
					attempts += 1
				
				if not placed:
					for day in range(7):
						for slot in range(self.max_daily_slots):
							if chromosome.get_slot(group_name, day, slot).is_empty:
								teacher = self._select_teacher(
									lesson['subject'], 
									lesson['lesson_type']
								)
								classroom = random.choice(self.classroom_names)
								
								timeslot = TimeSlot(
									group=group_name,
									subject=lesson['subject'],
									lesson_type=lesson['lesson_type'],
									teacher=teacher,
									classroom=classroom,
									is_empty=False
								)
								
								chromosome.set_slot(group_name, day, slot, timeslot)
								placed = True
								break
						if placed:
							break
		
		return chromosome
	
	def _stochastic_round(self, value: float) -> int:
		integer_part = int(value)
		fractional_part = value - integer_part
		
		if random.random() < fractional_part:
			return integer_part + 1
		return integer_part
	
	def _select_teacher(self, subject: str, lesson_type: str) -> str:
		if lesson_type == 'lecture':
			teachers = self.lecturers_by_subject.get(subject, [])
		else:
			teachers = self.practitioners_by_subject.get(subject, [])
		
		if not teachers:
			if self.teachers:
				return self.teachers[0]['name']
			return "Невідомий викладач"
		
		return random.choice(teachers)