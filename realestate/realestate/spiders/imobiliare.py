from gc import callbacks
from subprocess import call
from unittest import result
import unicodedata
import scrapy
import re


class ImobiliareSpider(scrapy.Spider):
    name = 'imobiliare'
    allowed_domains = ['imobiliare.ro']

    def start_requests(self): 
        URLs = ['https://www.imobiliare.ro/vanzare-apartamente/bucuresti/']
        
        for i in range(1, 300):
            URLs.append('https://www.imobiliare.ro/vanzare-apartamente/bucuresti?pagina=%s' % (i))
            print(URLs[i])
         
        for url in URLs:
            yield  scrapy.Request(url = url, callback = self.parse)
        
    def parse(self, response):
        for href in response.css("h2 > a.click_din_lista::attr(href)").extract():
            yield response.follow(href, self.parse_article_one_obj)

    def parse_article(self, response):
        detailsULs = response.css('ul.lista-tabelara')
        name = response.css('h1::text').get().encode().decode('utf-8')

        estate = {
            'name': name, 
            'details': {}, 
            'specs': {},
        }

        for ul in detailsULs: 
            for li in ul.css('li'):
                fieldTtile = li.css('li::text').get().encode().decode('utf-8')
                fieldValue = li.css('li > span::text').get().encode().decode('utf-8')
                estate['details'][fieldTtile] = fieldValue

        specsULs = response.css('div#b_detalii_specificatii > ul')
        spectTitles = response.css('div#b_detalii_specificatii > h4')

        for i in range(len(specsULs)):
            specName = spectTitles[i].css('h4::text').get()

            estate['specs'][specName] = []
            for specUL in specsULs[i].css('ul'): 
                for specLI in specUL.css('li'): 
                    estate['specs'][specName].append(specLI.css('li>span::text').get())

        yield estate


    def parse_article_one_obj(self, response):
        def parse_attributes(response, string):
            result = response.xpath("//*[contains(text(), '{}')]".format(string))
            if(len(result)>0):
                result = result.getall()[0]
                return re.search('<span>(.*)</span>', result).group(1) 
            return None

        location = response.css('div.row.localizare_top.header_info div.col-12.d-inline-flex::text')[1].extract().encode().decode('utf-8').replace("  ", "").replace("\n", "").split('zona', 1)[1]
        price = response.css('div.pret.first.dl_infotip_pret_fix::text').get().encode().decode('utf-8')
        name = response.css('h1::text').get().encode().decode('utf-8').replace("  ", "").replace("\n", "")
        rooms = parse_attributes(response, 'Nr. camere:')
        surface = parse_attributes(response, 'Suprafaţă utilă:')
        separation = parse_attributes(response, 'Compartimentare:')
        confort = parse_attributes(response, 'Confort:')
        floor = parse_attributes(response, 'Etaj:')[5:6]
        if(floor < '0' or floor > '99'):
            floor = 0
        kitchensNo =  parse_attributes(response, 'Nr. bucătării:')
        bathroomsNo = parse_attributes(response, 'Nr. băi:')
        year = parse_attributes(response, 'An construcţie:')
        balconiesNo = parse_attributes(response, 'Nr. balcoane:')

        estate = {
            'location': location,
            'name': name, 
            'price': price,
            'rooms': rooms,
            'surface': surface[:len(surface) - 3],
            'confort': confort,
            'separation': separation,
            'floor': floor,
            'kitchensNo': kitchensNo,
            'bathroomsNo': bathroomsNo,
            'year': year[0:4],
            'balconiesNo': balconiesNo,
        }

        yield estate

# source venv/bin/activate
# scrapy crawl imobiliare
