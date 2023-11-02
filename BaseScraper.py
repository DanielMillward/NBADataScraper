class BaseScraper():
    def __init__(self, start_date) -> None:
        self.start_date = start_date
        self.data = {}
        self.pages = self.get_pages()
        self.scrape()

    def scrape(self):
        """Saves data in self.data"""
        raise NotImplementedError("Base Class")
        # - for page in pages:
		#- pagedata = pagescrape(page)
		# - data\[page.id] = pagedata
    
    def get_pages(self):
        raise NotImplementedError("Base Class")
    
    def page_scrape(self):
        raise NotImplementedError("Base Class")