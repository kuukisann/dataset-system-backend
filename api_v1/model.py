from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import relationship, sessionmaker
from api_v1 import app
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature

engine = create_engine('mysql+pymysql://{}:{}@localhost:3306/{}'.
                       format(app.config['DB_USERNAME'], app.config['DB_PWD'], app.config['DB_NAME']), pool_size=20)
Base = declarative_base()


def create_session():
    Session = sessionmaker(bind=engine)
    return Session()


class DataSet(Base):
    __tablename__ = 'data_set'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, index=True)
    type = Column(String(128), nullable=False)
    creator = Column(String(256), nullable=False)
    createTime = Column(DateTime, nullable=False)
    modifyTime = Column(DateTime, nullable=False)
    resources = relationship("Resource", backref='data_set')

    def __repr__(self):
        return "<DataSet(id='%s', name='%s', creator='%s', createTime='%s', modifyTime='%s')>" % (
            self.id, self.name, self.creator, self.createTime, self.modifyTime)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'creator': self.creator,
            'createTime': self.createTime,
            'modifyTime': self.modifyTime
        }


class Resource(Base):
    __tablename__ = 'resource'

    id = Column(Integer, primary_key=True)
    dataSetID = Column(Integer, ForeignKey('data_set.id', onupdate='CASCADE', ondelete='CASCADE'), index=True)
    src = Column(String(512), nullable=False)
    type = Column(String(128), nullable=False)
    createTime = Column(DateTime, nullable=False)
    modifyTime = Column(DateTime, nullable=False)
    ifPositive = Column(Boolean, nullable=False)
    filename = Column(String(256), nullable=False)
    nameExtension = Column(String(32), nullable=False)
    fileMsg = Column(String(512), nullable=False)
    environment = Column(String(128))

    def __repr__(self):
        return "<Resource(id='%s', dataSetID='%s', src='%s', type='%s', createTime='%s', modifyTime='%s', " \
               "ifPositive='%s', filename='%s', nameExtension='%s', fileMsg='%s', environment='%s')>" % (
                   self.id, self.dataSetID, self.src, self.type, self.createTime, self.modifyTime,
                   self.ifPositive, self.filename, self.nameExtension, self.fileMsg, self.environment)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'src': self.src,
            'type': self.type,
            'createTime': self.createTime,
            'modifyTime': self.modifyTime,
            'ifPositive': self.ifPositive,
            'filename': self.filename,
            'nameExtension': self.nameExtension,
            'fileMsg': self.fileMsg,
            'environment': self.environment,
            'dataSetID': self.dataSetID
        }


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(64), nullable=False, index=True, unique=True)
    password = Column(String(256), nullable=False)
    role = Column(String(30), CheckConstraint("role in ('admin', 'user')"), nullable=False)

    def __repr__(self):
        return "<User(id='%s', username='%s', password='%s')>" % (
            self.id, self.username, self.password)

    @staticmethod
    def hash_password(password):
        return pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def generate_auth_token(self, expiration=3600 * 24):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        return data

    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username
        }
