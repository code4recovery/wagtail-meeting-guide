from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="wagtail-meeting_guide",
    description="Meeting Guide compatible Python package for Django's Wagtail CMS: meetings, locations, and API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tim Allen",
    author_email="flipper@peregrinesalon.com",
    url="https://github.com/meeting-guide/wagtail-meeting-guide",
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    install_requires=[
        "wagtailgeowidget<=5.1",
        "django-mptt<0.14.0",
        "django-weasyprint==0.5.4",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 3.0",
        "Framework :: Wagtail",
        "Framework :: Wagtail :: 2",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
