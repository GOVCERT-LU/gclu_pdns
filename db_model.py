# Copyright (c) 2013 GOVCERT.LU / Georges Toth & Foetz Guy

from sqlalchemy import Column, Integer, BigInteger, SmallInteger, Float, String, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import CIDR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


__all__ = ['Base', 'Session']

Session = scoped_session(sessionmaker())
Base = declarative_base()
filter_rrtype_rev = {1: 'a', 28: 'aaaa', 5: 'cname', 2: 'ns', 15: 'mx', 6: 'soa', 12: 'ptr', 16: 'txt'}


class Domain(Base):
  __tablename__ = 'domain'

  domain_id = Column(BigInteger, primary_key=True, autoincrement=True)
  domain_name = Column(String)
  parent_domain_id = Column(BigInteger, ForeignKey('parent_domain.parent_domain_id'))

  def __str__(self):
    return '{0}'.format(self.domain_name)


class Entry(Base):
  __tablename__ = 'entry'

  entry_id = Column(BigInteger, primary_key=True, autoincrement=True)
  domain_id = Column(BigInteger, ForeignKey('domain.domain_id'))
  type = Column(SmallInteger)
  ttl = Column(Integer)
  value = Column(String)
  first_seen = Column(DateTime)
  last_seen = Column(DateTime)
  count = Column(Integer)

  def __str__(self):
    return 'type: {0}, ttl: {1}, value: {2}, first_seen: {3}, last_seen: {4}, count: {5}'.format(
      filter_rrtype_rev[self.type], self.ttl, self.value, self.first_seen, self.last_seen, self.count)

  def get_dict(self):
    return {'type' : filter_rrtype_rev[self.type], 'ttl' : self.ttl, 'value' : self.value, 'first_seen' : self.first_seen,
            'last_seen' : self.last_seen, 'count' : self.count}


class Parent_Domain(Base):
  __tablename__ = 'parent_domain' 
 
  parent_domain_id = Column(BigInteger, primary_key=True, autoincrement=True)
  parent_domain_name = Column(String)

  def __str__(self):
    return '{0}'.format(self.parent_domain_name)


class Sensor(Base):
  __tablename__ = 'sensor' 

  sensor_id = Column(BigInteger, primary_key=True, autoincrement=True)
  sensor_name = Column(String)

  
class Sensor_Domain(Base):
  __tablename__ = 'sensor_domain' 

  domain_id = Column(BigInteger, ForeignKey('domain.domain_id'), primary_key=True, autoincrement=True) 
  sensor_id = Column(BigInteger, ForeignKey('sensor.sensor_id'), primary_key=True, autoincrement=True) 
  first_seen = Column(DateTime)
  last_seen = Column(DateTime)


class DNS_Server(Base):
  __tablename__ = 'dns_server'
  
  dns_server_id = Column(BigInteger, primary_key=True, autoincrement=True)
  entry_id = Column(BigInteger, ForeignKey('entry.entry_id'))
  ip = Column(CIDR)
  first_seen = Column(DateTime)
  last_seen = Column(DateTime)
  count = Column(Integer)
