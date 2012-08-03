from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='flask_menu_pool',
      version=version,
      description="Create menus from YAML files in the flask web framework",
      long_description=open("README.md").read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='yaml menu flask',
      author='moesian',
      url='https://github.com/moesian/flask_menu_pool.git',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['flask_menu_pool'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )