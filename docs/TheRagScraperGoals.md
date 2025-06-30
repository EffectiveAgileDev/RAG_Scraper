# The Rag Scraper Goals

## The Overall Goals

###  The RAG Scraper should retrieve all relevant data for import into the RAG system on the ChatBot. 
  - Becuase the ChatBot will be used by different people, to serve many different types of web sites, 
    it must be able to foucs on the most likely terms that people will use rather than the actual words 
    that the web site might use.

###  The problem is that the current implentation uses specific words to match what the web site has.
   - This results in very few of the concepts, let alone the actual words from the web site getting 
     in the data.

##  Specific Scraping Behaviour

###  The Scraper must have an insustry selection choce that is required at the top of the Scraper.

###  Some of the choices would be ...
   1. Restaurant
   2. Real Estate
   3. Medical
   4. Dental
   5. Furniture
   6. Hadware / Home Improvment
   7. Vechicle Fuel
   8. Vehicle Sales
   9. Vehicle Repair / Towing
   10. Ride Services
   11. Shop at Home
   12. Fast Food

###  Each of these types of directory websites that use chat bots must have a user customizable database.
#### This database should contain the catetories of things that the chat bot user would search for.
#### Each site scraped (when the user has selected an industry) should use the database as a guide for the proper categorization of the specific terms or strings that the web site might have.
#### The data scraped and put into the ouput file would contain in each category, the specific words or phrases that a wesite contains.
#### Some industries and sites within industries would have pricing data.  There needs to be a switch in the UI for Pricing, and if it is for each item.


## We should use modern AI systems to describe the database to be used as output by the Scraper.
