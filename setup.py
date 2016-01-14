"""Setup for ctatxblock XBlock."""

import os
from setuptools import setup

print('setup ()')

def package_data(pkg, roots):
    print('package_data()')
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                totalPath = os.path.relpath(os.path.join(dirname, fname), pkg)
                # print 'File: %s ' % totalPath
                data.append(totalPath)

    return {pkg: data}


setup(
    name='ctatxblock-xblock',
    version='0.38',
    description='CTAT XBlock Template',
    packages=[
        'ctatxblock',
    ],
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'ctatxblock = ctatxblock:CTATXBlock',
        ]
    },
    package_data=package_data("ctatxblock", ["static", "public"]),
)

print('setup () done')
