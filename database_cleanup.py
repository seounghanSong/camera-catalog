# usr/bin/python3.7

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Company, Camera, Base

engine = create_engine('sqlite:///camerastudio.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# IDEA: Need to clean up the existing rows before insert the initial db rows
# only truncate the table
meta = db.metadata
for table in reversed(meta.sorted_tables):
    print('Clear table %s' % table)
    session.execute(table.delete())
session.commit()

# Create dummy user
ADMIN = User(name="appuser", email="appuser@studio.com", picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(ADMIN)
session.commit()

# Camera for Fujifilm
company_fujifilm = Company(user_id=1, name="Fujifilm")
session.add(company_fujifilm)
session.commit()

camera_x_t20 = Camera(user_id=1,
                      name="x-t20",
                      description="It's mine",
                      price="$1,099",
                      company_id=1)
session.add(camera_x_t20)
session.commit()

camera_x_t2 = Camera(user_id=1,
                      name="x-t2",
                      description="Expensive",
                      price="$1,499",
                      company_id=1)
session.add(camera_x_t2)
session.commit()

# Camera for Sony
company_sony = Company(user_id=1, name="Sony")
session.add(company_sony)
session.commit()

camera_s_2 = Camera(user_id=1,
                      name="s2",
                      description="a6900 description",
                      price="$1,699",
                      company_id=2)
session.add(camera_s_2)
session.commit()

camera_s_1 = Camera(user_id=1,
                      name="s1",
                      description="a7200 description",
                      price="$1,899",
                      company_id=2)
session.add(camera_s_1)
session.commit()

# Camera for Sony
company_canon = Company(user_id=1, name="Canon")
session.add(company_canon)
session.commit()

camera_a_6900 = Camera(user_id=1,
                      name="a6900",
                      description="a6900 description",
                      price="$1,699",
                      company_id=3)
session.add(camera_a_6900)
session.commit()

camera_a_7200 = Camera(user_id=1,
                      name="a7200",
                      description="a7200 description",
                      price="$1,899",
                      company_id=3)
session.add(camera_a_7200)
session.commit()

print("successfully added all camera items!!")
