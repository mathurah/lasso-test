from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

class Lead(Base):
    __tablename__ = 'lead'
    urn = Column(String(250), primary_key=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    name = Column(String(250), nullable=False)
    current_company = Column(String(250))
    current_role = Column(String(250))
    previous_company = Column(String(250))
    previous_role = Column(String(250))
    link = Column(String(250), nullable=False)


engine = create_engine('sqlite:///leads.db')
Base.metadata.create_all(engine)