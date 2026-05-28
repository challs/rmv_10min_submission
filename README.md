# RMV 10 Minuten Guarantee Submission

> **⚠️ Archived / no longer functional.**
> RMV discontinued the 10-minute guarantee online refund process, so the form
> this script automated no longer exists. The repository is kept public for
> reference only — it is not maintained, dependencies are intentionally frozen
> at their last-known-working versions (see `Pipfile`), and the code will not
> run against the live RMV site. No fixes, dependency bumps, or security
> updates will be applied. Issues and PRs are disabled.

A script to automate the submission of RMV 10 minute guarantee requests

This is a little script I wrote to help for the submission of requests.
Given that I almost always travel the same route, and my personal details
and ticket does not normally change, I can fill in much of the details
with the same values each time.

## Installation

> The original `Pipfile.lock` has been removed so that GitHub no longer raises
> security alerts on long-frozen 2018-era pinned versions. The `Pipfile`
> remains as a record of the original dependency set (Python 3.7,
> `selenium 3.x`, `click >6.7`, etc.); a fresh `pipenv install` will resolve
> current versions which have not been tested with this code.

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

## Status

No further work planned — see the notice at the top of this README.
