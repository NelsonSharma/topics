from setuptools import setup, find_packages

setup(
    name =                      'topics',
    version =                   '1.0.0',
    url =                       'https://github.com/NelsonSharma/topics',
    author =                    'Nelson.S',
    author_email =              'mail.nelsonsharma@gmail.com',
    description =               'Flask-based web app for sharing files',
    packages =                  find_packages(include=['topics']),
    classifiers=                ['License :: OSI Approved :: MIT License'],
    #package_dir =               { '' : ''},
    install_requires =          ['Flask>=3.0.2', 'Flask-WTF>=1.2.1', 'waitress>=3.0.0'], # 'nbconvert>=7.16.2'
    include_package_data =      False,
    python_requires =           ">=3.8",
    
)   