import pytest

from algorithm.chromosome import Chromosome, TimeSlot
from algorithm.fitness import FitnessEvaluator


@pytest.fixture
def input_data():
	return {
		"groups": [
			{
				"name": "G1",
				"subjects": [
					{"subject": "Math", "lectures": 14, "practices": 14}
				]
			}
		],
		"desired_days_count": 5,
		"max_daily_slots": 4,
		"duration_weeks": 14
	}


def test_fitness_returns_float(input_data):
	chrom = Chromosome(groups=["G1"], max_daily_slots=4)
	evaluator = FitnessEvaluator(input_data)

	score = evaluator.evaluate(chrom)
	assert isinstance(score, float)


def test_teacher_conflict_penalty(input_data):
	chrom = Chromosome(groups=["G1", "G2"], max_daily_slots=4)

	slot1 = TimeSlot(group="G1", subject="Math", lesson_type="lecture", teacher="T1", is_empty=False)
	slot2 = TimeSlot(group="G2", subject="Math", lesson_type="lecture", teacher="T1", is_empty=False)

	chrom.set_slot("G1", 0, 0, slot1)
	chrom.set_slot("G2", 0, 0, slot2)

	evaluator = FitnessEvaluator(input_data)
	penalty = evaluator.evaluate(chrom)

	assert penalty > 0


def test_classroom_conflict_penalty(input_data):
	chrom = Chromosome(groups=["G1", "G2"], max_daily_slots=4)

	slot1 = TimeSlot(group="G1", subject="Math", lesson_type="lecture", classroom="101", is_empty=False)
	slot2 = TimeSlot(group="G2", subject="Math", lesson_type="lecture", classroom="101", is_empty=False)

	chrom.set_slot("G1", 1, 1, slot1)
	chrom.set_slot("G2", 1, 1, slot2)

	evaluator = FitnessEvaluator(input_data)
	penalty = evaluator.evaluate(chrom)

	assert penalty > 0