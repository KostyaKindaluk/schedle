import pytest

from algorithm.initializer import PopulationInitializer
from algorithm.chromosome import Chromosome


@pytest.fixture
def input_data():
	return {
		"subjects": ["Math"],
		"groups": [
			{
				"name": "G1",
				"subjects": [{"subject": "Math", "lectures": 14, "practices": 14}]
			}
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
		"duration_weeks": 14,
		"desired_days_count": 5
	}


def test_initializer_builds_indices(input_data):
	initializer = PopulationInitializer(input_data)
	assert "Math" in initializer.lecturers_by_subject
	assert "Math" in initializer.practitioners_by_subject


def test_create_population_returns_chromosomes(input_data):
	initializer = PopulationInitializer(input_data)
	population = initializer.create_population(3)

	assert len(population) == 3
	assert isinstance(population[0], Chromosome)


def test_stochastic_round_returns_int(input_data):
	initializer = PopulationInitializer(input_data)
	value = initializer._stochastic_round(1.5)
	assert isinstance(value, int)


def test_select_teacher_returns_name(input_data):
	initializer = PopulationInitializer(input_data)
	teacher = initializer._select_teacher("Math", "lecture")
	assert isinstance(teacher, str)