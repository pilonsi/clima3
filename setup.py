from setuptools import setup

setup(name='clima3',
      version='0.0',
      description='AEMET OpenData Analyzer Tool',
      author='Jorge Fabregat López',
      author_email='jfabregat@protonmail.com',
      url='https://github.com/pilonsi/clima3',
      packages=['clima3'],
      install_requires=['requests', 'PyQt6']
)
