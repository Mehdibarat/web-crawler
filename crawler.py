import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict
import nltk
import re
import json

# Initialize the nltk resources
nltk.download('punkt')

class WebCrawler:
    def __init__(self, start_url, max_depth=2):
        self.start_url = start_url
        self.max_depth = max_depth
        self.visited_urls = set()
        self.web_links_index = defaultdict(list)
        self.page_files_index = defaultdict(list)
        self.output_dir = 'crawled_pages'
        self.web_links_index_file = 'web_links_posting_list.json'
        self.page_files_index_file = 'page_files_posting_list.json'
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def fetch_content(self, url):
        try:
            response = requests.get(url, verify=False)  # Bypass SSL/TLS certificate verification
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return ""
    
    def save_content(self, url, content, count):
        file_path = os.path.join(self.output_dir, f'page_{count}.txt')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return file_path
    
    def extract_links(self, content, base_url):
        soup = BeautifulSoup(content, 'html.parser')
        links = set()
        for a_tag in soup.find_all('a', href=True):
            link = urljoin(base_url, a_tag['href'])
            parsed_link = urlparse(link)
            if parsed_link.netloc == urlparse(self.start_url).netloc:
                links.add(link)
        return links
    
    def index_content(self, content, url, file_path):
        soup = BeautifulSoup(content, 'html.parser')
        visible_texts = soup.stripped_strings
        full_text = " ".join(visible_texts)
        tokens = nltk.word_tokenize(full_text)
        for token in tokens:
            token = token.lower()
            if re.match(r'\w+', token):
                self.web_links_index[token].append(url)
                self.page_files_index[token].append(file_path)
    
    def crawl(self, url, depth):
        if depth > self.max_depth or url in self.visited_urls:
            return
        
        self.visited_urls.add(url)
        content = self.fetch_content(url)
        if content:
            file_path = self.save_content(url, content, len(self.visited_urls))
            self.index_content(content, url, file_path)
            links = self.extract_links(content, url)
            for link in links:
                self.crawl(link, depth + 1)
    
    def save_index(self):
        with open(self.web_links_index_file, 'w', encoding='utf-8') as file:
            json.dump(self.web_links_index, file, ensure_ascii=False, indent=4)
        with open(self.page_files_index_file, 'w', encoding='utf-8') as file:
            json.dump(self.page_files_index, file, ensure_ascii=False, indent=4)
    
    def load_index(self):
        if os.path.exists(self.web_links_index_file):
            with open(self.web_links_index_file, 'r', encoding='utf-8') as file:
                self.web_links_index = json.load(file)
        if os.path.exists(self.page_files_index_file):
            with open(self.page_files_index_file, 'r', encoding='utf-8') as file:
                self.page_files_index = json.load(file)
    
    def display_index(self):
        print("Web Links Index:")
        for word, links in self.web_links_index.items():
            print(f'{word}: {links}')
        
        print("\nPage Files Index:")
        for word, files in self.page_files_index.items():
            print(f'{word}: {files}')

# Usage
start_url = 'https://basu.ac.ir/'
crawler = WebCrawler(start_url)
crawler.crawl(start_url, 0)
crawler.save_index()  # Save the posting lists to separate files
crawler.display_index()