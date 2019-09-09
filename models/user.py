from pymongo import IndexModel
from pymongoext import Model, DictField, StringField, ListField, NumberField, DateTimeField
from pymongoext.manipulators import Manipulator
from models import BaseModel
from datetime import datetime, timedelta
from utils import default

config = default.get("config.json")


class User(BaseModel):
    __schema__ = DictField(dict(
        user_id=StringField(required=True),
        name=StringField(required=True),
        discriminator=StringField(required=True),
        quote_to=StringField(default='USD'),
        price_list=DictField(dict(
            coins=ListField(default=[])
        )),
        item_list=ListField(default=[]),
        game=DictField(dict(
            money=NumberField(default=config.economy.start_money),
            in_pocket=NumberField(default=0),
            portfolio=DictField(dict(
                transactions=ListField(default=[]),
                coins=ListField(default=[])
            )),
            wage=NumberField(default=config.economy.start_wage),
            total_wages=NumberField(default=0),
            last_wage=DateTimeField(default=datetime.now() - timedelta(hours=1)),
            created_at=DateTimeField(default=datetime.now())
        ))
    ))

    __indexes__ = [IndexModel('user_id', unique=True)]

    class InventoryAggregateManipulator(Manipulator):
        def transform_outgoing(self, doc, model):
            cur = User.aggregate([
                {"$lookup": {
                    "from": "item",
                    "foreignField": "_id",
                    "localField": "item_list",
                    "as": "inventory"
                }},
                {"$match": {"_id": doc['_id']}}
            ])
            for doc in cur:
                return doc

        def transform_incoming(self, doc, model, action):
            if 'inventory' in doc:
                del doc['inventory']
            return doc

    class RoundGameBalanceManipulator(Manipulator):

        def transform_incoming(self, doc, model, action):
            if 'game' in doc:
                if 'money' in doc['game']:
                    int(round(doc['game']['money']))
                if 'in_pocket' in doc['game']:
                    int(round(doc['game']['in_pocket']))
            return doc
