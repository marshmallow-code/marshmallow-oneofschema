from setuptools import setup

EXTRAS_REQUIRE = {
    "tests": ["pytest", "mock"],
    "lint": ["flake8==3.9.2", "flake8-bugbear==21.4.3", "pre-commit~=2.7"],
}
EXTRAS_REQUIRE["dev"] = EXTRAS_REQUIRE["tests"] + EXTRAS_REQUIRE["lint"] + ["tox"]


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content


setup(
    name="marshmallow-oneofschema",
    version="3.0.0",
    description="marshmallow multiplexing schema",
    long_description=read("README.rst"),
    author="Maxim Kulkin",
    author_email="maxim.kulkin@gmail.com",
    maintainer="Steven Loria",
    maintainer_email="sloria1@gmail.com",
    url="https://github.com/marshmallow-code/marshmallow-oneofschema",
    packages=["marshmallow_oneofschema"],
    license="MIT",
    keywords=[
        "serialization",
        "deserialization",
        "json",
        "marshal",
        "marshalling",
        "schema",
        "validation",
        "multiplexing",
        "demultiplexing",
        "polymorphic",
    ],
    python_requires=">=3.6",
    install_requires=["marshmallow>=3.0.0,<4.0.0"],
    extras_require=EXTRAS_REQUIRE,
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
