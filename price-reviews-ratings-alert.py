#!/usr/bin/python
import time
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from lxml import html
import ConfigParser
#******************************************
# Alert the price dropped for Amazon items.
#******************************************
# Original from: github.com/eyalzek/price-alert
# Modified by: Tung Thanh Le
# Language: Python 
# Version: 2.7 
# Email: ttungl at gmail
# URL: github/ttungl
# Updated: The percentage of price dropped,
# the amount of reviews, and ratings, 
#          the amount of reviews, and ratings.
# Input:
#     Your username and password in usrpass file
#     Your receiver's email
#     Your list of items (ASINs could be imported 
#     from the console or GUI)
# Output:
#     Current Price and Dropped Percentage.
#     The amount of customer reviews.
#     The customer ratings.
#******************************************

config = ConfigParser.RawConfigParser()
config.read("usrpass")
email_receiver = config.get('email','receiver')
email_user = config.get('email','user')
email_pass = config.get('email','pass')

# Change these values to your desired sale page (the selector and price check were tested on Amazon).
BASE_URL = "http://www.amazon.com/exec/obidos/ASIN/"
SMTP_URL = "smtp.gmail.com:587"
XPATH_SELECTOR = '//*[@id="acrCustomerReviewText"]'
XPATH_SELECTOR_PRICE = '//*[@id="priceblock_ourprice"]'
XPATH_SELECTOR_RATING = '//*[@id="reviewStarsLinkedCustomerReviews"]/i/span'

## seconds
SLEEP_INTERVAL = 10 
COUNT_ITEM = 0
price_temp1 = 0
price_temp2 = 0
#ITEMS is a list of lists, storing ASINs and their maximum prices
ITEMS = [['B0042A8CW2', 180], ['B00OTWOAAQ', 300]]

def send_email(reviews, price, rating, dropped, ASIN):
    global BASE_URL

    try:
        s = smtplib.SMTP(SMTP_URL)
        s.starttls()
        s.login(email_user, email_pass)
    except smtplib.SMTPAuthenticationError:
        print("Failed to login")
    else:
        print("Logged in! Composing message..")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "{0}, Price {1}, Dropped {2}%, Ratings {3} Alert.".format(reviews, price, dropped, rating)
        msg["From"] = email_user
        msg["To"] = email_receiver
        text = "The price is lower than your expected price about {0} %.\nThe current price is {1} !!\nThe item has {2}!!\nRating is {3}. \nThe URL of the item sale-off: {4}".format(dropped, price, reviews, rating, BASE_URL+ASIN)
        part = MIMEText(text, "plain")
        msg.attach(part)
        s.sendmail(email_user, email_receiver, msg.as_string())
        print("Message has been sent.")

while True:
    #item[0] is the item's ASIN while item[1] is that item's maximum price
    for item in ITEMS:
        r = requests.get(BASE_URL + item[0])
        tree = html.fromstring(r.text)
        try:
            #We have to strip the dollar sign off of the number to cast it to a float
            reviews = (tree.xpath(XPATH_SELECTOR)[0].text[0:])
            price = float(tree.xpath(XPATH_SELECTOR_PRICE)[0].text[1:])
            rating = (tree.xpath(XPATH_SELECTOR_RATING)[0].text[0:])
            
        except IndexError:
            #print("Didn't find the 'reviews'|'price'|'rating' element, trying again")
            continue
        if price <= item[1] and price != price_temp1:
            COUNT_ITEM +=1
            price_temp1 = price #update
            diff1 = ((item[1] - price)/item[1])*100
            diff1 = round(diff1, 2)
            print("Your expected price is {}".format(item[1]))
            print("The current price is {}".format(price))
            print("The price is dropped {} %".format(diff1))
            print("The item {3} has {0}, Price {1}, and Rating {2} !! Sending the email notification.".format(reviews, price, rating, item[0]))
            send_email(reviews, price, rating, diff1, item[0])
            break
        else:
            if price > item[1] and price !=price_temp2:
                COUNT_ITEM +=1
                price_temp2 = price 
                diff2 = ((price - item[1])/item[1])*100
                diff2 = round(diff2, 2)
                print("Your expected price is {}".format(item[1]))
                print("The current price is {}".format(price))
                print("The price is still higher than your expected price about {} %".format(diff2))
                print("The item {3} has {0}, Pricing is {1}, Rating is {2}".format(reviews,price,rating, item[0]))   

    if COUNT_ITEM == len(ITEMS):
        break
	# print "Sleeping for {} seconds".format(SLEEP_INTERVAL)
	# time.sleep(SLEEP_INTERVAL)
