# Import standard library modules
from typing import Callable

# Import third-party library modules
from cuid2 import cuid_wrapper
from sqlalchemy import (
    NVARCHAR,
    Boolean,
    Column,
    Float,
    ForeignKey,
    Index,
    Integer,
    and_,
    asc,
    desc,
    func,
    null,
)
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import false

Base = declarative_base()
metadata = Base.metadata

cuid_generator: Callable[[], str] = cuid_wrapper()


class User(Base):
    __tablename__ = "User"

    id = Column(
        NVARCHAR(length=1000),
        primary_key=True,
        autoincrement=False,
        nullable=False,
        default=cuid_generator,
    )
    name = Column(NVARCHAR(length=1000), nullable=True)
    email = Column(NVARCHAR(length=1000), nullable=True, unique=True)
    email_verified = Column(DATETIME2(), nullable=True)
    image = Column(NVARCHAR(length=1000), nullable=True)
    createdAt = Column(DATETIME2(), nullable=False, default=func.now())
    updatedAt = Column(
        DATETIME2(), nullable=False, onupdate=func.now(), default=func.now()
    )

    conversations = relationship("Conversation", back_populates="user")
    agentConversationSessions = relationship(
        "AgentConversationSession", back_populates="user"
    )
    knowledgebaseConversations = relationship(
        "KnowledgebaseConversation", back_populates="user"
    )


class AnalyticsEvent(Base):
    __tablename__ = "AnalyticsEvent"

    id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False)
    eventName = Column(NVARCHAR(length=1000), nullable=False)
    user = Column(NVARCHAR(length=1000), nullable=True)
    dateCreated = Column(DATETIME2(), nullable=False, default=func.now())
    eventTrigger = Column(NVARCHAR(length=1000), nullable=True)
    eventMetadata = Column(NVARCHAR(None), nullable=False)

    __table_args__ = (Index("eventName_dateCreated_idx", "eventName", "dateCreated"),)


# Relationship Manager Module


class MessageSource(Base):
    __tablename__ = "MessageSource"

    id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False)
    messageId = Column(NVARCHAR(length=1000), ForeignKey("Message.id"), nullable=False)
    message = relationship("Message", back_populates="messageSources")

    link = Column(NVARCHAR(length=1000), nullable=False)
    filename = Column(NVARCHAR(length=1000), nullable=False)

    chunks = Column(NVARCHAR(None), nullable=False)

    dateIngested = Column(DATETIME2(), nullable=False)
    dateCreated = Column(DATETIME2(), nullable=False, default=func.now())
    dateDeleted = Column(DATETIME2(), nullable=True)


class MessageSuggestion(Base):
    __tablename__ = "MessageSuggestion"

    id = Column(
        NVARCHAR(length=1000),
        primary_key=True,
        autoincrement=False,
        nullable=False,
        default=cuid_generator,
    )
    suggestion = Column(NVARCHAR(None), nullable=False)
    createdAt = Column(DATETIME2(), nullable=True, default=func.now())
    messageId = Column(NVARCHAR(length=1000), ForeignKey("Message.id"), nullable=False)
    message = relationship("Message", back_populates="messageSuggestions")


class RewriteResponse(Base):
    __tablename__ = "RewriteResponse"

    id = Column(
        NVARCHAR(length=1000),
        primary_key=True,
        autoincrement=False,
        nullable=False,
        default=cuid_generator,
    )
    messageId = Column(NVARCHAR(length=1000), ForeignKey("Message.id"), nullable=False)
    message = relationship("Message", back_populates="messageRewriteResponses")

    instruction = Column(NVARCHAR(length=1000), nullable=False)
    rewriteText = Column(NVARCHAR(None), nullable=False)

    createdAt = Column(DATETIME2(), nullable=False, default=func.now())


