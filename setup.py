import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    # Start the description after the badges
    start = long_description.find('#')
    long_description = long_description[start:]

setuptools.setup(
    name="python3-saml-django",
    version="1.1.4",
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
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],
    python_requires='>=3',
    extras_require={
        'test': (
            'django',
            'coverage',
            'pylint',
            'flake8',
            'flake8-docstrings',
            'isort',
            'codecov'
        ),
    },
)
