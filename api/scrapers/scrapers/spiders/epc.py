import scrapy
from bs4 import BeautifulSoup
from spiders.basespider import BasespiderSpider
import fitz
import re


class EpcSpider(BasespiderSpider):
    name = "epc"
    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)        
        self.pattern1 = r'\d{1,2}\s[A-Z]\b'
        self.pattern2 = r'\d{1,2}\s\|\s[A-Z]\b'
    
    def parse(self, response, **kwargs):
        data = response.meta.get("db_data")
        if any(
            substring in response.url for substring in [
                "jupix", "Document", "kea.pmp",
                "ewemove", ".pdf"
                ]
            ):
            data["scraped_info"] = self.parse_pdf(response)
            
        elif ".gov.uk" in response.url:
            data["scraped_info"] = self.parse_gov(response)
            
        else:
            data["scraped_info"] = self.parse_image(response)
            
        self.data.append(data)
        
        self.count += 1
        print(f"Number of imagess scraped: {self.count}, progress % {(self.count/self.num_urls)*100:.2f}", end="\r")
        self.check_time_limit()
        
        if len(self.data)%100 == 0:
            try:
                self.pipeline.process_epcs(self.data)
                self.data.clear()
            except Exception as e:                
                print(e)
                self.data.clear()

    def parse_image(self, response):
        return {
            "epc_image" : response.body,
            "epc_scraped" : True
        }
        
    def parse_gov(self, response):
        soup = BeautifulSoup(response.body, "html.parser")
        epc_current = soup.find(attrs={"class": "rating-current rating-label"})
        if epc_current:
            epc_current = epc_current.find(attrs={"class":"govuk-!-font-weight-bold"})
            if epc_current:
                epc_current = epc_current.text.split(" ")[0]
        
        epc_potential = soup.find(attrs={"class": "rating-potential rating-label"})
        if epc_potential:
            epc_potential = epc_potential.find(attrs={"class":"govuk-!-font-weight-bold"})
            if epc_potential:
                epc_potential = epc_potential.text.split(" ")[0]
        
        return {
            "epc_current" : epc_current,
            "epc_potential" : epc_potential,
            "epc_scraped" : True
        }
        

    def parse_pdf(self, response):
        try:
            pdf_doc = fitz.open("pdf", response.body)
        except:
            return {
                "epc_scraped": True
            }
        instances = 0
        epc_current = None
        epc_potential = None
        for page_num in range(pdf_doc.page_count):
            page = pdf_doc.load_page(page_num)
            text_list = page.get_text().split("\n")
            
            for idx, item in enumerate(text_list):
                if instances == 2:
                    break
                if (re.match(self.pattern1, item) or re.match(self.pattern2, item)) and instances == 0:
                    epc_current = int(item.split(" ")[0])
                    instances += 1
                elif (re.match(self.pattern1, item) or re.match(self.pattern2, item)) and instances == 1:
                    epc_potential = int(item.split(" ")[0])
                    instances += 1
                    break
                
        if epc_current and epc_potential:
            if epc_current > epc_potential:
                epc_current, epc_potential = epc_potential, epc_current
        
        return {
            "epc_current" : epc_current,
            "epc_potential" : epc_potential,
            "epc_scraped" : True
        }
        
    def closed(self, reason):
        self.close_spider(reason)
    
    def close_spider(self, reason):
        try:
            self.pipeline.process_epcs(self.data)
            self.data.clear()
        except Exception as e:                
            print(e)
            self.data.clear()
        