import threading
from django.apps import AppConfig


class SchedulingAppConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'scheduling_app'
	
	def ready(self):
		def restore_schedulings():
			import time
			time.sleep(2)
			
			from .models import Scheduling
			from algorithm.manager import get_manager
			
			in_progress = Scheduling.objects.filter(
				status='in_progress',
				checkpoint_generation__gt=0
			)
			
			if not in_progress.exists():
				return
			
			print(f"[Scheduling] Відновлення {in_progress.count()} незавершених розкладів...")
			
			manager = get_manager()
			
			for scheduling in in_progress:
				try:
					def make_save_callback(sched):
						def save_checkpoint(generation, population, fitness):
							sched.save_checkpoint(generation, population, fitness)
						return save_checkpoint
					
					def make_update_callback(sched):
						def update_status(new_status, result=None):
							if new_status == 'completed' and result:
								sched.save_results(
									schedules=[result['schedule']],
									fitness=result['fitness']
								)
							else:
								sched.status = new_status
								sched.save(update_fields=['status', 'updated_at'])
						return update_status
					
					input_data = scheduling.get_input_data()
					
					checkpoint_data = {
						'generation': scheduling.checkpoint_generation,
						'population': scheduling.checkpoint_population,
						'best_fitness': scheduling.checkpoint_best_fitness
					}
					
					manager.start_scheduling(
						scheduling_id=scheduling.id,
						input_data=input_data,
						save_callback=make_save_callback(scheduling),
						update_status_callback=make_update_callback(scheduling),
						checkpoint_data=checkpoint_data
					)
					
					print(f"[Scheduling] Відновлено розклад #{scheduling.id}: {scheduling.name}")
					
				except Exception as e:
					print(f"[Scheduling] Помилка відновлення #{scheduling.id}: {e}")
					scheduling.delete()
		
		thread = threading.Thread(target=restore_schedulings, daemon=True)
		thread.start()