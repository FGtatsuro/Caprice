import os

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        status = tox.cmdline(self.test_args)
        sys.exit(status)

version = '0.1'

setup(name='Caprice',
      version=version,
      description='JSON-resource manager',
      long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
      classifiers=[
          'Environment :: Web Environment',
          'Framework :: Flask',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
      ],
      keywords='Flask',
      author='Tatsuro Fujii',
      author_email='fujiistorage@gmail.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Flask',
          'Flask-DebugToolbar',
          'PasteDeploy',
          'jsonschema'
      ],
      # 'setup.py test' needs that virtualenv is installed in project.
      tests_require=[
          'tox'
      ],
      dependency_links=[
          'git+https://github.com/mitsuhiko/flask.git#egg=Flask'
      ],
      cmdclass={'test': Tox},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
