import os
from typing import Optional
from enum import Enum

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from fastapi import FastAPI
from fastapi_rss import (
    RSSFeed, RSSResponse, Item, Category, CategoryAttrs,
)
from pydantic import BaseModel

from db.models import Site, Victim

def make_session():
    path = f"sqlite:///{os.getenv('RW_DB_PATH', ':memory:')}"
    engine = create_engine(path)
    Session = sessionmaker(bind=engine, expire_on_commit=False) 
    return Session()

def close_session(session: Session):
    session.close()

class RssMode(str, Enum):
    TABLE = "TABLE"
    REGULAR = "REGULAR"

class EmojiAvailability(str, Enum):
    AVAILABLE = "✅"
    REMOVED = "❌"


app = FastAPI(redoc_url=None)

@app.get('/rss')
async def root(template: Optional[RssMode] = RssMode.REGULAR, hide_removed: Optional[bool] = False, search: Optional[str] = None):
    sess = make_session()

    conditions = []
    conditions.append(Victim.site_id == Site.id)
    if hide_removed:
        conditions.append(Victim.removed == False)
    if search:
        conditions.append(Victim.name.like(f"%{search}%"))
    
    vs = sess.query(Victim, Site).filter(*conditions).all()
    
    items=[]
    for v in vs:
        leak_desc = f"""<p>Leak available on {v.Site.actor} for <a href="{v.Victim.url}">{v.Victim.name}</a></p>"""
        
        if template == RssMode.REGULAR:
            leak_desc = f"""
                <p>A new leak has been published on <a href="{v.Site.url}">{v.Site.actor}</a> about <b>{v.Victim.name}</b>:
                <ul>
                <li>It is available at: {v.Victim.url}</li>
                <li>First seen: {v.Victim.first_seen}</li>
                <li>Last seen: {v.Victim.last_seen}</li>
                <li>Availability: {not v.Victim.removed}</li>
                </ul></p>
                """
        
        if template == RssMode.TABLE:
            leak_desc = f"""
                <table>
                <tr><td>Name</td><td>{v.Victim.name}</td><tr>
                <tr><td>URL</td><td>{v.Victim.url}</td><tr>
                <tr><td>Platform</td><td><a href="{v.Site.url}">{v.Site.actor}</a></td><tr>
                <tr><td>First seen</td><td>{v.Victim.first_seen}</td></tr>
                <tr><td>Last seen</td><td>{v.Victim.last_seen}</td></tr>
                <tr><td>Availability</td><td>{EmojiAvailability.REMOVED if bool(v.Victim.removed) else EmojiAvailability.AVAILABLE}</td></tr>
                </table>
                """
        
        item = Item(
            title=f"Leak available: {v.Victim.name}", 
            link=v.Victim.url, 
            description=leak_desc, 
            pub_date=v.Victim.published, 
            author=v.Site.actor)
        items.append(item)

    feed_data = {
        'title': 'Ransonwatch RSS feed',
        'link': 'https://127.0.0.1',
        'description': 'I expose an RSS feed with content of database',
        'language': 'en-us',
        'ttl': 40,
        'item': items
    }

    close_session(sess)

    feed = RSSFeed(**feed_data)
    return RSSResponse(feed)

