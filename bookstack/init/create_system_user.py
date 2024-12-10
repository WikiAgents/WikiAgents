import os
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

from shared.agent_onboarding import AgentOnboarding
from shared.agents_redis_cache import AgentsRedisCache
from shared.models import RedisAgent


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

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

redis = Redis("redis")


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


with SessionLocal() as session:
    main_agent_name = "WikiAgent"
    existing_user = session.query(User).filter_by(name=main_agent_name).first()
    if not existing_user:
        user = User(
            name=main_agent_name,
            email="wikiagent@wikiagents.local",
            password=hash_password("foobar"),
            slug="wikiagent",
            external_auth_id="",
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_role = UserRole(user_id=user.id, role_id=1)
        session.add(user_role)
        session.commit()

        api_token = APIToken(
            name=f"{main_agent_name} Token",
            token_id=WA_TOKEN,
            secret=hash_password(WA_SECRET),
            user_id=user.id,
            expires_at=date(2149, 1, 1),
        )
        session.add(api_token)
        session.commit()
        AgentsRedisCache().update_agent(
            RedisAgent(
                name=main_agent_name,
                type="wikiagent",
                token_id=WA_TOKEN,
                token_secret=WA_SECRET,
            )
        )
        # redis.hset(f"agent:{main_agent_name}", mapping={"token_id": WA_TOKEN, "token_secret": WA_SECRET})

    docling = session.query(User).filter_by(name="Docling").first()
    if not docling:
        # Onboard transcriber (has no page yet)
        AgentOnboarding().onboard_agent(
            RedisAgent(
                name="Docling",
                type="transcriber",
                command="/docling",
                code_path="agents.transcribers.docling.agent.DoclingTranscriber",
            )
        )
