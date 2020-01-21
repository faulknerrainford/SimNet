from setuptools import setup

classifiers = """
Development Status :: 3 - Alpha
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
Operating System :: OS Independent
Programming Language :: Python :: 3
""".strip().splitlines()

setup(
    name='Rvit Example',
    version='0.1',
    classifiers=classifiers,
    description='description of your app',
    url='',
    author='',
    author_email='',
    # namespace_packages=['rvit_example'],
    license='GPLv3',
    packages=['rvit_example'],
    install_requires=[
        'rvit @ git+https://github.com/matthew-egbert/rvit.git',
        'kivy @ git+https://github.com/kivy/kivy.git',
        'cython',
        'jinja2',
        'numpy',
        'pygame',
    ],
    entry_points={
        'gui_scripts': [
            'rvit_example = rvit_example:start',
        ]
    },
    include_package_data=True,
    zip_safe=False,
)
