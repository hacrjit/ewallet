from setuptools import setup, find_packages

setup(
    name='django-wallet-hacrjit',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=3.2',
        'djangorestframework',
    ],
    license='MIT',
    description='A plug-and-play Django wallet app',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hacrjit/django-wallet',
    author='Abhishek Hacrjit Singh',
    author_email='techabhi.me@gmail.com',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
    ],
)
