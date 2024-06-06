from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy.orm import relationship

from data.database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text, Enum, func, TIMESTAMP

class UserStatus(PyEnum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    DEACTIVATED = "DEACTIVATED"


class User(Base):
    __tablename__ = "users"

    id = Column(Text, primary_key=True)
    email = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    is_internal = Column(Boolean, nullable=False, default=False)
    profile_image = Column(Text)
    organization_id = Column(Text, ForeignKey("organizations.id"), nullable=True)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.PENDING)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


    def set_status_active(self):
        self.status = UserStatus.ACTIVE

    def set_status_pending(self):
        self.status = UserStatus.PENDING


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Text, primary_key=True)
    user_id = Column(Text, ForeignKey("users.id"))
    jti = Column(Text, nullable=False, default="")
    expires_at = Column(DateTime, nullable=False, default=datetime.now)
    end_at = Column(DateTime)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    impersonator_id = Column(Text, nullable=True)

    user = relationship("User")


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    image = Column(Text, nullable=True)
    hd = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
