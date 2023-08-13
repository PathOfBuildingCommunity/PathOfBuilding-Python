from setuptools import setup
import os

# https://docs.python.org/3/distutils/setupscript.html
# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#scripts


def package_files(directory, extensions=''):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            if extensions:
                if filename.endswith(extensions):
                    paths.append(os.path.join('..', path, filename))
            else:
                paths.append(os.path.join('..', path, filename))
    return paths


# let's get some data files
data_files = package_files('src/tree_data')
data_files.extend(package_files('src/data', '.xml'))
data_files.extend(package_files('src/data', '.json'))

setup(
    name='PathOfBuilding-Python',
    version='0.38',
    package_dir={'PathOfBuilding': 'src'},
    packages=['PathOfBuilding', 'PathOfBuilding.dialogs', 'PathOfBuilding.ui', 'PathOfBuilding.views',
              'PathOfBuilding.widgets', 'PathOfBuilding.windows'],
    package_data={'PathOfBuilding': data_files},
    url='https://github.com/pHiney/PathOfBuilding-Python',
    license='',
    author='phiney',
    author_email='',
    description='Path Of Building written in Python',
    scripts=['PathOfBuilding.sh', 'PathOfBuilding.bat']
)
