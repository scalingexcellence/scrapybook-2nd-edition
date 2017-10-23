# Learning Scrapy Book, 2nd Edition

This book covers the long awaited Scrapy v 1.4 that enables you to extract useful data from virtually any source with very little effort. It starts off by explaining the fundamentals of Scrapy framework, followed by a thorough description of how to extract data from any source, clean it up, shape it as per your requirement using Python and 3rd party APIs. Next you will be familiarised with the process of storing the scrapped data in databases as well as search engines and performing real time analytics on them with Spark Streaming. By the end of this book, you will perfect the art of scraping data for your applications with ease.

This 2nd edition of this book will soon be released.

## What you will learn

- Understand HTML pages and write XPath to extract the data you need
- Write Scrapy spiders with simple Python and do web crawls
- Push your data into any database, search engine or analytics system
- Configure your spider to download files, images and use proxies
- Create efficient pipelines that shape data in precisely the form you want
- Use Twisted Asynchronous API to process hundreds of items concurrently
- Make your crawler super-fast by learning how to tune Scrapy's performance
- Perform large scale distributed crawls with scrapyd and scrapinghub

## How to run

1. Download this repo on a directory either as a .zip or by doing `git clone https://github.com/scalingexcellence/scrapybook-2nd-edition.git`.

2. Go to the directory of the book by doing `cd scrapybook-2nd-edition`.

3. You can install all the code and depedencies with this command:
```
virtualenv -p python3 --no-site-packages --distribute .env && \
    source .env/bin/activate && \
    pip install -r requirements.txt
```

4. Then you start the web server with the examples for the book by doing:
```
start.sh &
```

5. Then you can `cd` to individual chapters and run the code as described in the book.

## Reference


`pip freeze`
`pip install scrapy`
 
