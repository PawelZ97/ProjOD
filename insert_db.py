from webnotes import db, User

user1 = User(email='admin@example.com', password='123456')
db.session.add(user1)
db.session.commit()