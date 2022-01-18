import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='wordle-tournaments-client',
    version='0.0.1',
    author='',
    author_email='',
    description='Client for playing Wordle tournaments',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/jlym/wordle-tournaments-client',
    project_urls = {
        "Bug Tracker": "https://github.com/jlym/wordle-tournaments-client/issues"
    },
    license='MIT',
    packages=['toolbox'],
    install_requires=['requests'],
)
