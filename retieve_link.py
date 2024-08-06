import json
from collections import Counter

class PostingListSearcher:
    def __init__(self, posting_list_file):
        self.posting_list_file = posting_list_file
        self.index = self.load_posting_list()

    def load_posting_list(self):
        with open(self.posting_list_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    def search(self, query):
        query_words = query.lower().split()
        result = {}

        for word in query_words:
            if word in self.index:
                result[word] = self.index[word]
            else:
                result[word] = []

        return result

    def display_results(self, results):
        for word, files in results.items():
            file_counter = Counter(files)
            sorted_files = sorted(file_counter.items(), key=lambda item: item[1], reverse=True)

            print(f'Word: "{word}" found in:')
            for file, frequency in sorted_files:
                print(f'  - {file} (frequency: {frequency})')
            if not files:
                print(f'  - No results found for "{word}".')

# Usage
posting_list_file = 'web_links_posting_list.json'
searcher = PostingListSearcher(posting_list_file)

query = input("Enter your search query: ")
results = searcher.search(query)
searcher.display_results(results)
