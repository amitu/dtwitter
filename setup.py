from setuptools import setup, find_packages

try:
    long_description=open('README.md', 'rt').read(),
except Exception:
    long_description=""

setup(
    name = "dtwitter",
    description = "django helper for twitter auth",
    long_description=long_description,

    version = "0.1.0",
    author = 'Amit Upadhyay',
    author_email = "upadhyay@gmail.com",

    url = 'https://github.com/amitu/dtwitter/',
    license = 'BSD',

    install_requires = ["tweepy"],
    packages = find_packages(),

    zip_safe = True
)
