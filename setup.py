from setuptools import setup

setup(
    name='stormssh-gui',
    version='0.3',
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
