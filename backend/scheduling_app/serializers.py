from rest_framework import serializers

from .models import Scheduling


class SchedulingCreateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Scheduling
		fields = [
			'name',
			'subjects',
			'groups',
			'teachers',
			'classrooms',
			'duration_weeks',
			'max_daily_slots',
			'desired_days_count',
		]
	
	def validate_subjects(self, value):
		if not isinstance(value, list) or len(value) == 0:
			raise serializers.ValidationError("Повинен бути хоча б один предмет")
		
		for subject in value:
			if not isinstance(subject, dict) or 'name' not in subject:
				raise serializers.ValidationError("Кожен предмет має мати поле 'name'")
			
			if not subject['name'] or not subject['name'].strip():
				raise serializers.ValidationError("Назва предмета не може бути пустою")
		
		return value
	
	def validate_groups(self, value):
		if not isinstance(value, list) or len(value) == 0:
			raise serializers.ValidationError("Повинна бути хоча б одна група")
		
		for group in value:
			if not isinstance(group, dict):
				raise serializers.ValidationError("Некоректний формат групи")
			
			if 'name' not in group:
				raise serializers.ValidationError("Група має мати поле 'name'")
			
			if not group['name'] or not group['name'].strip():
				raise serializers.ValidationError("Назва групи не може бути пустою")
			
			if 'subjects' not in group or not isinstance(group['subjects'], list):
				raise serializers.ValidationError("Група має мати список предметів")
			
			if len(group['subjects']) == 0:
				raise serializers.ValidationError(f"Група '{group['name']}' має мати хоча б один предмет")
			
			for subj in group['subjects']:
				if 'subject' not in subj:
					raise serializers.ValidationError("Предмет групи має мати поле 'subject'")
				
				if not subj['subject'] or not subj['subject'].strip():
					raise serializers.ValidationError("Назва предмета у групі не може бути пустою")
				
				if 'lectures' not in subj or 'practices' not in subj:
					raise serializers.ValidationError(
						"Предмет групи має мати поля 'lectures' та 'practices'"
					)
				
				if subj['lectures'] <= 0 and subj['practices'] <= 0:
					raise serializers.ValidationError(
						f"Предмет '{subj['subject']}' у групі '{group['name']}' має мати хоча б одну пару"
					)
		
		return value
	
	def validate_teachers(self, value):
		if not isinstance(value, list) or len(value) == 0:
			raise serializers.ValidationError("Повинен бути хоча б один викладач")
		
		for teacher in value:
			if not isinstance(teacher, dict):
				raise serializers.ValidationError("Некоректний формат викладача")
			
			if 'name' not in teacher:
				raise serializers.ValidationError("Викладач має мати поле 'name'")
			
			if not teacher['name'] or not teacher['name'].strip():
				raise serializers.ValidationError("Ім'я викладача не може бути пустим")
			
			if 'subjects' not in teacher or not isinstance(teacher['subjects'], list):
				raise serializers.ValidationError("Викладач має мати список предметів")
			
			if len(teacher['subjects']) == 0:
				raise serializers.ValidationError(f"Викладач '{teacher['name']}' має викладати хоча б один предмет")
			
			for subj in teacher['subjects']:
				if 'subject' not in subj:
					raise serializers.ValidationError("Предмет викладача має мати поле 'subject'")
				
				if not subj['subject'] or not subj['subject'].strip():
					raise serializers.ValidationError("Назва предмета у викладача не може бути пустою")
				
				if not subj.get('is_lecturer', False) and not subj.get('is_practitioner', False):
					raise serializers.ValidationError(
						f"Викладач '{teacher['name']}' має вміти викладати '{subj['subject']}' як лектор або практик"
					)
		
		return value
	
	def validate_classrooms(self, value):
		if not isinstance(value, list) or len(value) == 0:
			raise serializers.ValidationError("Повинна бути хоча б одна аудиторія")
		
		for classroom in value:
			if not isinstance(classroom, dict) or 'name' not in classroom:
				raise serializers.ValidationError("Кожна аудиторія має мати поле 'name'")
			
			if not classroom['name'] or not classroom['name'].strip():
				raise serializers.ValidationError("Назва аудиторії не може бути пустою")
		
		return value
	
	def validate_max_daily_slots(self, value):
		if value < 1 or value > 10:
			raise serializers.ValidationError("Кількість пар має бути від 1 до 10")
		return value
	
	def validate_desired_days_count(self, value):
		if value < 1 or value > 7:
			raise serializers.ValidationError("Кількість днів має бути від 1 до 7")
		return value

class SchedulingListSerializer(serializers.ModelSerializer):
	class Meta:
		model = Scheduling
		fields = [
			'id',
			'name',
			'status',
			'checkpoint_generation',
			'checkpoint_best_fitness',
			'final_fitness',
			'created_at',
			'updated_at',
			'completed_at',
		]
		read_only_fields = fields

class SchedulingDetailSerializer(serializers.ModelSerializer):
	class Meta:
		model = Scheduling
		fields = [
			'id',
			'name',
			'status',
			'subjects',
			'groups',
			'teachers',
			'classrooms',
			'duration_weeks',
			'max_daily_slots',
			'desired_days_count',
			'checkpoint_generation',
			'checkpoint_best_fitness',
			'best_schedules',
			'final_fitness',
			'created_at',
			'updated_at',
			'completed_at',
		]
		read_only_fields = [
			'id',
			'status',
			'checkpoint_generation',
			'checkpoint_best_fitness',
			'best_schedules',
			'final_fitness',
			'created_at',
			'updated_at',
			'completed_at',
		]