import pytest
from algorithm.genetic_algorithm import GeneticAlgorithm


def minimal_input_data():
	return {
		'subjects': ['Math'],
		'groups': [{
			'name': 'G1',
			'subjects': [{
				'subject': 'Math',
				'lectures': 14,
				'practices': 14
			}]
		}],
		'teachers': [{
			'name': 'T1',
			'subjects': [{
				'subject': 'Math',
				'is_lecturer': True,
				'is_practitioner': True
			}]
		}],
		'classrooms': [{'name': '101'}],
		'max_daily_slots': 4,
		'duration_weeks': 14,
		'desired_days_count': 5
	}


def test_ga_initialization():
	ga = GeneticAlgorithm(minimal_input_data(), population_size=10, max_generations=1)
	assert ga.population_size == 10


def test_ga_run_returns_result():
	ga = GeneticAlgorithm(
		minimal_input_data(),
		population_size=10,
		max_generations=2
	)

	result = ga.run()

	assert "schedule" in result
	assert "fitness" in result
	assert "generation" in result


def test_get_top_schedules():
	ga = GeneticAlgorithm(
		minimal_input_data(),
		population_size=10,
		max_generations=1
	)
	ga.run()

	top = ga.get_top_schedules(count=2)
	assert len(top) == 2
	assert top[0]["rank"] == 1