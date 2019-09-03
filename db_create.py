from autochannel import create_app, db

app = create_app()
app.app_context().push()

db.init_app(app)
db.create_all()


# from autochannel.models import Guild, Category
# #guild = Guild.query.get(129238373448679425)
# guild = Guild.query.get(321048288574963722)

# test_guild = Guild(id=129238373448679425) 
#db.session.add(test_guild)
