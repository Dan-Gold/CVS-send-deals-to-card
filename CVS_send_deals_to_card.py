"""

Python 3.10.4


OVERVIEW:

	Neither CVS.com nor the app has an add all deals to card button and going through
	adding all of CVS's weekly deals to your card is a hassle. This tool automates the 
	process so all you need to do is run this tool.



Technical:

	selenium==4.1.3
	selenium-stealth==1.0.6
	undetected-chromedriver==2.1.1
	urllib3==1.26.5




OUTPUT:

	Nothing



USAGE:
	usage: CVS_send_deals_to_card.py [-h] -u USERNAME -p [PASSWORD] [-headless]

	This program is used to log the current user onto the CVS website, navigate to the current rewards
	page and add all of the current deals to the users card.

	options:
	  -h, --help     show this help message and exit
	  -headless      Run this application in a headless configuration.

	required arguments:
	  -u USERNAME    The email or username used to log into the website.
	  -p [PASSWORD]  The password used to log into the website. If none specified the program will ask
		             the user for a password via terminal input.



EXAMPLE:

	python3 CVS_send_deals_to_card.py -u username -p password

	python3 CVS_send_deals_to_card.py -u username



Revision Log:

Name                |  Revision  |  Date      |  Note
--------------------------------------------------------------------------------
Dan_Gold            |  1.1       | 05/20/2022 |  Initial release.
--------------------------------------------------------------------------------


https://stackoverflow.com/questions/65080685/usb-usb-device-handle-win-cc1020-failed-to-read-descriptor-from-node-connectio?answertab=scoredesc#tab-top
If you aren't having issues connecting to a device with WebUSB you can ignore these warnings. They are triggered by Chrome attempting to read properties of USB devices that are currently suspended.

"""

import argparse
import getpass
import random
import sys
import time


# URL Lib
import urllib
import urllib.request
import urllib.robotparser as urobot

# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains

# Selenium stealth
from selenium_stealth import stealth

# undetected _chromedriver
import undetected_chromedriver as uc


def argParse():
	""" This is the argparse for calling this script as main """

	parser = argparse.ArgumentParser(description = "This program is used to log the current user onto the CVS website, navigate to the current rewards page and add all of the current deals to the users card. ")

	required = parser.add_argument_group("required arguments")

	# Required arguments
	required.add_argument('-u', dest="username", help = "The email or username used to log into the website. ", required=True)
	required.add_argument('-p', action=password, dest="password", nargs='?', help = "The password used to log into the website. If none specified the program will ask the user for a password via terminal input. ", required=True)

	# Optional arguments
	#parser.add_argument('-w', dest="webWait", default=20, help = "Max amount of time to wait for a web page element to load", required=True)
	parser.add_argument('-headless', dest="headless", action='store_true', help = "Run this application in a headless configuration. ")

	args = parser.parse_args()

	return(args)



class password(argparse.Action):
	""" Callable for password argument. """

	def __call__(self, parser, namespace, values, option_string):
		if(values is None):
			values = getpass.getpass()

		setattr(namespace, self.dest, values)



