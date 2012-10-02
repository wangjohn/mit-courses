from BeautifulSoup import BeautifulSoup
import re
import urllib2
from datetime import datetime
import csv

def find_result_set_items(url):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    
    results = []
    for item in soup.find('div', {'id':'ResultSetItems'}).findAll('table', {'class': 'li rsittlref'}):
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
        examine_item(item.find('div', {'class':'ittl'}).a["href"])

        results.append({
            'title': title,
            'num_dozens': num_dozens,
            'price': price, 
            'was_sold': was_sold,
            'date': date,
            'unit_price': unit_price,
            'percentage_capitals': percentage_capitals,
            'number_annoying_punctuation': number_exclamations
        })
    return results

def get_title(title_link_soup):
    return str(title_link_soup.find('a', text=True))

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

def examine_item(link):
    results = {}
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

    print results["seller_score"]
    bid_history_soup = soup.find("div", {"class": "vi-cvip-bidt1"})
    if bid_history_soup:
        # If there is bid history, get the list of buyers and their bids
        bid_history_link = bid_history_soup.a["href"]
        print bid_history_link
        try:
            bid_history_page = urllib2.urlopen(bid_history_link)
            bid_history_soup = BeautifulSoup(bid_history_page)
        except:
            return results
        history_table = bid_history_soup.find("div", {"id": "vizrefdiv"})
        buyers = history_table.findAll("tr")
        for i in xrange(len(buyers)):
            buyer = buyers[i]
            buyer_score = buyer.find("a", {"id":"feedBackScoreDiv3"}, text=True)
            if buyer_score:
                results["buyers"].append([buyer_score])
            bid_info = buyer.findAll("td", {"class":"contentValueFont"})
            for i in xrange(len(bid_info)//2):
                cost = bid_info[i].find("span", text=True)
                datetime = bid_info[i+1].findAll("span", text=True)
                print cost, datetime
        print bid_info
        print results["buyers"] 

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
        item_list = ['title','num_dozens','price','was_sold','date','unit_price','percentage_capitals','number_annoying_punctuation']
        writer.writerow(item_list)
        for i in xrange(len(results)):
            writer.writerow([results[i][item] for item in item_list])

if __name__ == '__main__':
    results = []
    #results.extend(find_result_set_items('http://www.ebay.com/sch/i.html?_sadis=200&LH_ItemCondition=3&LH_SALE_CURRENCY=0&_from=R40&_sacat=0&_adv=1%7C1&_sop=13&_dmd=1&LH_Complete=1&_nkw=titleist+prov1+golf+balls+new+1+dozen&rt=nc'))
    #results.extend(find_result_set_items('http://www.ebay.com/sch/i.html?_sadis=200&_adv=1%7C1&LH_ItemCondition=3&_sop=13&LH_SALE_CURRENCY=0&_sacat=0&_from=R40&LH_Complete=1&_dmd=1&_nkw=titleist+prov1+golf+balls+new+1+dozen&_pgn=2&_skc=200&rt=nc'))
    results.extend(find_result_set_items('http://www.ebay.com/sch/i.html?_sadis=200&LH_ItemCondition=3&LH_SALE_CURRENCY=0&_from=R40&_sacat=0&_adv=1%7C1&_sop=13&_dmd=1&LH_Complete=1&_nkw=titleist+prov1+golf+balls+new+1+dozen&_pgn=3&_skc=400&rt=nc'))
    #print_to_csv(results, 'ps2_scraped_data_2.csv')
