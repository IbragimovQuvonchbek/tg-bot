from datetime import datetime

from sqlalchemy import create_engine, String, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

engine = create_engine('postgresql+psycopg2://postgres:1601@localhost:5432/tg_bot')


class Base(DeclarativeBase):
    pass


class Music(Base):
    __tablename__ = 'music'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[String] = mapped_column(String(255))
    title: Mapped[String] = mapped_column(String(255))
    performer: Mapped[String] = mapped_column(String(255))
    file_id: Mapped[String] = mapped_column(String(255))
    duration: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)
