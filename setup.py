from setuptools import setup

setup(
    name='storm-gui',
    version='0.1',
    packages=['storm_gui'],
    url='http://github.com/emre/storm-gui',
    license='MIT',
    author='Emre Yilmaz',
    author_email='mail@emreyilmaz.me',
    description='a gui application form stormssh',
    install_requires=["stormssh", ],
    entry_points={
        'console_scripts': ['storm-gui = storm_gui.storm_gui:main',]
    }
)
