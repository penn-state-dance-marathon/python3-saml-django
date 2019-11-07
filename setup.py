import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-saml-thon",
    version="0.0.1",
    author="THON Technology",
    author_email="technology@thon.org",
    description="A Django wrapper for the python OneLogin SAML package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/penn-state-dance-marathon/django_saml",
    packages=['django_saml'],
    install_requires=['python3-saml'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    extras_require={
        'test': (
            'django>=1.11',
            'coverage',
            'pylint',
            'flake8',
            'flake8-docstrings',
            'isort',
        ),
    },
)
