import subprocess


def test_django_project_check():
	result = subprocess.run(
		["python", "manage.py", "check"],
		capture_output=True,
		text=True
	)
	assert result.returncode == 0