class cvsDeals():
	""" Goes to the CVS website and adds all of the current deals to the users rewards card. """

	def __init__(self, username, password, webWait, headless):
		""" Object constructor for the class. """

		# Input
		self.userName = username # Username or email used to log into the website
		self.passWord = password # Password used to log into the website associated with the given username or email address
		self.webWait = webWait

		# Hard coded links for navigation
		# TODO: need to remove hard coded links and use on site navigation, running into issue where the site still knows that I am using a bot, even with selenium stealth and undetected chrome driver
		self.cvsMain = "https://www.cvs.com"
		self.loginURL = "https://www.cvs.com/retail-login/account/login/home?icid=cvsheader:signin&screenname=/"
		self.extraCare = "https://www.cvs.com/extracare/home?icid=cvsheader:extracare"
		self.robots = "https://www.cvs.com/robots.txt"

		# Webdriver setup
		options = self.driverOptions(headless)
		self.driver = uc.Chrome(options=options)

		stealth(self.driver,
				languages=["en-US", "en"],
				vendor="Google Inc.",
				platform="Win32",
				webgl_vendor="Intel Inc.",
				renderer="Intel Iris OpenGL Engine",
				fix_hairline=True,
				)

		self.robotsParse = self.setupURLChecker()
		random.seed(time.time())

	def driverOptions(self, headless):
		""" Sets up the desired options for the chrome driver. """

		options = uc.ChromeOptions()
		options.add_argument("start-maximized")
		options.add_experimental_option("excludeSwitches", ["enable-automation"])
		options.add_experimental_option('useAutomationExtension', False)

		if(headless):
			options.add_argument("--headless")

		return(options)

	def setupURLChecker(self):
		""" Sets up the robot file parser that will be used in checkCanBotURL(). """

		rp = urobot.RobotFileParser()
		rp.set_url(self.robots)
		rp.read()
		return(rp)

	def randomWaitTime(self, minI=4, maxI=10):
		""" Waits for a random amount of time to pass to not overload the website and
		hopefully to trick the website to thinking we are not a bot and to give the server
		a break from fast requests. 

		minI cannot be less than 4. Returns nothing. """

		if(minI < 4):
			minI = 4

		rand = random.uniform(minI, maxI)

		print("    Waiting for {0} seconds... Standby...".format(rand))

		time.sleep(rand)

	def checkCanBotURL(self, url):
		""" Checks the given URL to see if the program is allowed to bot the specific web page based on information from the website's robots.txt file. """

		print("Checking robots.txt")

		if(self.robotsParse.can_fetch("*", url)):
			print("    The web page: {0}   is allowed to be parsed and botted according to the robot.txt file on hand. ".format(url))
			return(True)
		else:
			print("    The web page: {0}   is NOT allowed to be parsed and botted according to the robot.txt file on hand. ".format(url))
			return(False)

	def login(self):
		""" Logs the user into the website if robots.txt allows. """

		print("Logging user into the website")

		# Setup wait object
		wait = WebDriverWait(self.driver, self.webWait)

		# On main page, need to click on login element and wait for the login page to laod
		el_signIn = self.driver.find_element(By.ID, "signInBtn")
		el_signIn.click()

		# Wait for email address text box
		emailBox = "/html/body/div/cvs-login/div/cvs-login-container/div/div/div/cvs-email-field/cvs-text-input/div/input"
		el_email_box = wait.until(EC.presence_of_element_located((By.XPATH, emailBox)))

		# Wait to not overload server
		self.randomWaitTime()

		# Click on email address text box
		el_email_box.click()

		# Wait to not overload server
		self.randomWaitTime()

		# Enter the given email address
		el_email_box.send_keys(self.userName)

		# Wait to not overload server
		self.randomWaitTime()

		# Click continue
		#				  /html/body/div[1]/cvs-login/div/cvs-login-container/div/div/div/cvs-email-field/button
		continueButton = "/html/body/div/cvs-login/div/cvs-login-container/div/div/div/cvs-email-field/button"
		el_continue = self.driver.find_element_by_xpath(continueButton)
		el_continue.click()

		# Wait to not overload server
		self.randomWaitTime()

		# Wait for password text box
		passBox = "/html/body/div/cvs-login/div/cvs-login-container/div/div/div/cvs-password-field/cvs-text-input/div/input[1]"
		el_pass_box = wait.until(EC.presence_of_element_located((By.XPATH, passBox)))

		# Wait to not overload server
		self.randomWaitTime()

		# Click on password text box
		el_pass_box.click()

		# Wait to not overload server
		self.randomWaitTime()

		# Enter password into text box
		el_pass_box.send_keys(self.passWord)

		# Wait to not overload server
		self.randomWaitTime()

		# Click on sign in box
		signIn = "/html/body/div/cvs-login/div/cvs-login-container/div/div/div/cvs-password-field/button"
		el_continue = self.driver.find_element_by_xpath(signIn)
		el_continue.click()

		# Once clicked on sign in, website will redirect to main page

		# TODO: add a check to make sure the user is logged in, search for <a href="javascript:void(0)" class="head-links">Sign Out</a>

		# Wait to not overload server
		self.randomWaitTime()

	def goToDeals(self):
		""" Navigates to the deals page on the CVS website. """

		print("Navigating to deals page...")

		# Wait to not overload server
		self.randomWaitTime()

		self.driver.get(self.extraCare)

		# Wait to not overload server
		self.randomWaitTime()

	def expandPageInstantOne(self):
		""" Scrolls instantly all the way down to the bottom of the current website page by
		going down to the 'upper-footer-container' """

		# Wait to not overload server
		self.randomWaitTime()

		print("Scrolling to the bottom of the website...")

		el_bot = self.driver.find_element(by=By.CLASS_NAME, value="upper-footer-container")

		# Scroll to the bottom of the page
		actions = ActionChains(self.driver)
		actions.move_to_element(el_bot).perform()

		print("Scrolling complete")

	def expandPageInstantTwo(self):
		""" Another way to instantly go all the way down to the bottom of a web page. """

		print("Scrolling to the bottom of the website...")

		# Wait to not overload server
		self.randomWaitTime()

		self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

	def expandPageSmoothFast(self):
		""" Smoothly scroll down to the element we are trying to reach to load the whole
		page. This scrolls to quickly, need to find a way to slow this down if I intend
		to use this. """

		print("Scrolling to the bottom of the website...")

		el_bot = self.driver.find_element(by=By.CLASS_NAME, value="upper-footer-container")

		self.driver.execute_script('arguments[0].scrollIntoView({behavior:"smooth"});', el_bot)

	def expandPage(self):
		""" Slowly scroll to the 'upper-footer-container' element. """

		# Wait to not overload server
		self.randomWaitTime()

		print("Scrolling to the bottom of the website...")

		el_bot = self.driver.find_element(by=By.CLASS_NAME, value="upper-footer-container")

		width = el_bot.location.get('x')
		height = el_bot.location.get('y')

		scrollDisctance = 10

		while(scrollDisctance < height):
			self.driver.execute_script(("window.scrollTo(0, "+str(scrollDisctance)+")"))
			time.sleep(random.uniform(0.25, 1.0))
			thing = random.uniform(100, 350)
			scrollDisctance = scrollDisctance + thing

	def addAllDealsToCard(self):
		""" Goes through the entire deals page and adds all of them to your card. """

		print("Adding deals to your card...")

		# Get the entire all coupons element
		results = self.driver.find_elements(by=By.XPATH, value="//app-all-coupons")

		actionIcons = []

		# Just in case they decided to use multiple '//app-all-coupons' in the future
		# Get all 'action-icon' elements from the 'app-all-coupons' elements
		for item in results:
			actionIcons = actionIcons + item.find_elements(by=By.CLASS_NAME, value="action-icon")

		dealsToAdd = []

		# Process all of the found 'action-icon' elements and make sure to get only the
		# elements containing "i-send-to-card.svg"
		for item in actionIcons:
			if("i-send-to-card.svg" in item.get_attribute("src")):
				dealsToAdd.append(item)

		# Wait to not overload server
		self.randomWaitTime(maxI=5)


		# Now go through and click on all of them to add to card, processing time for each request should take around 1-5 seconds
		for item in dealsToAdd:

			# Scroll to the element
			self.driver.execute_script('arguments[0].scrollIntoView({behavior:"smooth"});', item)

			time.sleep(0.5)

			item.click()
			print("Clicked on element {0}".format(item.get_attribute("src").split('/')[-1]))

			# Wait to not overload server
			self.randomWaitTime(maxI=6)

	def mainDriverTest(self):
		""" Main driver for testing on downloaded website. """

		print("Running TEST main driver")

		self.extraCare = "file:///home/daniel/Documents/CVS_website/FullWebsite/Manage ExtraCare Deals & Rewards.html"

		self.driver.get(self.extraCare)

		# Already at deals/rewards page on the downloaded website for now

		# Wait to not overload server
		self.randomWaitTime()

		# Load the entire page
		self.expandPage()

		# Wait to not overload server
		self.randomWaitTime()

		# Gather all of the info
		self.addAllDealsToCard()

		print("Program Complete")

	def mainDriver(self):
		""" Runs the execution of the current class. """

		# Check if able to bot cvs main page
		canBotMainCVS = self.checkCanBotURL(self.cvsMain)

		if(canBotMainCVS):
			# Go to the cvs main page
			self.driver.get(self.cvsMain)
		else:
			sys.exit()

		# Wait to not overload server
		self.randomWaitTime(10, 15)


		# Check if able to bot extra care page, else exit program
		canBotInitial = self.checkCanBotURL(self.extraCare)
		if(not canBotInitial):
			sys.exit()

		# Wait to not overload server
		self.randomWaitTime()

		loggedIn = False

		# Check if the user is logged into the website
		try:
			self.driver.find_element(by=By.LINK_TEXT, value="Sign Out")
			loggedIn = True
		except Exception as e:
			loggedIn = False

		# If not logged in check if able to automatically log the user into the website
		if(not loggedIn):

			# Check if it is fine for the bot to automatically sign the user into the website
			canBot = self.checkCanBotURL(self.loginURL)

			if(canBot):
				self.login()

				# Wait to not overload server
				self.randomWaitTime()

				# Go back to the extra care deals page
				self.goToDeals()

			else:

				print("Please take some time to click on the sign in option above and log yourself into your account. The site currently disallows bots to sign a user into the website. \nYou have 60 seconds to complete login process. ")
				time.sleep(60)

				# Go back to the extra care deals page
				self.goToDeals()

		# Wait to not overload server
		self.randomWaitTime()

		# Load the entire page
		self.expandPage()

		# Wait to not overload server
		self.randomWaitTime()

		# Gather all of the info
		self.addAllDealsToCard()

		print("Program Complete")



if __name__ == "__main__":
	# This is main

	option = argParse()

	username = option.username
	password = option.password
	headless = option.headless
	#webWait = option.webWait
	webWait = 20

	app = cvsDeals(username, password, webWait, headless)

	#app.mainDriverTest()

	app.mainDriver()


