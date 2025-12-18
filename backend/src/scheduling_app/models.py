from django.db import models
import json

from user_app.models import User


class Scheduling(models.Model):
	STATUS_CHOICES = [
		('pending', 'Очікує'),
		('in_progress', 'У процесі'),
		('completed', 'Завершено'),
	]
	
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedulings')
	name = models.CharField(max_length=255)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
	
	subjects = models.JSONField()
	groups = models.JSONField()
	teachers = models.JSONField()
	classrooms = models.JSONField()
	
	duration_weeks = models.IntegerField()
	max_daily_slots = models.IntegerField()
	desired_days_count = models.IntegerField()
	
	checkpoint_generation = models.IntegerField(default=0)
	checkpoint_population = models.JSONField(null=True, blank=True)
	checkpoint_best_fitness = models.FloatField(null=True, blank=True)
	
	best_schedules = models.JSONField(null=True, blank=True,)
	final_fitness = models.FloatField(null=True, blank=True)
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	completed_at = models.DateTimeField(null=True, blank=True)
	
	class Meta:
		ordering = ['-created_at']
		verbose_name = 'Розклад'
		verbose_name_plural = 'Розклади'
	
	def __str__(self):
		return f"{self.name} - {self.get_status_display()}"
	
	def get_input_data(self):
		return {
			'subjects': self.subjects,
			'groups': self.groups,
			'teachers': self.teachers,
			'classrooms': self.classrooms,
			'duration_weeks': self.duration_weeks,
			'max_daily_slots': self.max_daily_slots,
			'desired_days_count': self.desired_days_count,
		}
	
	def save_checkpoint(self, generation, population, best_fitness):
		self.checkpoint_generation = generation
		self.checkpoint_population = population
		self.checkpoint_best_fitness = best_fitness
		self.save(update_fields=['checkpoint_generation', 'checkpoint_population', 
				'checkpoint_best_fitness', 'updated_at'])
	
	def save_results(self, schedules, fitness):
		self.best_schedules = schedules
		self.final_fitness = fitness
		self.status = 'completed'
		from django.utils import timezone
		self.completed_at = timezone.now()
		self.save()