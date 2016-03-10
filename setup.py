"""Setup for ctatxblock XBlock."""

import os
from setuptools import setup

def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                totalPath = os.path.relpath(os.path.join(dirname, fname), pkg)
                data.append(totalPath)

    return {pkg: data}


setup(
    name='ctatxblock-xblock',
    version='0.90',
    description='CTAT XBlock',
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
