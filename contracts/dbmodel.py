###########################################################################################
# dbmodel - database model for contracts database
#
#       Date            Author          Reason
#       ----            ------          ------
#       06/29/18        Lou King        Create
#
#   Copyright 2018 Lou King.  All rights reserved
###########################################################################################

# standard
import os.path
from ConfigParser import SafeConfigParser

# pypi
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from flask_security import current_user, UserMixin, RoleMixin

# set up database - SQLAlchemy() must be done after app.config SQLALCHEMY_* assignments
db = SQLAlchemy()
Table = db.Table
Column = db.Column
Integer = db.Integer
Float = db.Float
Boolean = db.Boolean
String = db.String
Date = db.Date
Time = db.Time
DateTime = db.DateTime
Sequence = db.Sequence
Enum = db.Enum
UniqueConstraint = db.UniqueConstraint
ForeignKey = db.ForeignKey
relationship = db.relationship
backref = db.backref
object_mapper = db.object_mapper
Base = db.Model

# some string sizes
URL_LEN = 2047      # https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
EVENT_LEN = 256
DATE_LEN = 10
TIME_LEN = 5
DATETIME_LEN = DATE_LEN + 1 + TIME_LEN
STATE_LEN = 16
NAME_LEN = 256
EMAIL_LEN = 100
SERVICE_LEN = 20
FIELD_LEN = 30
COURSE_LEN = 50
ROLENAME_LEN = 32
ADDRESS_LEN = 100
FEETYPE_LEN = 15
ALGNAME_LEN = 10
ORGANIZATION_LEN = 30
NOTES_LEN = 1024
DESCR_LEN = 512
FID_LEN = 128   # not taking chance, but 44 per https://stackoverflow.com/questions/38780572/is-there-any-specific-for-google-drive-file-id
SNAILADDR_LEN = 256
PHONE_LEN = 13
CONTRACT_TYPE_LEN = 30
CONTRACK_BLOCK_LEN = 2048
CONTRACT_BLOCK_TYPE_LEN = 20

class Lead(Base):
    __tablename__ = 'lead'
    id          = Column( Integer, primary_key=True )
    name        = Column( String(NAME_LEN) )
    email       = Column( String(EMAIL_LEN) )

class ContractType(Base):
    __tablename__ = 'contracttype'
    id              = Column( Integer, primary_key=True )
    contractType    = Column( String(CONTRACT_TYPE_LEN) )
    description     = Column( String(DESCR_LEN) )
    
class ContractBlockType(Base):
    __tablename__ = 'contractblocktype'
    id              = Column( Integer, primary_key=True )
    blockType       = Column( String(CONTRACT_BLOCK_TYPE_LEN) )
    description     = Column( String(DESCR_LEN) )
    
class Contract(Base):
    __tablename__ = 'contract'
    id                  = Column( Integer, primary_key=True )
    contractTypeId      = Column( Integer, ForeignKey('contracttype.id' ) )
    contractType        = relationship( 'ContractType', backref='contracts', lazy=True )
    blockPriority       = Column( Integer, nullable=False )
    contractBlockTypeId = Column( Integer, ForeignKey('contractblocktype.id' ) )
    contractBlockType   = relationship( 'ContractBlockType', backref='contracts', lazy=True )
    block               = Column( String(CONTRACK_BLOCK_LEN) )

class FeeType(Base):
    __tablename__ = 'feetype'
    id          = Column( Integer, primary_key=True )
    feeType     = Column( String(FEETYPE_LEN) ) # e.g., fixed, basedOnField, addOn
    # feeHandling = Column( String(ALGNAME_LEN) ) # e.g., fixed, basedOnField, addOn
    description = Column( String(DESCR_LEN) )

# see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To Many
eventservice_table = Table('eventservice', Base.metadata,
    Column( 'event_id', Integer, ForeignKey('event.id' ) ),
    Column( 'service_id', Integer, ForeignKey('service.id' ), nullable=False ),
    )

class Service(Base):
    __tablename__ =  'service'
    id                = Column( Integer, primary_key=True ) 
    service           = Column( String(SERVICE_LEN) )
    serviceLong       = Column( String(DESCR_LEN) )
    isCalendarBlocked = Column( Boolean )
    feeTypeId         = Column( Integer, ForeignKey('feetype.id' ), nullable=False )
    feeType           = relationship( 'FeeType', backref='services', lazy=True )
    fee               = Column( Integer )              # must be set for feeType = fixed
    basedOnField      = Column( String(FIELD_LEN) )    # must be set for feeType = basedOnField

# for a given service, fieldValues are sorted
# fee is based on the largest fieldValue <= basedOnField 
class FeeBasedOn(Base):
    __tablename__ =  'feebasedon'
    id         = Column( Integer, primary_key=True )
    serviceId  = Column( Integer, ForeignKey('service.id' ), nullable=False )
    service    = relationship( 'Service', backref='feeBasedOns', lazy=True )
    fieldValue = Column( Integer )
    fee        = Column( Integer )

