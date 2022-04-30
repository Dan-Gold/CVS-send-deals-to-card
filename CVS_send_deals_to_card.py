"""

Python 3.10.4

Summary:
This is a failed project. CVS.com keeps blocking my browser eventhough I am following thier robots.txt file as far as I can tell in conjunction with urllib.robotparser


https://stackoverflow.com/questions/65080685/usb-usb-device-handle-win-cc1020-failed-to-read-descriptor-from-node-connectio?answertab=scoredesc#tab-top
If you aren't having issues connecting to a device with WebUSB you can ignore these warnings. They are triggered by Chrome attempting to read properties of USB devices that are currently suspended.

"""

import argparse
import getpass
import random
import sys
import time



import urllib
import urllib.request
import urllib.robotparser as urobot


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains


def argParse():
	""" This is the argparse for calling this script as main """

	parser = argparse.ArgumentParser(description = "This program is used to log the current user onto the CVS website, navagate to the current rewards page and add all of the current deals to the users card. ")

	required = parser.add_argument_group("required arguments")

	# Required arguments
	required.add_argument('-u', dest="username", help = "The email or username used to log into the website. ", required=True)
	required.add_argument('-p', action=password, dest="password", nargs='?', help = "The password used to log into the webiste. If none specified the program will ask the user for a password via terminal input. ", required=True)

	# Optional arguments
	#parser.add_argument('-w', dest="webWait", default=20, help = "Max ammount of time to wait for a webpage element to load", required=True)

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

	def __init__(self, username, password, webWait):
		""" Object constructor for the class. """

		# Input
		self.userName = username # Username or email used to log into the website
		self.passWord = password # Password used to log into the website associated with the given username or email address
		self.webWait = webWait

		# Hard coded links for navigation
		self.loginURL = "https://www.cvs.com/retail-login/account/login/home?icid=cvsheader:signin&screenname=/"
		self.extraCare = "https://www.cvs.com/extracare/home?icid=cvsheader:extracare"
		self.robots = "https://www.cvs.com/robots.txt"

		# Internal setup actions
		self.driver = webdriver.Chrome()
		self.robotsParse = self.setupURLChecker()
		random.seed(time.time())

	def setupURLChecker(self):
		""" Sets up the robot file parser that will be used in checkCanBotURL(). """

		rp = urobot.RobotFileParser()
		rp.set_url(self.robots)
		rp.read()
		return(rp)

	def randomWaitTime(self, min=4, max=10):
		""" Waits for a random amount of time to pass to not overload the website and hopefully to trick the website to thinking we are not a bot and to give the server a break from fast requests. min cannot be less than 3. Returns nothing. """

		if(min < 4):
			min = 4

		rand = random.uniform(min, max)

		print("Waiting for {0} seconds... Standby...".format(rand))

		time.sleep(rand)

	def checkCanBotURL(self, url):
		""" Checks the given url to see if the program is allowed to bot the specific webpage based on information from the website's robots.txt file. """

		if(self.robotsParse.can_fetch("*", url)):
			print("The webpage: {0}   is allowed to be parsed and botted according to the robot.txt file on hand. ".format(url))
			return(True)
		else:
			print("The webpage: {0}   is NOT allowed to be parsed and botted according to the robot.txt file on hand. ".format(url))
			return(False)

	def checkDriver(self):
		""" Checks if google chrome driver is installed. TODO: Check preferences to see which driver the user wants to use, or test to see if this can work with other drivers... Check/download latest driver. """
		pass

	def login(self):
		""" Logs the user into the website if robots.txt allows. """

		# Setup wait object
		wait = WebDriverWait(self.driver, self.webWait)

		# Go straight to login page
		self.driver.get(self.loginURL)

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

		# Wait to not overload server
		self.randomWaitTime()

	def goToDeals(self):
		""" Navigates to the deals page on the CVS website. """

		# Wait to not overload server
		self.randomWaitTime()

		self.driver.get("https://www.cvs.com/extracare/home?icid=cvsheader:extracare")

		# Wait to not overload server
		self.randomWaitTime()

	def expandPage(self):
		""" Scrolls all the way down to the bottom of the current website page by scrolling down to the copy right information. """

		# Wait to not overload server
		self.randomWaitTime()

		# Create wait object
		wait = WebDriverWait(self.driver, self.webWait)

		# Wait for copy right to show up at the bottom of the page
		copyRight = "/html/body/app-root/div[2]/app-home-page/cvs-footer-container/footer/div/section[2]/cvs-legal-content-ribbon//div[2]/p"
		el_copyRight = wait.until(EC.presence_of_element_located((By.XPATH, copyRight)))

		# Wait to not overload server
		self.randomWaitTime()

		# Scroll to the bottom of the page
		el_copyRight.scrollIntoView()

		# Wait to not overload server
		self.randomWaitTime()

	def addAllDealsToCard(self):
		""" Goes through the entire deals page and adds all of them to your card. """

		# Get all i-send-to-card.svg xpath locations or something, elements
		#<img _ngcontent-sfk-c58="" alt="" class="action-icon" src="/webcontent/ng-extracare/extracare-v2/assets/img/coupon-images/i-send-to-card.svg">
		# HTML <img _ngcontent-sfk-c62="" alt="" class="action-icon" src="/webcontent/ng-extracare/extracare-v2/assets/img/coupon-images/i-send-to-card.svg">
		# Selector #coupon_396718 > div.right-part.ng-star-inserted > button > img
		# JS path # document.querySelector("#coupon_396718 > div.right-part.ng-star-inserted > button > img")
		# XPATH # /html/body/app-root/div[2]/app-home-page/main/app-home-content/app-authenticated-view/div/app-coupon-listing-wrapper/div/div/div[2]/div/app-all-coupons/div/div[3]/div[1]/div[29]/app-manufacture/div/div[2]/button/img
		#         /html/body/app-root/div[2]/app-home-page/main/app-home-content/app-authenticated-view/div/app-coupon-listing-wrapper/div/div/div[2]/div/app-all-coupons/div/div[3]/div[1]/div[22]/app-manufacture/div/div[2]/button/img
		#         /html/body/app-root/div[2]/app-home-page/main/app-home-content/app-authenticated-view/div/app-coupon-listing-wrapper/div/div/div[2]/div/app-all-coupons/div/div[2]/div[32]/div/app-variable/div/div[2]/button/img


		results = driver.find_elements_by_xpath("//app-all-coupons")

		# Store results for testing purposes, maybe it will be usefull.
		for item in results:
			print("==================================================================")
			print(item)
			print(item.get_attribute("innerHTML"))
			print(item.get_attribute("outerHTML"))
			print(item.get_attribute("src"))

			with open(cvsData.txt, 'a+') as f:
				f.write("===========================================================================================================================================================================================================")
				f.write(item)
				f.write(item.get_attribute("innerHTML"))
				f.write(item.get_attribute("outerHTML"))
				f.write(item.get_attribute("src"))

	def mainDriver(self):
		""" Runs the execution of the current class. """

		canBotInitial = self.checkCanBotURL(self.extraCare)

		if(canBotInitial):
			# Go to the extra care deals page
			self.driver.get(self.extraCare)
		else:
			sys.exit()

		# Wait to not overload server
		self.randomWaitTime(10, 15)

		loggedIn = False

		# Check if the user is logged into the website
		try:
			self.driver.find_element_by_link_text("Sign Out")
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

		# See which deals are not added to card, or can be added to the card
		# after parsing click on all of the elements to add to card, but make sure to give 3-5 is seconds randomly



if __name__ == "__main__":
	# This is main

	option = argParse()

	username = option.username
	password = option.password
	#webWait = option.webWait
	webWait = 20

	app = cvsDeals(username, password, webWait)

	app.mainDriver()

