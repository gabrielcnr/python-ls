import io

from setuptools import setup


with io.open('README.md', encoding='UTF-8') as fp:
    long_description = fp.read()


setup(
    name='python-ls',
    use_scm_version={'write_to': 'python_ls/_version.py'},
    setup_requires=['setuptools_scm'],
    packages=['python_ls'],
    data_files = [("", ["LICENSE"])],
    author='Gabriel Reis',
    author_email='gabrielcnr@gmail.com',
    description='A better replacement for Python dir() builtin function',
    long_description=long_description,
    long_description_content_type='text/markdown',

    license='MIT',
    keywords='python dir ls search attributes',
    url='http://github.com/gabrielcnr/python-ls',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
