from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from autochannel.models import Guild, Category

engine = create_engine('sqlite:////tmp/site.db')
session = Session(engine)
guild = session.query(Guild).get(321048288574963722)
cats = session.query(Category).with_entities(Category.id, Category.enabled, Category.prefix).filter_by(guild_id=321048288574963722).all()


print(cats)
session.close()


# cats = list(Category.query.with_entities(Category.id).filter_by(guild_id=guild_id).all())