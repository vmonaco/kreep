from setuptools import setup

setup(
    name='kreep',
    version='0.1',
    description='Keystroke recognition and entropy elimination program',
    url='http://github.com/vmonaco/kreep',
    author='Vinnie Monaco',
    author_email='contact@vmonaco.com',
    license='GPL',
    packages=['kreep'],
    package_dir={'kreep': 'kreep'},
    package_data={'kreep': ['kreep/data']},
    entry_points={
        'console_scripts': ['kreep = kreep.__main__:main']
    },
    install_requires=[
        'pandas',
        'dpkt',
        'scipy'
    ],
    include_package_data=True,
    zip_safe=False
)