class Message(Base):
    __tablename__ = "Message"

    id = Column(
        NVARCHAR(length=1000),
        primary_key=True,
        autoincrement=False,
        nullable=False,
        default=cuid_generator,
    )
    conversationId = Column(
        NVARCHAR(length=1000), ForeignKey("Conversation.id"), nullable=False
    )
    conversation = relationship("Conversation", back_populates="messages")
    is_bot = Column(Boolean(), nullable=False, server_default=false())
    text = Column(NVARCHAR(None), nullable=False)
    token_count = Column(Integer(), nullable=False)

    rating = Column(Boolean(), nullable=True)
    ratingData = Column(NVARCHAR(None), nullable=True)
    ratingText = Column(NVARCHAR(None), nullable=True)

    messageSources = relationship(
        "MessageSource",
        primaryjoin=and_(
            MessageSource.messageId == id, MessageSource.dateDeleted == null()
        ),
        back_populates="message",
        order_by=asc(MessageSource.id),
    )
    messageSuggestions = relationship(
        "MessageSuggestion",
        back_populates="message",
        order_by=asc(MessageSuggestion.id),
    )
    messageRewriteResponses = relationship(
        "RewriteResponse", back_populates="message", order_by=asc(RewriteResponse.id)
    )

    createdAt = Column(DATETIME2(), nullable=False, default=func.now())
    deletedAt = Column(DATETIME2(), nullable=True)


class Conversation(Base):
    __tablename__ = "Conversation"

    id = Column(
        NVARCHAR(length=1000),
        primary_key=True,
        autoincrement=False,
        nullable=False,
        default=cuid_generator,
    )
    title = Column(NVARCHAR(length=1000), nullable=False)
    userId = Column(NVARCHAR(length=1000), ForeignKey("User.id"), nullable=False)
    user = relationship("User", back_populates="conversations")

    messages = relationship(
        "Message",
        back_populates="conversation",
        primaryjoin=and_(Message.conversationId == id, Message.deletedAt == null()),
        order_by=desc(Message.createdAt),
    )

    lastMessageDate = Column(DATETIME2(), nullable=False, default=func.now())

    createdAt = Column(DATETIME2(), nullable=False, default=func.now())
    updatedAt = Column(
        DATETIME2(), nullable=False, onupdate=func.now(), default=func.now()
    )
    deletedAt = Column(DATETIME2(), nullable=True)
    pinnedAt = Column(DATETIME2(), nullable=True)


# Librarian Module
class KnowledgebaseMessageSource(Base):
    __tablename__ = "KnowledgebaseMessageSource"

    id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False)
    messageId = Column(
        NVARCHAR(length=1000), ForeignKey("KnowledgebaseMessage.id"), nullable=False
    )
    message = relationship("KnowledgebaseMessage", back_populates="messageSources")

    link = Column(NVARCHAR(length=1000), nullable=False)
    filename = Column(NVARCHAR(length=1000), nullable=False)

    chunks = Column(NVARCHAR(None), nullable=False)

    dateIngested = Column(DATETIME2(), nullable=False)
    dateCreated = Column(DATETIME2(), nullable=False, default=func.now())
    dateDeleted = Column(DATETIME2(), nullable=True)


class KnowledgebaseMessageSuggestion(Base):
    __tablename__ = "KnowledgebaseMessageSuggestion"

    id = Column(
        NVARCHAR(length=1000),
        primary_key=True,
        autoincrement=False,
        nullable=False,
        default=cuid_generator,
    )
    suggestion = Column(NVARCHAR(None), nullable=False)
    createdAt = Column(DATETIME2(), nullable=True, default=func.now())
    messageId = Column(
        NVARCHAR(length=1000), ForeignKey("KnowledgebaseMessage.id"), nullable=False
    )
    message = relationship("KnowledgebaseMessage", back_populates="messageSuggestions")


class KnowledgebaseRewriteResponse(Base):
    __tablename__ = "KnowledgebaseRewriteResponse"

    id = Column(
        NVARCHAR(length=1000),
        primary_key=True,
        autoincrement=False,
        nullable=False,
        default=cuid_generator,
    )
    messageId = Column(
        NVARCHAR(length=1000), ForeignKey("KnowledgebaseMessage.id"), nullable=False
    )
    message = relationship(
        "KnowledgebaseMessage", back_populates="messageRewriteResponses"
    )

    instruction = Column(NVARCHAR(length=1000), nullable=False)
    rewriteText = Column(NVARCHAR(None), nullable=False)

    createdAt = Column(DATETIME2(), nullable=False, default=func.now())


