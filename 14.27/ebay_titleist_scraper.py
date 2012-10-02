from BeautifulSoup import BeautifulSoup
import re
import urllib2
from datetime import datetime
import csv

def find_result_set_items(url):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    
    results = []
    counter = 0
    for item in soup.find('div', {'id':'ResultSetItems'}).findAll('table', {'class': 'li rsittlref'}):
        counter += 1
        # get the soup objects
        title_link_soup = item.find('div', {'class': 'ittl'})
        price_soup = item.find('td', {'class': 'prc'})
        num_bids_soup = item.find('td', {'class': 'bids bin1'})
        if not price_soup:
            price_soup = item.find('tr', {'class':'prc'})
        if not num_bids_soup:
            num_bids_soup = item.find('tr', {'class':'bids bin1'})
        time_soup = item.find('span', {'class':'tme'}).span

        # get the characteristics from the soup objects
        title = get_title(title_link_soup)
        num_dozens = parse_title_for_dozen(title)
        price = get_price(price_soup)
        was_sold = get_sold_status(num_bids_soup)
        date = get_time(time_soup) 
        percentage_capitals = get_percentage_capitals(title)
        number_exclamations = get_number_exclamations(title)
        if price and num_dozens:
            unit_price = price * 1.0 / num_dozens
        else:
            unit_price = None

        # get the item link
        item_bid_results = examine_item(item.find('div', {'class':'ittl'}).a["href"])
        next_result_hash = {
            'title': title,
            'num_dozens': num_dozens,
            'price': price, 
            'was_sold': was_sold,
            'date': date,
            'unit_price': unit_price,
            'percentage_capitals': percentage_capitals,
            'number_annoying_punctuation': number_exclamations
        }
        for key, value in item_bid_results.iteritems():
            next_result_hash[key] = value
        results.append(next_result_hash)
        print "Result %s: next_result_hash['title']" % str(counter)
    return results

def get_title(title_link_soup):
    title = str(title_link_soup.find('a', text=True))
    return re.sub(";","-",title) # replace semicolons so it doesn't goof up csv formatting

def get_price(price_soup):
    regex_search = re.search("<div class=\"(.*?)(bidsold|binsold)\".*?>\s*\$(.*?)</div>", str(price_soup))
    if regex_search:
        string_price = regex_search.group(3)
        try:
            return float(string_price.strip())
        except ValueError:
            return None
    return None

def get_sold_status(num_bids_soup):
    if num_bids_soup.find('span', {'class': 'sold'}):
        return True
    return False

# returns a hash results of the following spec:
# results["seller_score"] is the seller's ebay score
# results["buyers"] is a list of lists for each bid in the bid histry
#   [buyer_score, price of bid, date of bid]
# results["bid_history_link"] is a link leading to bid history
# results["auction_link"] is a link leading to the auction page
def examine_item(link):
    results = {"auction_link": link}
    try:
        page = urllib2.urlopen(link)
    except:
        return results
    soup = BeautifulSoup(page)
    seller_score = soup.find("div", {"class": "si-content si-mini-sinfo"})

    # go through the spans and figure out the seller's reputation score
    for span in seller_score.findAll("span"):
        search_result = re.search("<a href=\".*?\".*?>(.*?)</a>", str(span))
        if search_result:
            results["seller_score"] = search_result.group(1)
            break

    bid_history_soup = soup.find("div", {"class": "vi-cvip-bidt1"})
    if bid_history_soup:
        # If there is bid history, get the list of buyers and their bids
        bid_history_link = bid_history_soup.a["href"]
        results["bid_history_link"] = bid_history_link
        try:
            bid_history_page = urllib2.urlopen(bid_history_link)
            bid_history_soup = BeautifulSoup(bid_history_page)
        except:
            return results
        history_table = bid_history_soup.find("div", {"id": "vizrefdiv"})
        buyers = history_table.findAll("tr")
        results["buyers"] = []
        for i in xrange(len(buyers)):
            # skip the first row, since it is just the header
            if i > 0:
                buyer = buyers[i]
                # get the buyer's ebay reputation score
                search_result = re.search("<a id=\"feedBackScoreDiv3\">(.*?)</a>", str(buyer))
                try:
                    buyer_score = search_result.group(1)
                except:
                    buyer_score = None
                bid_info = buyer.findAll("td", {"class":"contentValueFont"})
                cost = None
                date = None
                # get the info from the contentValueFont class
                if bid_info:
                    search_result = re.search("US\s*\$(.*?)</span>", str(bid_info[0]))
                    try:
                        cost = search_result.group(1)
                    except:
                        cost = None 
                    date = bid_info[1].findAll("span", text=True)
                    try:
                        date = [str(result).strip() for result in date]
                        date = datetime.strptime(' '.join(date).strip(), "%b-%d-%y %H:%M:%S PDT")
                    except:
                        date = None

                # add the information to the results hash, if we have any 
                if buyer_score or cost or date:
                    results["buyers"].append([buyer_score, cost, date])
    return results

