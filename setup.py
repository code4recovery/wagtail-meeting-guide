from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="wagtail-meeting_guide",
    version="0.1.dev10",
    description="Meeting Guide compatible Python package for Django's Wagtail CMS: meetings, locations, and API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tim Allen",
    author_email="flipper@peregrinesalon.com",
    url="https://github.com/meeting-guide/wagtail-meeting-guide",
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        "wagtail>=2.0",
        "wagtailgeowidget==4.0.5",
        "django-mptt==0.10.0",
        "django-weasyprint==0.5.4",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Framework :: Wagtail",
        "Framework :: Wagtail :: 2",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
