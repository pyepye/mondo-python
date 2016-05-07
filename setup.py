import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='mondo',
    version='0.1.0',
    packages=find_packages('mondo'),
    package_dir={'': 'mondo'},
    description='Wrapper for the Mondo API',
    long_description=README,
    author='Matt Pye',
    author_email='pyematt@gmail.com',
    zip_safe=True,
    install_requires=['requests'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.4',
    ],
)
