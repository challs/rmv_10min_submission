# RMV 10 Minuten Guarantee Submission

A script to automate the submission of RMV 10 minute guarantee requests

This is a little script I wrote to help for the submission of requests.
Given that I almost always travel the same route, and my personal details
and ticket does not normally change, I can fill in much of the details
with the same values each time.

## Installation

Install the requirements:

```shell
pipenv install
```

## Configuration

Edit the settings in `rmv_config.ini`

### Personal section

Here you need to enter your name, email, address and phone number.

```ini
[personal]
first_name=Max
last_name=Mustmann
email=max@example.de
phone=069 12345678
street=Fritz-Str. 123
zip=6000
city=Frankfurt am Main
```

### Ticket section

This section contains details of your ticket to be used.

### Route sections

You can define a route name for each route you use, and then refer to
this name when you execute the script.

```ini
[route:work]
start=Frankfurt Hauptbahnhof
end=Darmstadt Hauptbahnhof
```

To use the route above, the submission command line would contain the parameter `-r work`.

## Execute

For help:

```shell
% python ./rmv_submission.py --help
Usage: rmv_submission.py [OPTIONS]

Options:
  -r, --route TEXT    Route name for the journey
  -d, --date TEXT     Departure date (dd.mm.yyyy)
  -t, --time TEXT     Departure time (hh:mm)
  --cancelled         train was cancelled
  -a, --arrival TEXT  arrival time (hh:mm)
  --submit            auto submit
  --help              Show this message and exit.
```

Example invocation:

```shell
python ./rmv_submission.py -r work -d 01.12.2018 -t 08:00 -a 09:20
```

### Logging

A log of submissions is written to `rmv.log` in the current directory.

## Outstanding items

* Make browser selection configurable
* Test and document further ticket options
* Tests
