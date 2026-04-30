import pytest
import time

from algorithm.manager import SchedulingManager


def dummy_save_callback(*args, **kwargs):
	pass

def dummy_status_callback(*args, **kwargs):
	pass


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


def test_start_scheduling_registers_task():
	manager = SchedulingManager()

	manager.start_scheduling(
		scheduling_id=1,
		input_data=minimal_input_data(),
		save_callback=dummy_save_callback,
		update_status_callback=dummy_status_callback
	)

	time.sleep(0.5)

	assert manager.is_running(1) is True


def test_cannot_start_same_scheduling_twice():
	manager = SchedulingManager()

	manager.start_scheduling(
		1,
		minimal_input_data(),
		dummy_save_callback,
		dummy_status_callback
	)

	with pytest.raises(ValueError):
		manager.start_scheduling(
			1,
			minimal_input_data(),
			dummy_save_callback,
			dummy_status_callback
		)


def test_cancel_scheduling():
	manager = SchedulingManager()

	manager.start_scheduling(
		2,
		minimal_input_data(),
		dummy_save_callback,
		dummy_status_callback
	)

	manager.cancel_scheduling(2)
	assert manager.is_running(2) is True