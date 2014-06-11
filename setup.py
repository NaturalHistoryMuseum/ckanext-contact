from setuptools import setup, find_packages

version = '0.1'

setup(
	name='ckanext-contact',
	version=version,
	description='CKAN Extension providing Contact / Feedback form',
	classifiers=[],
	keywords='',
	author='Ben Scott',
	author_email='ben@benscott.co.uk',
	url='',
	license='',
    packages=find_packages(exclude=['tests']),
    namespace_packages=['ckanext', 'ckanext.contact'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[],
	entry_points=\
	"""
    [ckan.plugins]
    	contact=ckanext.contact.plugin:ContactPlugin
	""",
)