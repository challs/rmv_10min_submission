#!/usr/bin/env python3
# coding: utf-8

import configparser
import sys
import time
from typing import Dict

import click

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class RMVConfig:
    CONFIG_FILE="rmv_config.ini"

    def __init__(self, filename: str=CONFIG_FILE):
        config = configparser.ConfigParser()
        config.read(filename)

        # Ticket details
        self.ticket = config['ticket']

        # Personal information
        self.personal = config['personal']

        salutation=self.personal.get("salutation")
        valid_salutations=('Herr', 'Frau')

        if salutation not in valid_salutations:
            click.echo("Salutation {} is not valid. It must be one of: {}".format(salutation, ",".join(valid_salutations)))
            sys.exit(-1)


        # Gerneral settings
        self.general = config['general']

        # Routes as a dict, key is route name
        self.routes = {
            s.split(':')[1]: config[s] for s in config.sections() if s.startswith('route:')}


class RMVRefund:

    url = 'https://www.rmv.de/elma/public/complaints/ten-min-step1.action'

    def __init__(self, config: RMVConfig, route: str, date: str, time: str, arrival_time, cancelled, submit=False):

        routeconfig = config.routes[route]
        self.start = routeconfig["start"]
        self.end = routeconfig["end"]
        self.date = date
        self.time = time
        self.arrival_time = arrival_time
        self.cancelled = cancelled

        self.config = config
        self.driver = None
        self.wait = None
        self.do_submit = submit
        self.confirmation_id = ''
        self.scheduled_departure = None
        self.scheduled_arrival = None

    def open(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 15) # This needs to represent the maximum waiting time for the RMV page
        self.driver.get(self.url)

        # Accept cookie bar
        self.wait_and_click('#cookie-bar a.cb-enable')

    def click(self, css):
        elem = self.driver.find_element_by_css_selector(css)
        elem.click()

    def wait_and_click(self, css):
        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css)))
        element.location_once_scrolled_into_view
        self.driver.find_element_by_css_selector(css).click()
        
    def input(self, css, value):
        elem = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css)))
        elem.location_once_scrolled_into_view
        elem.clear()
        elem.send_keys(value)

    def step1(self):
        # Choose the connection
        click.echo("Step 1: Choose the connection")

        self.input('input#startStation', self.start)

        self.wait_and_click("div#startResult > div.station")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div#startResult > div.station")))

        self.input('input#endStation', self.end)
        self.wait_and_click("div#endResult > div.station")
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div#endResult > div.station")))

        self.input('input#tripDate', self.date)
        self.input('input#tripTime', self.time)

        self.click('button[name="action:step1-next"]')

    def step2(self):
        click.echo("Step 2: Journey selection")

        route_group = self.driver.find_element_by_css_selector("#ten-min-step2 #routesTable div.route-group:first-of-type")
        journey_date = route_group.find_element_by_css_selector("ul.route-stop:first-child li.stop-date").text
        assert journey_date == self.date, "The journey date (%s) is not the same as the input date (%s)" % (journey_date, self.date)

        self.scheduled_departure = route_group.find_element_by_css_selector("ul.route-stop:first-child li.stop-departure").text
        self.scheduled_arrival = route_group.find_element_by_css_selector("ul.route-stop:last-child li.stop-arrival").text

        assert self.scheduled_departure == self.time, \
            "The journey departure time (%s) is not the same as the input time (%s)" % (self.scheduled_departure, self.start)

        elem = route_group.find_element_by_css_selector("ul.route-stop:last-child li.stop-helper a")

        # Scroll down the page because a click sometimes gets lost on the bottom of the page
        self.driver.find_element_by_css_selector("#cancelButton").location_once_scrolled_into_view
        elem.location_once_scrolled_into_view
        click.echo("Journey found. Date={} Departure={} Arrival={}".format(journey_date, self.scheduled_departure, self.scheduled_arrival))
        time.sleep(1) # To give me time to see the click
        elem.click()

    def step3(self):
        click.echo("Step 3: Arrival details")
        
        if self.cancelled:
            self.wait_and_click('label.widgetRadio[for=delayedOptionsOUTAGE')

        if self.arrival_time:
            self.input('input#actualArrival', self.arrival_time)
        else:
            click.echo("No arrival time - saying we did not travel")
            self.wait_and_click('#alternative')

        self.click('button#nextStep')

    def step4(self):
        tkt = self.config.ticket
        click.echo("Step 4: Ticket")
        
        # This depends on the ticket used
        self.wait_and_click('#ten-min-step4 #ticketType option[value="{}"]'.format(tkt["ticket_type"]))
        self.input('#ticketDetails input#selectedExpiryDate', tkt["expiry_date"])
        self.wait_and_click('#selectedCustomerGroup option[value="{}"]'.format(tkt["customer_group"]))
        self.wait_and_click('#selectedTicketDetail option[value="{}"]'.format(tkt["ticket_detail"]))
        self.wait_and_click('#selectedPriceCategory option[value="{}"]'.format(tkt["price_category"]))
        self.click('button#nextStep')

    def step5(self):
        data = self.config.personal
        click.echo("Step 5: Address")
        
        # This depends on who is claiming
        salutations={
            'Herr': 'MR',
            'Frau': 'MS',
        }
        salutation=salutations[data["salutation"]]
        self.click('select#formOfAddress option[value="{}"]'.format(salutation))
        self.input('input#firstName', data["first_name"])
        self.input('input#lastName', data["last_name"])
        self.input('input#email', data["email"])
        self.input('input#emailConfirmation', data["email"])
        self.input('input#phoneNo', data["phone"])
        self.input('input#streetNumber', data["street"])
        self.input('input#zip', data["zip"])
        self.input('input#city', data["city"])

        self.click('button#nextStep')

        if not self.config.general.get("guidelines_agreed"):
            accepted = click.confirm('Do you accept the guidelines?')
        
        if accepted:
            self.click('input#guidelinesAgreed')
        else:
            click.echo("Guidelines must be accepted first - aborting")
            sys.exit(-1)

    def runsteps(self):
        self.open()
        self.step1()
        self.step2()
        self.step3()
        self.step4()
        self.step5()

        if self.do_submit:
            submit = True
        else:
            submit = click.confirm('Do you want to continue?')

        if submit:
            self.submit()
        else:
            click.echo("Not submitting")

    def submit(self):
            click.echo("Submit")
        
            self.click('button#nextStep')
            css = '#ten-min-step7 div#embeddedContent p strong'
            longwait = WebDriverWait(self.driver, 60) # It can take a while to submit
            elem = longwait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css)))
            elem.location_once_scrolled_into_view
            vorgangstext = self.driver.find_element_by_css_selector(
                css).text

            self.confirmation_id = vorgangstext.split(' ')[-1]

            click.echo("Confirmation no: {}".format(self.confirmation_id))

    def dolog(self):
        msg = "{}: {} -> {}, {}-{}, actual arrival:{} cancelled={} vorgang={}".format(
            self.date,
            self.start, self.end,
            self.time, self.scheduled_arrival,
            self.arrival_time,
            self.cancelled,
            self.confirmation_id
        )   
        click.echo(msg)
        with open('rmv.log', 'a+') as f:
            f.write(msg + '\n')


@click.command()
@click.option('-r', '--route', type=click.STRING,
     help='Route name for the journey', prompt=True)
@click.option('-d', '--date', type=click.STRING, help='Departure date (dd.mm.yyyy)', prompt=True)
@click.option('-t', '--time', type=click.STRING, help='Departure time (hh:mm)', prompt=True)
@click.option('--cancelled', help='train was cancelled', is_flag=True, default=False)
@click.option('-a', '--arrival', type=click.STRING, help='arrival time (hh:mm)', prompt=True)
@click.option('--submit', is_flag=True, default=False, help='auto submit')
def journey(route, date, time, cancelled, arrival, submit):

    config = RMVConfig()

    rmv = RMVRefund(
        config,
        route,
        date,
        time,
        arrival,
        cancelled,
        submit,
    )

    rmv.runsteps()

    # Write results to logfile
    rmv.dolog()

if __name__ == '__main__':
    journey()
