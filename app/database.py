from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    notes = relationship('Note', back_populates='user')

class Note(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    created_at = Column(String, nullable=False)
    score_tag = Column(String)
    agreement = Column(String)
    subjectivity = Column(String)
    confidence = Column(String)
    user = relationship('User', back_populates='notes')

class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    subscribed_user_id = Column(Integer, ForeignKey('users.id'))

class DatabaseManager:
    def __init__(self, config):
        self.engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
        self.Session = sessionmaker(bind=self.engine)
        self.metadata = Base.metadata  # Use the Base metadata

    def init_db(self):
        """Create all tables in the database."""
        self.metadata.create_all(self.engine)

    def drop_db(self):
        """Drop all tables from the database."""
        self.metadata.drop_all(self.engine)

    def get_session(self):
        return self.Session()

    def add_user(self, username, password):
        session = self.get_session()
        user = User(username=username, password=password)
        session.add(user)
        session.commit()
        user_id = user.id
        session.close()
        return user_id

    def get_user_by_name(self, username):
        session = self.get_session()
        user = session.query(User).filter_by(username=username).first()
        session.close()
        return user

    def get_user_by_id(self, id):
        session = self.get_session()
        user = session.query(User).filter_by(id=id).first()
        session.close()
        return user

    def add_note(self, user_id, title, body, created_at, score_tag, agreement, subjectivity, confidence):
        session = self.get_session()
        note = Note(
            user_id=user_id,
            title=title,
            body=body,
            created_at=created_at,
            score_tag=score_tag,
            agreement=agreement,
            subjectivity=subjectivity,
            confidence=confidence
        )
        session.add(note)
        session.commit()
        note_id = note.id
        session.close()
        return note_id

    def get_notes(self, user_id):
        session = self.get_session()
        notes = session.query(Note).filter_by(user_id=user_id).all()
        session.close()
        return notes

    def get_note(self, note_id):
        session = self.get_session()
        note = session.query(Note).filter_by(id=note_id).first()
        session.close()
        return note
    
    def get_last_note(self, user_id):
        session = self.get_session()
        note = session.query(Note).filter_by(user_id=user_id).order_by(Note.created_at.desc()).first()
        session.close()
        return note

    def get_all_users(self):
        session = self.get_session()
        users = session.query(User).all()
        session.close()
        return users

    def add_subscription(self, user_id, subscribed_user_id):
        session = self.get_session()
        subscription = Subscription(user_id=user_id, subscribed_user_id=subscribed_user_id)
        session.add(subscription)
        session.commit()
        session.close()

    def get_subscription(self, user_id, subscribed_user_id):
        session = self.get_session()
        subscription = session.query(Subscription).filter_by(user_id=user_id, subscribed_user_id=subscribed_user_id).first()
        session.close()
        return subscription
    
    def get_user_subscriptions(self, user_id):
        session = self.get_session()
        subscription = session.query(Subscription).filter_by(user_id=user_id).all()
        session.close()
        return subscription
    