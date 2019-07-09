from distutils.core import setup

#with open('README.rst') as f:
#    readme = f.read()

setup(
    name='geokernel',
    version='0.7',
    packages=['geokernel'],
    description='Geo command language kernel for Jupyter',
    long_description='...',
    author='Nikita Terlych',
    author_email='nikita_terlych@mail.ru',
    url='https://github.com/sterdah/geo-kernel',
    install_requires=[
        'jupyter_client', 'IPython', 'ipykernel', 'websocket'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)