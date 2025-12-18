import pytest

from algorithm.operators import GeneticOperators
from algorithm.chromosome import Chromosome, TimeSlot


def input_data():
	return {
		"groups": [
			{"name": "G1", "subjects": [{"subject": "Math"}]}
		],
		"teachers": [
			{
				"name": "T1",
				"subjects": [
					{"subject": "Math", "is_lecturer": True, "is_practitioner": True}
				]
			}
		],
		"classrooms": [{"name": "101"}],
		"max_daily_slots": 4,
		"duration_weeks": 14
	}


def test_tournament_selection_returns_chromosome():
	chrom1 = Chromosome(["G1"], 4)
	chrom2 = Chromosome(["G1"], 4)
	chrom1.fitness = 10
	chrom2.fitness = 5

	ops = GeneticOperators(input_data())
	selected = ops.tournament_selection([chrom1, chrom2])

	assert isinstance(selected, Chromosome)


def test_crossover_returns_two_children():
	parent1 = Chromosome(["G1"], 4)
	parent2 = Chromosome(["G1"], 4)

	ops = GeneticOperators(input_data())
	child1, child2 = ops.crossover(parent1, parent2)

	assert isinstance(child1, Chromosome)
	assert isinstance(child2, Chromosome)


def test_mutate_resets_fitness():
	chrom = Chromosome(["G1"], 4)
	chrom.fitness = 10

	ops = GeneticOperators(input_data())
	ops.mutate(chrom, mutation_rate=1.0)

	assert chrom.fitness is None