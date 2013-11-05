from app import db

print "WARNING: This is a destructive action"

db.drop_all()
db.create_all()
