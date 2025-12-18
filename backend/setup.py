import setuptools


if __name__ == "__main__":
	setuptools.setup(
		name='backend',
		packages=setuptools.find_packages(where='src'),
		package_dir={'': 'src'},
	)