#!/usr/bin/env python
from setuptools import setup, find_packages

# https://github.com/pypa/sampleproject/blob/main/setup.py
setup(
    name='tfc-backend',
    version='0.0.1',
    license='Proprietary',
    setup_requires=["setuptools_scm>=6.0.1"],
    use_scm_version=True,
    classifiers=[  # https://pypi.org/classifiers/
        # How mature is this project? Common values are
        #   1 - Planning
        #   2 - Pre-Alpha
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        #   6 - Mature
        #   7 - Inactive
        'Development Status :: 1 - Planning',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        # 'Programming Language :: Python :: 3.10',
        'Framework :: Django'
    ],
    packages=find_packages(),
    python_requires='>=3.8, <4',
    include_package_data=True,
    install_requires=[
        'django',
        'django-cors-headers',
        'django-extensions',
        'django-filter',
        'djangorestframework',
        'djangorestframework-simplejwt==4.5.0',
        'PyJWT==1.7.1',
        'dj-database-url',
        'psycopg2-binary',
    ],
    #   extras_require={  # pip install sampleproject[dev]
    #       'dev': ['check-manifest'],
    #       'test': ['coverage'],
    #   },
    scripts=['manage.py'],
    project_urls={
        'Bug Reports': 'https://github.com/Smithienious/tfc-backend/issues',
    },
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    # entry_points={  # Optional
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
)
