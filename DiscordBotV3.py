import bs4
import requests
from discord.ext import commands
from operator import itemgetter
import os
import discord
from dotenv import load_dotenv


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

client = discord.Client()

# BOT_PREFIX = ("?", "!")

# bot = commands.Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_message(message):
    # executed if user message starts with !help
    if message.content.startswith("!help"):
        await message.channel.send("Commands available: \n !newegg [search input] \n !amazon [search input]")

    # executed if user message starts with !newegg
    if message.content.startswith("!newegg"):
        # ask user to enter the product he wants to search
        user_input = message.content[7:-4]
        user_budget = float(message.content[-4:])
        await message.channel.send( "Item: %s \nBudget: $%d" %(user_input,user_budget))

        # used for comparing product name between user and web(to eliminate unmatched products)
        user_input = user_input.upper()
        product_check = user_input.split()
        await message.channel.send( "Browsing through Newegg. Please wait...")

        # newegg
        # combine root newegg url with user input
        newegg_url = (
            "https://www.newegg.ca/Product/ProductList.aspx?Submit=ENE&DEPA=0&Order=BESTMATCH&Description="
            + user_input
        )

        # build the connection and get html page from url, add headers information since amazon/newegg is heavy-anti-scraping website
        newegg_req = requests.get(
            newegg_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Mobile Safari/537.36"
            },
        )
        # get content from website
        newegg_data = newegg_req.content

        # html parsing
        newegg_soup = bs4.BeautifulSoup(newegg_data, "html.parser")

        # find total pages
        all_page = []
        newegg_pages = newegg_soup.find_all("div", {"id": "page_NavigationBar"})
        for pages in newegg_pages:
            page_tag = pages.find_all("div", {"class": "btn-group-cell"})
            for page in page_tag:
                all_page.append(page.text.strip())
        if all_page != []:
            last_page = int(all_page[-2])
        else:
            last_page = 1
        # scrape all the pages

        product_dic = {}
        for n in range(last_page):
            page = n + 1
            newegg_url = (
                "https://www.newegg.ca/Product/ProductList.aspx?Submit=ENE&DEPA=0&Order=BESTMATCH&Description="
                + user_input
                + "&page="
                + str(page)
            )

            # build the connection and get html page from url, add headers information since amazon/newegg is heavy-anti-scraping website
            newegg_req = requests.get(
                newegg_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Mobile Safari/537.36"
                },
            )

            newegg_data = newegg_req.content

            # html parsing
            newegg_soup = bs4.BeautifulSoup(newegg_data, "html.parser")

            # locate each product info
            newegg_items = newegg_soup.find_all("div", {"class": "item-container"})
            # print(len(newegg_items))

            # use for loops to find each product name and price from product info

            for item in newegg_items:
                item_name = item.find("a", {"class": "item-title"})
                item_name = item_name.text
                # if input only 1 word
                if len(product_check) == 1:
                    if product_check[0] in item_name.upper():
                        # print(item_name.strip())
                        # add product to list
                        product_dic[item_name.strip()] = ""
                        # item_price = (
                        #     item.find("li", {"class": "price-current"}).find("strong").text
                        #     + item.find("li", {"class": "price-current"}).find("sup").text
                        # )
                        try:
                            item_price = item.find("li", {"class": "price-current"})
                            item_price = (
                                item_price.find("strong").text +
                                item_price.find("sup").text
                            )
                            # print(item_price)
                            item_price = item_price.replace(",", "")
                            product_dic[item_name.strip()] = item_price
                        except:
                            # print("Third party sellers,Visit website for more details")
                            product_dic[item_name.strip(
                            )] = "Third party sellers,Visit website for more details"
                # if input 2 words
                elif len(product_check) == 2:
                    if product_check[0] and product_check[1] in item_name.upper():
                        # print(item_name.strip())
                        # add product to list
                        product_dic[item_name.strip()] = ""
                        try:
                            item_price = item.find("li", {"class": "price-current"})
                            item_price = (
                                item_price.find("strong").text +
                                item_price.find("sup").text
                            )
                            # print(item_price)
                            item_price = item_price.replace(",", "")
                            product_dic[item_name.strip()] = item_price
                        except:
                            # print("Third party sellers,Visit website for more details")
                            product_dic[item_name.strip(
                            )] = "Third party sellers,Visit website for more details"
                # if input 3 words
                elif len(product_check) == 3:
                    if (
                        product_check[0]
                        and product_check[1]
                        and product_check[2] in item_name.upper()
                    ):
                        # print(item_name.strip())
                        # add product to list
                        product_dic[item_name.strip()] = ""
                        try:
                            item_price = item.find("li", {"class": "price-current"})
                            item_price = (
                                item_price.find("strong").text +
                                item_price.find("sup").text
                            )
                            # print(item_price)
                            item_price = item_price.replace(",", "")
                            product_dic[item_name.strip()] = item_price
                        except:
                            # print("Third party sellers,Visit website for more details")
                            product_dic[item_name.strip(
                            )] = "Third party sellers,Visit website for more details"

        if user_budget > 1:
            for key, value in product_dic.items():
                try:
                    if float(value) <= user_budget:
                        await message.channel.send( (key + "\n" + value))
                except:
                    await message.channel.send( (key + "\n" + value))
            await message.channel.send( "End of search. If nothing shows up, means products are not available at this budget")

        else:
            for key, value in product_dic.items():
                await message.channel.send( key + "\n" + value)
            # search lowest value in product_dic = best price
            try:
                # set Third party sellers to None, So we can skip this string when we do conversion
                for key, value in product_dic.items():
                    if "Third party" in value:
                        product_dic[key] = None
                # find best price
                product_dic = dict((k, float(v))
                                   for k, v in product_dic.items() if v is not None)
                await message.channel.send( "Best Price is:")
                await message.channel.send(  (min(product_dic.items(), key=itemgetter(1))))
            except:
                await message.channel.send( "End of search. If nothing shows up, means products are not available at this budget")

            #pings the user who triggered the bot commands
            await message.channel.send(  str(message.author.mention))

    # executed if user message starts with !amazon
    if message.content.startswith("!amazon"):
        # reads user input using string manipulation
        amazon_user_input = message.content[7:-4]
        amazon_user_budget = float(message.content[-4:])
        await message.channel.send( "Item: %s \nBudget: $%d" %(amazon_user_input,amazon_user_budget))

        # used for comparing product name between user and web(to eliminate unmatched products)
        amazon_user_input = amazon_user_input.upper()
        amazon_product_check = amazon_user_input.split()
        await message.channel.send( "Browsing through Amazon. Please wait... \n")

        # amazon

        # scrape how many pages(default is 10)
        pages = 10

        # combine root amazon url with user input and scrape all the pages
        product_dic = {}
        for n in range(pages):
            page = n + 1
            amazon_url = "https://www.amazon.com/s?k=" + amazon_user_input + "&page=" + str(page)
            # build the connection and get html page from url, add headers information since amazon/newegg is heavy-anti-scraping website
            amazon_req = requests.get(
                amazon_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Mobile Safari/537.36"
                },
            )
            # get content from website
            amazon_data = amazon_req.content

            # html parsing
            amazon_soup = bs4.BeautifulSoup(amazon_data, "html.parser")

            # locate each product info
            amazon_items = amazon_soup.find_all(
                "div", {"class": "s-include-content-margin s-border-bottom"}
            )

            # use for loops to find each product name and price from product info

            for item in amazon_items:
                item_name = item.find(
                    "span", {"class": "a-size-base a-color-base a-text-normal"}
                )
                item_name = item_name.text
                # if input only 1 word
                if len(amazon_product_check) == 1:
                    if amazon_product_check[0] in item_name.upper():
                        # print(item_name.strip())
                        product_dic[item_name.strip()] = ""
                        try:
                            item_price = item.find(
                                "span", {"class": "a-offscreen"}).text
                            # print(item_price)
                            item_price = item_price.replace(",", "")
                            item_price = item_price.replace("$", "")
                            product_dic[item_name.strip()] = item_price
                        except:
                            # print("Third party sellers,Visit website for more details")
                            product_dic[item_name.strip(
                            )] = "Third party sellers,Visit website for more details"
                # if input 2 words
                elif len(amazon_product_check) == 2:
                    if amazon_product_check[0] and amazon_product_check[1] in item_name.upper():
                        # print(item_name)
                        product_dic[item_name.strip()] = ""
                        try:
                            item_price = item.find(
                                "span", {"class": "a-offscreen"}).text
                            # print(item_price)
                            item_price = item_price.replace(",", "")
                            item_price = item_price.replace("$", "")
                            product_dic[item_name.strip()] = item_price
                        except:
                            # print("Third party sellers,Visit website for more details")
                            product_dic[item_name.strip(
                            )] = "Third party sellers,Visit website for more details"
                # if input 3 words
                elif len(amazon_product_check) == 3:
                    if (
                        amazon_product_check[0]
                        and amazon_product_check[1]
                        and amazon_product_check[2] in item_name.upper()
                    ):
                        # print(item_name)
                        product_dic[item_name.strip()] = ""
                        try:
                            item_price = item.find(
                                "span", {"class": "a-offscreen"})   .text
                            # print(item_price)
                            item_price = item_price.replace(",", "")
                            item_price = item_price.replace("$", "")
                            product_dic[item_name.strip()] = item_price
                        except:
                            # print("Third party sellers,Visit website for more details")
                            product_dic[item_name.strip()] = "Third party sellers,Visit website for more details"

        if amazon_user_budget > 1:
            for key, value in product_dic.items():
                try:
                    if float(value) <= amazon_user_budget:
                        await message.channel.send( (key + "\n" + value))
                except:
                    await message.channel.send( (key + "\n" + value))
            await message.channel.send( "End of search. If nothing shows up, means products are not available at this budget")

        else:
            for key, value in product_dic.items():
                await message.channel.send( key + "\n" + value)
            # search lowest value in product_dic = best price
            try:
                # set Third party sellers to None, So we can skip this string when we do conversion
                for key, value in product_dic.items():
                    if "Third party" in value:
                        product_dic[key] = None
                # find best price
                product_dic = dict((k, float(v))
                                   for k, v in product_dic.items() if v is not None)
                await message.channel.send( "Best Price is:")
                await message.channel.send(  (min(product_dic.items(), key=itemgetter(1))))
            except:
                await message.channel.send( "End of search. If nothing shows up, means products are not available at this budget")

            #pings the user who triggered the bot commands
            await message.channel.send(  str(message.author.mention))


client.run(token)
