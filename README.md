# Wagtail Meeting Guide

Meeting Guide compatible Python package for [the Wagtail CMS](https://wagtail.io) on the [Django web framework](https://www.djangoproject.com).

*This is pre-alpha software, in active development!*

Wagtail Meeting Guide requires both Wagtail 2.0 and Django 2.0.

## Installation to Your Django Project

* Install with the command `pip install wagtail-meeting-guide`
* Add `meeting_guide` to your `INSTALLED_APPS`.
* Run migrations: `python manage.py migrate meeting_guide`
* Load Meeting Guide's meeting types: `python manage.py loaddata meeting_guide_types.json`

## Configuration

* Enter the Wagtail CMS, and go to `Settings`, `Meeting Types`.
* Enter your Intergroup's code for each of the Meeting Guide Code Types
* Go to `Regions` and enter your regions; regions can have a parent, so you can nest them. For example, you could have `Philadelphia County` as a region with no parent, and `Center City` as a sub-region with `Philadelphia County` as the parent.

## Release Notes

### 0.1

## Maintainer

* Timothy Allen (https://github.com/FlipperPA/)
