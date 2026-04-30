import threading
from typing import Dict, Optional

from .genetic_algorithm import GeneticAlgorithm


class SchedulingManager:
	def __init__(self):
		self.active_tasks = {}
		self.lock = threading.Lock()
	
	def start_scheduling(self, scheduling_id: int, input_data: Dict, 
						save_callback, update_status_callback,
						checkpoint_data: Optional[Dict] = None):
		with self.lock:
			if scheduling_id in self.active_tasks:
				raise ValueError(f"Scheduling {scheduling_id} вже виконується")
			
			should_stop = {'value': False}
			self.active_tasks[scheduling_id] = {
				'thread': None,
				'algorithm': None,
				'should_stop': should_stop
			}
		
		try:
			algorithm = GeneticAlgorithm(
				input_data=input_data,
				population_size=100,
				max_generations=500,
				target_fitness=0.0,
				checkpoint_interval=5
			)
			
			def checkpoint_callback(checkpoint_data):
				save_callback(
					checkpoint_data['generation'],
					checkpoint_data['population'],
					checkpoint_data['best_fitness']
				)
			
			algorithm.set_checkpoint_callback(checkpoint_callback)
			
			if checkpoint_data:
				algorithm.load_from_checkpoint(checkpoint_data)
			
			def run_algorithm():
				try:
					update_status_callback('in_progress')
					
					result = self._run_with_cancellation(algorithm, should_stop)
					
					if not should_stop['value'] and result:
						self._save_final_results(
							scheduling_id, 
							result, 
							save_callback,
							update_status_callback
						)
					
				except Exception as e:
					print(f"Помилка при виконанні scheduling {scheduling_id}: {e}")
					import traceback
					traceback.print_exc()
				
				finally:
					with self.lock:
						if scheduling_id in self.active_tasks:
							del self.active_tasks[scheduling_id]
			
			thread = threading.Thread(target=run_algorithm, daemon=True)
			
			with self.lock:
				self.active_tasks[scheduling_id]['thread'] = thread
				self.active_tasks[scheduling_id]['algorithm'] = algorithm
			
			thread.start()
			
		except Exception as e:
			with self.lock:
				if scheduling_id in self.active_tasks:
					del self.active_tasks[scheduling_id]
			raise
	
	def _run_with_cancellation(self, algorithm: GeneticAlgorithm, 
		should_stop: Dict) -> Dict:
		if not algorithm.population:
			algorithm.initialize_population()
		
		while (algorithm.current_generation < algorithm.max_generations 
			and not should_stop['value']):
			
			algorithm._evolve()
			algorithm.current_generation += 1
			
			algorithm._evaluate_population()
			
			current_best = min(algorithm.population, key=lambda x: x.fitness)
			if current_best.fitness < algorithm.best_fitness:
				algorithm.best_fitness = current_best.fitness
				algorithm.best_chromosome = current_best.copy()
			
			if algorithm.current_generation % algorithm.checkpoint_interval == 0:
				algorithm._save_checkpoint()
			
			if algorithm.best_fitness <= algorithm.target_fitness:
				break
		
		if not should_stop['value']:
			return algorithm._prepare_results()
		
		return None
	
	def _save_final_results(self, scheduling_id: int, result: Dict,
		save_callback, update_status_callback):
		if result is None:
			return

		update_status_callback('completed', result)
	
	def cancel_scheduling(self, scheduling_id: int):
		with self.lock:
			if scheduling_id not in self.active_tasks:
				raise ValueError(f"Scheduling {scheduling_id} не виконується")
			
			self.active_tasks[scheduling_id]['should_stop']['value'] = True
	
	def is_running(self, scheduling_id: int) -> bool:
		with self.lock:
			return scheduling_id in self.active_tasks
	
	def get_status(self, scheduling_id: int) -> Optional[Dict]:
		with self.lock:
			if scheduling_id not in self.active_tasks:
				return None
			
			task = self.active_tasks[scheduling_id]
			algorithm = task['algorithm']
			
			return {
				'generation': algorithm.current_generation,
				'best_fitness': algorithm.best_fitness,
				'is_running': True
			}


_manager_instance = None

def get_manager() -> SchedulingManager:
	global _manager_instance
	if _manager_instance is None:
		_manager_instance = SchedulingManager()
	return _manager_instance