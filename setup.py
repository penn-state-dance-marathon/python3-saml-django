import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    # Start the description after the badges
    start = long_description.find('#')
    long_description = long_description[start:]

setuptools.setup(
    name="python3-django-saml",
    version="0.0.1",
    author="THON Technology",
    author_email="technology@thon.org",
    description="Implement SAML Single Sign-On in your Django project quickly and easily.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/penn-state-dance-marathon/python3-saml-django",
    packages=['django_saml'],
    install_requires=['python3-saml'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
    extras_require={
        'test': (
            'django>=1.11',
            'coverage',
            'pylint',
            'flake8',
            'flake8-docstrings',
            'isort',
            'codecov'
        ),
    },
)
