import io
import os

from setuptools import setup
from setuptools.command.install import install

PTH_FILE = 'python_ls.pth'

with io.open('README.md', encoding='UTF-8') as fp:
    long_description = fp.read()


class install_with_pth(install):
    @property
    def target(self):
        return os.path.join(self.install_lib, PTH_FILE)

    def get_outputs(self):
        outputs = install.get_outputs(self) or []
        return outputs + [self.target]

    def run(self):
        ret = install.run(self)
        with open(PTH_FILE) as ifp:
            with open(self.target, 'w') as ofp:
                ofp.write(ifp.read())
        return ret


setup(
    name='python-ls',
    use_scm_version={'write_to': 'python_ls/_version.py'},
    setup_requires=['setuptools_scm'],
    packages=['python_ls'],
    data_files=[("", ["LICENSE"])],
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
    cmdclass={
        'install': install_with_pth,
    }
)
