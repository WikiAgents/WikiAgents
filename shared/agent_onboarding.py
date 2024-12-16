import os
import random
import string
from datetime import date, datetime

import bcrypt
from redis import Redis
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

from shared.agents_redis_cache import AgentsRedisCache
from shared.bookstack_client import AgentBookStackClient
from shared.models import AgentType, RedisAgent
from shared.utils import extract_section_content


def hash_password(password: str):
    hashed_key = bcrypt.hashpw(
        password.encode(), bcrypt.gensalt(rounds=12, prefix=b"2b")
    )
    return hashed_key.decode().replace("$2b$", "$2y$")


WA_TOKEN = os.environ["WA_TOKEN"]
WA_SECRET = os.environ["WA_SECRET"]

DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_DATABASE = os.environ["DB_DATABASE"]
DB_URL = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@bookstack-db:3306/{DB_DATABASE}"

redis = Redis("redis", 6379)

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(191), nullable=False)
    email = Column(String(191), unique=True, nullable=False)
    password = Column(String(60), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    email_confirmed = Column(Boolean, nullable=False, default=False)
    image_id = Column(Integer, default=0)
    external_auth_id = Column(String(191))
    system_name = Column(String(191))
    slug = Column(String(180), unique=True)


class UserRole(Base):
    __tablename__ = "role_user"

    user_id = Column(Integer, primary_key=True)
    role_id = Column(Integer, primary_key=True)


class APIToken(Base):
    __tablename__ = "api_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    token_id = Column(String, unique=True, nullable=False)
    secret = Column(String, unique=True, nullable=False)
    user_id = Column(Integer)
    expires_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AgentOnboarding:
    def onboard_agent(self, agent: RedisAgent):
        user_id, token_id, token_secret = self.generate_agent_user(agent.name)
        agent.user_id = user_id
        agent.token_id = token_id
        agent.token_secret = token_secret
        AgentsRedisCache().update_agent(agent)

    def offboard_agent(self, name: str):
        user_id = redis.hget(f"agent:{name}", "user_id")
        AgentBookStackClient("WikiAgent").delete_user(user_id.decode())
        AgentsRedisCache().delete_agent(name)

    def generate_agent_user(self, name: str):
        with SessionLocal() as session:
            user = session.query(User).filter_by(name=name).first()
            token_id, token_secret = None, None
            if not user:
                slug = name.replace(" ", "").lower()
                user = User(
                    name=name,
                    email=f"{slug}@wikiagents.local",
                    password=hash_password("foobar"),
                    slug=slug,
                    external_auth_id="",
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                user_role = UserRole(user_id=user.id, role_id=1)
                session.add(user_role)
                session.commit()

                token_id = slug
                token_secret = WA_SECRET
                api_token = APIToken(
                    name=f"{name} Token",
                    token_id=token_id,
                    secret=hash_password(token_secret),
                    user_id=user.id,
                    expires_at=date(2149, 1, 1),
                )
                session.add(api_token)
                session.commit()

            return user.id, token_id, token_secret
