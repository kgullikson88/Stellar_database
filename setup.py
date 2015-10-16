from setuptools import setup

requires = ['pandas',]

setup(name='stellar_data',
      version='0.1.0',
      description='A database and scripts that have stellar data for my sample.',
      author='Kevin Gullikson',
      author_email='kevin.gullikson@gmail.com',
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering :: Astronomy',
      ],
      packages=['stellar_data'],
      install_requires=requires)