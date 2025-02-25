from invoke import task

import app
import metrics

@task
def start_single_console(c):
    #starts a single worker for a single patient
    app.single_work() 

@task
def test_rules(c):
    #comprehensively tests the rules portion
    c.run("python -m pytest -rP tests_rules.py")

@task
def run_metrics(c):
    metrics.run_on_dataset()

@task 
def start_frontend(c):
    c.run("python server.py")

@task
def start_input_csv(c, input_string):
    app.single_work(input_csv = input_string)