import requests
info = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "O2u7Kug97EzDAdbpNr5syg", "isbns":  '0380795272'}).json()
print(info['books'][0]['average_rating'])
