class BaseScraper():
    def __init__(self, start_date, player_list=None) -> None:
        self.start_date = start_date
        self.data = {}
        if player_list is None:
            self.pages = self.get_pages()
        else:
            self.pages = player_list
        self.scrape()

    def get_pages(self, players_urls=None):
        raise NotImplementedError("Base Class - get_pages")
    
    def scrape(self):
        """Saves data in self.data"""
        raise NotImplementedError("Base Class - scrape")
        # - for page in pages:
		#- pagedata = pagescrape(page)
		# - data\[page.id] = pagedata
    
    def page_scrape(self):
        raise NotImplementedError("Base Class")