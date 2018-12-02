# Camera Studio Web Application

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

Camera Studio Web Application is a camera item catalog which can be edited only authorized account by google oauth

# Prerequisites

  - `vagrant up` >> `vagrant ssh` for enabling virtual environment
  - `pip install -r requirements.txt` in order to install all required modules
  - If above pip command not working, do `source /bin/activate` in command line interface

# Features

  - Only authorized account by google can do CRUD function for web application

We can also implement in future:
  - Upload camera item's image for better description to user rather than just plain text
  - Add more third party authorization method like facebook, linkedin etc.
  - Add local authorization method

This application have purpose to practice build simple CRUD web application using 3rd party authorization tool like google oauth2 by [Udacity](https://www.udacity.com/)

> This work might not work for python2.7 by the python module's compatibility
> basically, it works with python3.7 (`usr/bin/python3.7`)

Below there's a simple implementation example which can enable python3.7 environment

### DB Schema

Camera Studio web application has few of Class(Table) within DB:

* [User] - `id`, `name`
* [Company] - `id`, `name`, `user_id`[User.id]
* [Camera] - `id`, `name`, `description`, `price`, `user_id`[User.id], `company_id`[Company.id]

### Simple Implementation

Camera studio webapplication requires few of python modules to run.

Install the dependencies and start the server.

```sh
$ cd camera-catalog
$ vagrant up
$ vagrant ssh
$ cd /camera-catalog
$ pip install -r requirements.txt
```

For python virtual environments...(without enabling vagrant virtual env)
`source /bin/activate` command has python3.7 setting itself!!

```sh
$ cd camera-catalog
$ source /bin/activate
$ deactivate (for deactivate virtual environment)
```