def get_time(time_soup):
    if time_soup:
        time_string = time_soup.find('span', text=True)
        if time_string:
            return datetime.strptime(time_string, "%b-%d %H:%M")
    return None

Small_numbers = {
    'zero': 0,
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
    'eleven': 11,
    'twelve': 12,
    'thirteen': 13,
    'fourteen': 14,
    'fifteen': 15,
    'sixteen': 16,
    'seventeen': 17,
    'eighteen': 18,
    'nineteen': 19,
    'twenty': 20,
    'thirty': 30,
    'forty': 40,
    'fifty': 50,
    'sixty': 60,
    'seventy': 70,
    'eighty': 80,
    'ninety': 90
}

def parse_title_for_dozen(title):
    words = re.compile("[\s-]").split(title)
    for i in xrange(len(words)):
        if re.match("dozen", words[i], flags=re.IGNORECASE):
            if i > 0:
                # first check if can be made into an integer
                stripped_word = words[i-1].lower().strip()
                try:
                    return int(stripped_word)
                except ValueError:
                    if stripped_word in Small_numbers:
                        return Small_numbers[stripped_word]
                # if none of these tactics work, give up and assume 1
                return 1 
            else:
                # otherwise we assume there is only a single dozen of balls
                return 1
    # if we can't find the word dozen, we return None
    return None

def get_percentage_capitals(title):
    length = len(title)
    lowercase = title.lower()
    counter = 0
    for i in xrange(len(title)):
        if title[i] != lowercase[i]:
            counter += 1
        if title[i] == " ":
            length -= 1
    return float(counter) / length

def get_number_exclamations(title):
    return len(re.findall("[!?\*\-]", title))

def print_to_csv(results, filename):
    with open(filename, 'wb') as f:
        writer = csv.writer(f)
        item_list = ['title','num_dozens','price','was_sold','date','unit_price','percentage_capitals','number_annoying_punctuation','seller_score','auction_link','bid_history_link']
        extra_items = ['buyer_score', 'price_of_bid', 'date_of_bid', 'final_buyer']
        writer.writerow(item_list + extra_items)
        for i in xrange(len(results)):
            if "buyers" in results[i]:
                for j in xrange(len(results[i]["buyers"])):
                    buyer_bid = results[i]["buyers"][j]
                    buyer_bid.append(True if j == 0 else False)
                    writer.writerow([(results[i][item] if (item in results[i]) else None) for item in item_list] + buyer_bid)
            else:
                writer.writerow([(results[i][item] if (item in results[i]) else None) for item in item_list])

if __name__ == '__main__':
    results = []
    #results.extend(find_result_set_items('http://www.ebay.com/sch/i.html?_sadis=200&LH_ItemCondition=3&LH_SALE_CURRENCY=0&_from=R40&_sacat=0&_adv=1%7C1&_sop=13&_dmd=1&LH_Complete=1&_nkw=titleist+prov1+golf+balls+new+1+dozen&rt=nc'))
    #results.extend(find_result_set_items('http://www.ebay.com/sch/i.html?_sadis=200&_adv=1%7C1&LH_ItemCondition=3&_sop=13&LH_SALE_CURRENCY=0&_sacat=0&_from=R40&LH_Complete=1&_dmd=1&_nkw=titleist+prov1+golf+balls+new+1+dozen&_pgn=2&_skc=200&rt=nc'))
    #results.extend(find_result_set_items('http://www.ebay.com/sch/i.html?_sadis=200&LH_ItemCondition=3&LH_SALE_CURRENCY=0&_from=R40&_sacat=0&_adv=1%7C1&_sop=13&_dmd=1&LH_Complete=1&_nkw=titleist+prov1+golf+balls+new+1+dozen&_pgn=3&_skc=400&rt=nc'))
    results.extend(find_result_set_items("http://www.ebay.com/sch/i.html?_nkw=callaway+tour+golf+balls+dozen&_sacat=0&_odkw=callaway+tour+golf+balls+1+dozen&_sadis=200&_adv=1%7C1&_sop=13&LH_SALE_CURRENCY=0&_osacat=0&_from=R40&_dmd=1&LH_Complete=1"))
    results.extend(find_result_set_items('http://www.ebay.com/sch/i.html?_sadis=200&_adv=1%7C1&_sop=13&LH_SALE_CURRENCY=0&_sacat=0&_from=R40&LH_Complete=1&_dmd=1&_nkw=callaway+tour+golf+balls+dozen&_pgn=2&_skc=200&rt=nc'))
    print_to_csv(results, 'ps2_scraped_data_callway.csv')
