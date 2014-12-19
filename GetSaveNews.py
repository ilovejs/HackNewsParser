#!/usr/bin/env python
import requests
from lxml import html

################# Config #################
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Record(Base):
    __tablename__ = 'HNews'
    id = Column(Integer, primary_key=True)
    hid = Column(Integer)
    title = Column(String)
    url = Column(String)



from sqlalchemy import create_engine
engine = create_engine('sqlite:///hacknews.db')



from sqlalchemy.orm import sessionmaker
# Construct a session maker object
session = sessionmaker()
# Bind the session maker to engine
session.configure(bind=engine)
# Create all the tables in the database which are
# defined by Base's subclasses such as Record
Base.metadata.create_all(engine)
################# End config #################



def RequestPageToArray (url):
    # Test url: http://localhost/HN.htm
    p = requests.get(url).content
    dom = html.fromstring(p)

    # Test rules in Chrome, unfortunately, "tbody" is rendered in Chrome and Firefox as extra. So, should get rid of it.
    #
    # css path: (Copy from Chrome Inspector)
    #   body tbody > tr:nth-child(3) tbody > tr > td:nth-child(3) > a
    # xpath:
    #   /html/body/center/table/tbody/tr[3]/td/table/tbody/tr/td[3]/a
    NewsIdArray = []
    NewsContentArray = []
    rowCounter = 0
     
    ### Pattern is:
    #   title, url
    #   id
    #   line separator
    for e in dom.xpath("/html/body/center/table/tr[3]/td/table/tr"):
        added_hid = False
        # has content
        x = e.find("td[3]/a")
        # has id link inside comment
        y = e.find("td[2]/a[2]")
     
        rowCounter += 1
     
        # has title content, then collect Title and Url
        if hasattr(x, 'text'):
                titleD = x.text
                urlD = x.get('href')
                # print titleD, urlD
                NewsContentArray.append( (titleD, urlD) )
     
        # Need comment area, since comment area contains hack news id
        if (y is not None):
            hid = y.get('href')[8:]
            # print hid
            NewsIdArray.append(hid)
            added_hid = True
     
        # !Patch for edge case where Title exists but NO Comment and Hack news id.
        # Second row in each group (3 rows) should contains hack news id, otherwise mock one up.
        if rowCounter % 3 == 2:
            # Add pseudo hid
            if added_hid == False:
                NewsIdArray.append(88888888)
    
    # Which execute first ?
    yield NewsIdArray
    yield NewsContentArray



def SaveToDb():
    """ Request and save to database
    """
    # db write
    s = session()
    try:
        # Get page 1 - 28
        for pageNumber in range(1, 29):
            pageUrl = "https://news.ycombinator.com/news?p=" + str(pageNumber)
            print "Visit Page: " + str(pageNumber) + "======================>"
            # 30 is the page count, get rid of NewsIdArray[30] because it's edge case.
            NewsIdArray, NewsContentArray = RequestPageToArray(pageUrl)
            # Each page has 30 threads
            for threadNumber in range(0, 30):

                hid = NewsIdArray[threadNumber]

                title, url = NewsContentArray[threadNumber]
                #print hid, title, url

                # Check uniqueness by Hid
                checkOld = s.query(Record).filter(Record.hid == hid).count()
                # Has added before ?
                if checkOld == 0:
                    s.add(Record(hid=hid, title=title, url=url))
                    print "Add the " + str(threadNumber)+ "th thread on page:" + str(hid) + " | " + title + " | " + url

    except RuntimeError as rr:
        print "------------Fail at Page: " + str(pageNumber) + ", the " + str(threadNumber) + "th Thread."
        print rr
    except TypeError as tr:
        print "------------Fail at Page: " + str(pageNumber) + ", the " + str(threadNumber) + "th Thread."
        print tr
    except NameError as n:
        print "------------Fail at Page: " + str(pageNumber) + ", the " + str(threadNumber) + "th Thread."
        print n
    finally:
        s.commit()
        print "------------Finish at Page: " + str(pageNumber) + ", the " + str(threadNumber) + "th Thread."




def TestPartial():
    """ Request and save to database
    """
    # db write
    s = session()
    try:
        # Get page 1 - 27
        for pageNumber in range(28,30):
            pageUrl = "https://news.ycombinator.com/news?p=" + str(pageNumber)
            print "Test on page: " + str(pageNumber)
            # 30 is the page count, get rid of NewsIdArray[30] because it's edge case.
            NewsIdArray, NewsContentArray = RequestPageToArray(pageUrl)

            for threadNumber in range(0, 30):
                print "Trying thread: " + str(threadNumber)
                hid = NewsIdArray[threadNumber]

                title, url = NewsContentArray[threadNumber]
                #print hid, title, url

                # Check uniqueness by Hid
                checkOld = s.query(Record).filter(Record.hid == hid).count()
                # Has added before ?
                if checkOld == 0:
                    s.add(Record(hid=hid, title=title, url=url))
                    print "Add Record: " + str(id) + " | " + title + " | " + url

    except RuntimeError as rr:
        print "------------Fail at Page: " + str(pageNumber) + ", the " + str(threadNumber) + "th Thread."
        print rr
    except TypeError as tr:
        print "------------Fail at Page: " + str(pageNumber) + ", the " + str(threadNumber) + "th Thread."
        print tr
    except NameError as n:
        print "------------Fail at Page: " + str(pageNumber) + ", the " + str(threadNumber) + "th Thread."
        print n
    finally:
        s.commit()
        print "------------Finish at Page: " + str(pageNumber) + ", the " + str(threadNumber) + "th Thread."

