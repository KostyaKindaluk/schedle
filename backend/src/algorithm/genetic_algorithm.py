import random
from typing import Dict, List, Callable, Optional

from .chromosome import Chromosome
from .initializer import PopulationInitializer
from .fitness import FitnessEvaluator
from .operators import GeneticOperators


class GeneticAlgorithm:
	def __init__(self, input_data: Dict, 
			population_size: int = 100,
			max_generations: int = 500,
			target_fitness: float = 0.0,
			checkpoint_interval: int = 5):
		self.input_data = input_data
		self.population_size = population_size
		self.max_generations = max_generations
		self.target_fitness = target_fitness
		self.checkpoint_interval = checkpoint_interval
		
		self.initializer = PopulationInitializer(input_data)
		self.evaluator = FitnessEvaluator(input_data)
		self.operators = GeneticOperators(input_data)
		
		self.population = []
		self.current_generation = 0
		self.best_chromosome = None
		self.best_fitness = float('inf')
		
		self.checkpoint_callback = None
	
	def set_checkpoint_callback(self, callback: Callable):
		self.checkpoint_callback = callback
	
	def initialize_population(self):
		self.population = self.initializer.create_population(self.population_size)
		self._evaluate_population()
		self.current_generation = 0
	
	def load_from_checkpoint(self, checkpoint_data: Dict):
		self.current_generation = checkpoint_data['generation']
		self.best_fitness = checkpoint_data['best_fitness']
		
		self.population = [
			Chromosome.from_dict(chrom_data) 
			for chrom_data in checkpoint_data['population']
		]
		
		self.best_chromosome = min(self.population, key=lambda x: x.fitness)
	
	def run(self) -> Dict:
		if not self.population:
			self.initialize_population()
		
		while self.current_generation < self.max_generations:
			self._evolve()
			self.current_generation += 1
			
			self._evaluate_population()
			
			current_best = min(self.population, key=lambda x: x.fitness)
			if current_best.fitness < self.best_fitness:
				self.best_fitness = current_best.fitness
				self.best_chromosome = current_best.copy()
			
			if self.current_generation % self.checkpoint_interval == 0:
				self._save_checkpoint()
			
			if self.current_generation % 10 == 0:
				print(f"Покоління {self.current_generation}: Найкраща оцінка = {self.best_fitness:.2f}")
			
			if self.best_fitness <= self.target_fitness:
				print(f"Досягнуто цільову оцінку {self.best_fitness} на поколінні {self.current_generation}")
				break
		
		return self._prepare_results()
	
	def _evolve(self):
		new_population = []
		
		elite_count = max(2, self.population_size // 10)
		sorted_pop = sorted(self.population, key=lambda x: x.fitness)
		new_population.extend([chrom.copy() for chrom in sorted_pop[:elite_count]])
		
		while len(new_population) < self.population_size:
			parent1 = self.operators.tournament_selection(self.population, tournament_size=5)
			parent2 = self.operators.tournament_selection(self.population, tournament_size=5)
			
			if random.random() < 0.85:
				child1, child2 = self.operators.crossover(parent1, parent2)
			else:
				child1 = parent1.copy()
				child2 = parent2.copy()
			
			if self.current_generation < 100:
				mutation_rate = 0.3
			elif self.current_generation < 300:
				mutation_rate = 0.2
			else:
				mutation_rate = 0.15
			
			self.operators.mutate(child1, mutation_rate=mutation_rate)
			self.operators.mutate(child2, mutation_rate=mutation_rate)
			
			new_population.append(child1)
			if len(new_population) < self.population_size:
				new_population.append(child2)
		
		self.population = new_population[:self.population_size]
	
	def _evaluate_population(self):
		for chromosome in self.population:
			if chromosome.fitness is None:
				chromosome.fitness = self.evaluator.evaluate(chromosome)
	
	def _save_checkpoint(self):
		if self.checkpoint_callback:
			checkpoint_data = {
				'generation': self.current_generation,
				'best_fitness': self.best_fitness,
				'population': [chrom.to_dict() for chrom in self.population]
			}
			self.checkpoint_callback(checkpoint_data)
	
	def _prepare_results(self) -> Dict:
		if self.best_chromosome is None:
			self.best_chromosome = min(self.population, key=lambda x: x.fitness)
		
		return {
			'schedule': self.best_chromosome.to_dict(),
			'fitness': self.best_chromosome.fitness,
			'generation': self.current_generation
		}
	
	def get_top_schedules(self, count: int = 3) -> List[Dict]:
		sorted_pop = sorted(self.population, key=lambda x: x.fitness)
		top_schedules = []
		
		for i, chrom in enumerate(sorted_pop[:count]):
			top_schedules.append({
				'rank': i + 1,
				'schedule': chrom.to_dict(),
				'fitness': chrom.fitness,
			})
		
		return top_schedules