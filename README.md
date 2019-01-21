# Wagtail Meeting Guide

Meeting Guide compatible Python package for [the Wagtail CMS](https://wagtail.io) on the [Django web framework](https://www.djangoproject.com).

*This is pre-alpha software, in active development!*

Wagtail Meeting Guide requires both Wagtail 2.0 and Django 2.0.

## Pre-Requisites

Using this package requires both the Wagtail CMS and Django. Wagtail and Django are fantastic for running your website, but require a developer. If you are new, I would recommend going through both the [Django](https://docs.djangoproject.com/en/dev/intro/tutorial01/) and [Wagtail](http://docs.wagtail.io/en/v2.4/getting_started/tutorial.html) tutorials before trying to use this package.

A Google Geocode API key is also required.

## Installation to Your Django Project

* Install with the command `pip install wagtail-meeting-guide`
* Add `meeting_guide` and `wagtailgmaps` to your `INSTALLED_APPS`.
* Add the following settings, including your Google Geocode API key:

* Run migrations: `python manage.py migrate meeting_guide`
* Load Meeting Guide's meeting types: `python manage.py loaddata meeting_guide_types.json`

## Configuration

* Enter the Wagtail CMS, and go to `Settings`, `Meeting Types`.
* Enter your Intergroup's code for each of the Meeting Guide Code Types
* Go to `Regions` and enter your regions; regions can have a parent, so you can nest them. For example, you could have `Philadelphia County` as a region with no parent, and `Center City` as a sub-region with `Philadelphia County` as the parent.

## Including the Meeting Guide in Your Django Template

The API end point for the locations and meetings you create in Wagtail has to be added to your site's root `urls.py`. Add a line like this:

```python
urlpatterns = [
    ...
    path("meeting-guide/", include("meeting_guide.urls")),
    ...
]
```

You can include the Meeting Guide within any Django Template. Here is an example:

```django+html
{% extends "base.html" %}

{% load meeting_guide %}

{% block content %}
    {% meeting_guide %}
{% endblock content %}
```

## Release Notes

### 0.1

## Maintainer

* Timothy Allen (https://github.com/FlipperPA/)
