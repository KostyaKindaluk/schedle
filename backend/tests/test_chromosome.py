import pytest
from algorithm.chromosome import TimeSlot, Chromosome


def test_timeslot_empty_to_dict():
	slot = TimeSlot()
	data = slot.to_dict()
	assert data == {"is_empty": True}


def test_timeslot_non_empty_to_dict():
	slot = TimeSlot(
		group="G1",
		subject="Math",
		lesson_type="lecture",
		teacher="T1",
		classroom="C1",
		is_empty=False
	)
	data = slot.to_dict()
	assert data["is_empty"] is False
	assert data["subject"] == "Math"


def test_timeslot_from_dict():
	data = {
		"is_empty": False,
		"group": "G1",
		"subject": "Math",
		"lesson_type": "lecture",
		"teacher": "T1",
		"classroom": "C1"
	}
	slot = TimeSlot.from_dict(data)
	assert slot.is_empty is False
	assert slot.subject == "Math"


def test_chromosome_initialization():
	chrom = Chromosome(groups=["G1"], max_daily_slots=4)
	slot = chrom.get_slot("G1", 0, 0)
	assert slot.is_empty is True


def test_set_and_get_slot():
	chrom = Chromosome(groups=["G1"], max_daily_slots=4)
	slot = TimeSlot(group="G1", subject="Math", lesson_type="lecture", is_empty=False)
	chrom.set_slot("G1", 0, 1, slot)

	fetched = chrom.get_slot("G1", 0, 1)
	assert fetched.subject == "Math"


def test_count_lessons():
	chrom = Chromosome(groups=["G1"], max_daily_slots=4)
	slot = TimeSlot(group="G1", subject="Math", lesson_type="lecture", is_empty=False)
	chrom.set_slot("G1", 0, 0, slot)

	lessons = chrom.count_lessons()
	assert lessons["G1"]["Math"]["lectures"] == 1