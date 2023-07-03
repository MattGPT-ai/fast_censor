from setuptools import setup, find_packages


setup(
    name="fast-censor",
    version="0.2",
    description="A fast and flexible utility for censoring and filtering text",
    author="Matt Buchovecky",
    author_email="mbuchove@gmail.com",
    packages=find_packages(),
    package_data={
        "fast-censor": ["fast_censor/word_lists/*"],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
