from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
try:
    from My_Budget.sql.set_config import set_config
except:
    import sys
    sys.path.insert(1, r'D:\Learn\Python\repos\First_Flask\My_Budget')
    from sql.set_config import set_config

params = set_config()
engine = create_engine(f'postgresql://{params["user"]}:{params["password"]}@{params["host"]}/{params["database"]}',
                        connect_args= dict(host=params["host"], port=params["port"]))
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)