#!/usr/bin/env python
import requests
from lxml import html
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
# Construct a sessionmaker object
session = sessionmaker()
 
# Bind the sessionmaker to engine
session.configure(bind=engine)
 
# Create all the tables in the database which are
# defined by Base's subclasses such as Record
Base.metadata.create_all(engine)
 
#--------------------------------------------------------
# Test url: http://localhost/HN.htm
 
p = requests.get("http://news.ycombinator.com").content
dom = html.fromstring(p)
 
# Test rules in Chrome, unfortunately, "tbody" is rendered in Chrome and Firefox as extra. So, should get rid of it.
#
# css path: (Copy from Chrome Inspector)
#   body tbody > tr:nth-child(3) tbody > tr > td:nth-child(3) > a
# xpath:
#   /html/body/center/table/tbody/tr[3]/td/table/tbody/tr/td[3]/a
 
news1 = []
news2 = []
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
 
    # has title content
    if hasattr(x, 'text'):
            titleD = x.text
            urlD = x.get('href')
            # print titleD, urlD
            news2.append( (titleD, urlD) )
 
    # has comment area
    if (y is not None):
        hid = y.get('href')[8:]
        # print hid
        news1.append(hid)
        added_hid = True
 
    # Patch for edge case where Title exists but no Comment and Hack news id.
    # Second row in each group (3 rows) should contains hack news id, otherwise mock one up.
    if rowCounter % 3 == 2:
        #add pseudo hid
        if added_hid == False:
            news1.append(88888888)
 
# db write
s = session()
 
# 30 is the page count, get rid of news1[30] because it's edge case.
for i in range(0, 30):
    hid = news1[i]
    title, url = news2[i]
    #print hid, title, url
 
    checkOld = s.query(Record).filter(Record.hid == hid).count()
    if (checkOld == 0):
        s.add(Record(hid=hid, title=title, url=url))
 
s.commit()