class KnowledgebaseMessage(Base):
    __tablename__ = "KnowledgebaseMessage"

    id = Column(
        NVARCHAR(length=1000),
        primary_key=True,
        autoincrement=False,
        nullable=False,
        default=cuid_generator,
    )
    conversationId = Column(
        NVARCHAR(length=1000),
        ForeignKey("KnowledgebaseConversation.id"),
        nullable=False,
    )
    conversation = relationship("KnowledgebaseConversation", back_populates="messages")
    is_bot = Column(Boolean(), nullable=False, server_default=false())
    text = Column(NVARCHAR(None), nullable=False)
    token_count = Column(Integer(), nullable=False)

    rating = Column(Boolean(), nullable=True)
    ratingData = Column(NVARCHAR(None), nullable=True)
    ratingText = Column(NVARCHAR(None), nullable=True)

    messageSources = relationship(
        "KnowledgebaseMessageSource",
        primaryjoin=and_(
            KnowledgebaseMessageSource.messageId == id,
            KnowledgebaseMessageSource.dateDeleted == null(),
        ),
        back_populates="message",
        order_by=asc(KnowledgebaseMessageSource.id),
    )
    messageSuggestions = relationship(
        "KnowledgebaseMessageSuggestion",
        back_populates="message",
        order_by=asc(KnowledgebaseMessageSuggestion.id),
    )
    messageRewriteResponses = relationship(
        "KnowledgebaseRewriteResponse",
        back_populates="message",
        order_by=asc(KnowledgebaseRewriteResponse.id),
    )

    createdAt = Column(DATETIME2(), nullable=False, default=func.now())
    deletedAt = Column(DATETIME2(), nullable=True)


class KnowledgebaseConversation(Base):
    __tablename__ = "KnowledgebaseConversation"

    id = Column(
        NVARCHAR(length=1000),
        primary_key=True,
        autoincrement=False,
        nullable=False,
        default=cuid_generator,
    )
    title = Column(NVARCHAR(length=1000), nullable=False)
    userId = Column(NVARCHAR(length=1000), ForeignKey("User.id"), nullable=False)
    user = relationship("User", back_populates="knowledgebaseConversations")

    messages = relationship(
        "KnowledgebaseMessage",
        back_populates="conversation",
        primaryjoin=and_(
            KnowledgebaseMessage.conversationId == id,
            KnowledgebaseMessage.deletedAt == null(),
        ),
        order_by=desc(KnowledgebaseMessage.createdAt),
    )

    lastMessageDate = Column(DATETIME2(), nullable=False, default=func.now())

    createdAt = Column(DATETIME2(), nullable=False, default=func.now())
    updatedAt = Column(
        DATETIME2(), nullable=False, onupdate=func.now(), default=func.now()
    )
    deletedAt = Column(DATETIME2(), nullable=True)
    pinnedAt = Column(DATETIME2(), nullable=True)


# Train with AI Module
class AgentMessage(Base):
    __tablename__ = "AgentMessage"

    id = Column(
        NVARCHAR(length=1000),
        primary_key=True,
        autoincrement=False,
        nullable=False,
        default=cuid_generator,
    )
    conversationId = Column(
        NVARCHAR(length=1000), ForeignKey("AgentConversation.id"), nullable=False
    )
    conversation = relationship("AgentConversation", back_populates="messages")
    is_bot = Column(Boolean(), nullable=False, server_default=false())
    text = Column(NVARCHAR(None), nullable=False)
    token_count = Column(Integer, nullable=False)

    rating = Column(Boolean(), nullable=True)
    ratingData = Column(NVARCHAR(None), nullable=True)
    ratingText = Column(NVARCHAR(None), nullable=True)

    createdAt = Column(DATETIME2(), nullable=False, default=func.now())
    deletedAt = Column(DATETIME2(), nullable=True)

    duration = Column(Integer(), nullable=False)