class Course(Base):
    __tablename__ = 'course'
    id          = Column( Integer, primary_key=True ) 
    course      = Column( String(COURSE_LEN) )
    address     = Column( String(ADDRESS_LEN) )
    isStandard  = Column( Boolean ) # true if standard city course

# see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To Many
eventaddon_table = Table('eventaddon', Base.metadata,
    Column( 'event_id', Integer, ForeignKey('event.id' ) ),
    Column( 'addon_id', Integer, ForeignKey('addon.id' ), nullable=False ),
    )

class AddOn(Base):
    __tablename__ = 'addon'
    id          = Column( Integer, primary_key=True ) 
    shortDescr  = Column( String(SERVICE_LEN) )
    longDescr   = Column( String(NOTES_LEN) )
    fee         = Column( Integer )
    # eventId     = Column( Integer, ForeignKey('event.id' ), nullable=False )

class State(Base):
    __tablename__ = 'state'
    id          = Column( Integer, primary_key=True ) 
    state       = Column( String(STATE_LEN) )
    description = Column( String(DESCR_LEN) )

class Client(Base):
    __tablename__ = 'client'
    id                  = Column( Integer, primary_key=True ) 
    client              = Column( String(ORGANIZATION_LEN) )
    clientUrl           = Column( String(URL_LEN) )
    contactFirstName    = Column( String(NAME_LEN) )
    contactFullName     = Column( String(NAME_LEN) )
    contactEmail        = Column( String(EMAIL_LEN) )
    clientPhone         = Column( String(SNAILADDR_LEN) )
    clientAddr          = Column( String(PHONE_LEN) )

class Event(Base):
    __tablename__ = 'event'
    id                  = Column( Integer, primary_key=True )
    event               = Column( String(EVENT_LEN) )
    date                = Column( String(DATE_LEN) )
    eventUrl            = Column( String(URL_LEN) )
    registrationUrl     = Column( String(URL_LEN) )

    # see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To One
    state_id            = Column( Integer, ForeignKey('state.id') )
    state               = relationship( 'State', backref='events', lazy=True )
    lead_id             = Column( Integer, ForeignKey('lead.id') )
    lead                = relationship( 'Lead', backref='events', lazy=True )
    course_id           = Column( Integer, ForeignKey('course.id') )
    course              = relationship( 'Course', backref='events', lazy=True )
    client_id           = Column( Integer, ForeignKey('client.id') )
    client              = relationship( 'Client', backref='events', lazy=True )

    mainStartTime       = Column( String(TIME_LEN) )
    mainTimeAmPm        = Column( Enum('am', 'pm') )
    mainDistance        = Column( Float )
    mainDistanceUnits   = Column( Enum('M',  'km') )
    funStartTime        = Column( String(TIME_LEN) )
    funTimeAmPm         = Column( Enum('am', 'pm') )
    funDistance         = Column( Float )
    funDistanceUnits    = Column( Enum('M', 'km') )

    # see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To Many
    services            = relationship( 'Service', secondary=eventservice_table, backref='events', lazy=True )
    finishersPrevYear   = Column( Integer )
    finishersCurrYear   = Column( Integer )
    maxParticipants     = Column( Integer )
    # see http://docs.sqlalchemy.org/en/latest/orm/basic_relationships.html Many To Many
    addOns              = relationship( 'AddOn', secondary=eventaddon_table, backref='events', lazy=True )
    contractSentDate    = Column( String(DATETIME_LEN) )
    contractSignedDate  = Column( String(DATETIME_LEN) )
    invoiceSentDate     = Column( String(DATE_LEN) )
    paymentRecdDate     = Column( String(DATE_LEN) )
    isOnCalendar        = Column( Boolean )
    contractDocId       = Column( String(FID_LEN) )
    notes               = Column( String(NOTES_LEN) )

# adapted from 
#   http://flask-dance.readthedocs.io/en/latest/backends.html#sqlalchemy
#   
class RolesUsers(Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))

class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(ROLENAME_LEN), unique=True)
    description = Column(String(DESCR_LEN))

class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email               = Column( String(EMAIL_LEN), unique=True )
    name                = Column( String(NAME_LEN) )
    given_name          = Column( String(NAME_LEN) )
    last_login_at       = Column( DateTime() )
    current_login_at    = Column( DateTime() )
    last_login_ip       = Column( String(100) )
    current_login_ip    = Column( String(100) )
    login_count         = Column( Integer )
    active              = Column( Boolean() )
    confirmed_at        = Column( DateTime() )
    roles               = relationship('Role', secondary='roles_users',
                          backref=backref('users', lazy='dynamic'))
