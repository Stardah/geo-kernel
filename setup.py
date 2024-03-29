import setuptools

#with open('README.rst') as f:
#    readme = f.read()

setuptools.setup(
    name='geokernel',
    version='0.5.4.3',
    packages=['geokernel'],
    description='Geo command language kernel for Jupyter',
    long_description='...',
    author='Nikita Terlych',
    author_email='nikita_terlych@mail.ru',
    url='https://github.com/sterdah/geo-kernel',
    install_requires=[
        'jupyter_client', 'IPython', 'ipykernel', 'websocket_client'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    # data_files=[('geokernel', ['cmd.json']), ('.', 'config.txt')],
    package_data={'geokernel': ['cmd.json']},
    include_package_data=True
)