class AgentConversation(Base):
    __tablename__ = "AgentConversation"

    id = Column(
        NVARCHAR(length=1000),
        primary_key=True,
        autoincrement=False,
        nullable=False,
        default=cuid_generator,
    )
    title = Column(NVARCHAR(length=1000), nullable=False)
    userId = Column(NVARCHAR(length=1000), nullable=False)

    sessionId = Column(
        Integer, ForeignKey("AgentConversationSession.id"), unique=True, nullable=False
    )
    session = relationship("AgentConversationSession", back_populates="conversation")

    messages = relationship("AgentMessage", back_populates="conversation")

    lastMessageDate = Column(DATETIME2(), nullable=False, default=func.now())

    createdAt = Column(DATETIME2(), nullable=False, default=func.now())
    updatedAt = Column(
        DATETIME2(), nullable=False, onupdate=func.now(), default=func.now()
    )
    deletedAt = Column(DATETIME2(), nullable=True)
    pinnedAt = Column(DATETIME2(), nullable=True)

    duration = Column(Integer(), nullable=False)

    scorecard = relationship(
        "AgentConversationScorecard", back_populates="conversation", uselist=False
    )


class AgentConversationSession(Base):
    __tablename__ = "AgentConversationSession"

    id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False)
    agentId = Column(NVARCHAR(length=1000), nullable=False)

    userId = Column(NVARCHAR(length=1000), ForeignKey("User.id"), nullable=False)
    user = relationship("User", back_populates="agentConversationSessions")

    conversation = relationship(
        "AgentConversation", back_populates="session", uselist=False
    )

    dateCreated = Column(DATETIME2(), nullable=False, default=func.now())
    dateDeleted = Column(DATETIME2(), nullable=True)


class AgentConversationSessionMetadata(Base):
    __tablename__ = "AgentConversationSessionMetadata"

    id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False)
    sessionId = Column(Integer(), nullable=False)
    messageId = Column(NVARCHAR(length=1000), nullable=False)
    scoreChangeStreak = Column(Integer(), nullable=False, default=0)
    receptionAnalysis = Column(NVARCHAR(None), nullable=True)
    receptionScore = Column(Float(), default=0.25)
    dateCreated = Column(DATETIME2(), nullable=False, default=func.now())
    dateDeleted = Column(DATETIME2(), nullable=True)


class AgentConversationScorecard(Base):
    __tablename__ = "AgentConversationScorecard"

    id = Column(
        NVARCHAR(length=1000),
        primary_key=True,
        autoincrement=False,
        nullable=False,
        default=cuid_generator,
    )
    conversationId = Column(
        NVARCHAR(length=1000),
        ForeignKey("AgentConversation.id"),
        unique=True,
        nullable=False,
    )
    conversation = relationship("AgentConversation", back_populates="scorecard")

    overallPerformance = Column(NVARCHAR(length=1000), nullable=False)
    bestQuality = Column(NVARCHAR(length=1000), nullable=False)
    areaOfImprovement = Column(NVARCHAR(length=1000), nullable=False)
    duration = Column(NVARCHAR(length=1000), nullable=False)

    categories = relationship(
        "AgentConversationScorecardCategory", back_populates="scorecard"
    )


class AgentConversationScorecardCategory(Base):
    __tablename__ = "AgentConversationScorecardCategory"

    id = Column(
        NVARCHAR(length=1000),
        primary_key=True,
        autoincrement=False,
        nullable=False,
        default=cuid_generator,
    )
    scorecardId = Column(
        NVARCHAR(length=1000),
        ForeignKey("AgentConversationScorecard.id"),
        nullable=False,
    )
    scorecard = relationship("AgentConversationScorecard", back_populates="categories")

    name = Column(NVARCHAR(length=1000), nullable=False)
    rating = Column(NVARCHAR(length=1000), nullable=False)
    analysis = Column(NVARCHAR(None), nullable=False)
    recommendation = Column(NVARCHAR(None), nullable=False)
