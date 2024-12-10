import os
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_DATABASE = os.environ["DB_DATABASE"]
DB_URL = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@bookstack-db:3306/{DB_DATABASE}"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    endpoint = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    timeout = Column(Integer, default=60)
    last_error = Column(String, nullable=False, default="")
    last_called_at = Column(DateTime, nullable=True)
    last_errored_at = Column(DateTime, nullable=True)

    tracked_events = relationship("WebhookTrackedEvent", back_populates="webhook")


class WebhookTrackedEvent(Base):
    __tablename__ = "webhook_tracked_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    webhook_id = Column(Integer, ForeignKey("webhooks.id"), nullable=False)
    event = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    webhook = relationship("Webhook", back_populates="tracked_events")


events = [
    "bookshelf_create",
    "bookshelf_update",
    "bookshelf_delete",
    "book_create",
    "book_update",
    "book_delete",
    "page_create",
    "page_update",
    "page_delete",
    "comment_create",
]


def initialize_webhooks():
    with SessionLocal() as session:
        for event in events:
            # Check if webhook already exists for this event
            webhook_name = f"{event}_webhook"
            existing_webhook = (
                session.query(Webhook).filter_by(name=webhook_name).first()
            )

            if not existing_webhook:
                # Create a new webhook
                new_webhook = Webhook(
                    name=webhook_name, endpoint=f"http://api:80/{event}", active=True
                )
                session.add(new_webhook)
                session.commit()  # Commit to get the webhook ID

                # Create a corresponding tracked event
                tracked_event = WebhookTrackedEvent(
                    webhook_id=new_webhook.id, event=event
                )
                session.add(tracked_event)
                try:
                    session.commit()
                    print(f"Initialized webhook for event: {event}")
                except IntegrityError:
                    session.rollback()
                    print(f"Failed to initialize webhook for event: {event}")
            else:
                print(f"Webhook for event '{event}' already exists.")


initialize_webhooks()
