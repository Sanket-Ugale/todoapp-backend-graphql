#!/bin/bash

# Run Django tests with XML output
python manage.py test todo.tests --testrunner=xmlrunner.extra.djangotestrunner.XMLTestRunner --verbosity=2 --output-dir=test-reports

# Run the percentage calculator
python calculate_percentage.py
