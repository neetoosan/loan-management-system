from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class MemberStatus(enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"


class LoanStatus(enum.Enum):
    PENDING = "Pending"
    ACTIVE = "Active"
    PAID = "Paid"
    DEFAULTED = "Defaulted"


class ContributionType(enum.Enum):
    MONTHLY = "Monthly"
    WEEKLY = "Weekly"
    VOLUNTARY = "Voluntary"


class Member(Base):
    """Member model - stores information about group members"""
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    contact = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    join_date = Column(DateTime, default=datetime.now, nullable=False)
    status = Column(Enum(MemberStatus), default=MemberStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    loans = relationship("Loan", back_populates="member", cascade="all, delete-orphan")
    contributions = relationship("Contribution", back_populates="member", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Member(id={self.id}, name='{self.name}', status={self.status})>"


class Loan(Base):
    """Loan model - stores loan information for members"""
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    amount = Column(Float, nullable=False)
    interest_rate = Column(Float, default=0.0, nullable=False)  # Interest rate in percentage
    start_date = Column(DateTime, default=datetime.now, nullable=False)
    end_date = Column(DateTime, nullable=True)
    status = Column(Enum(LoanStatus), default=LoanStatus.PENDING, nullable=False)
    total_interest = Column(Float, default=0.0, nullable=False)
    amount_repaid = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    member = relationship("Member", back_populates="loans")
    repayments = relationship("LoanRepayment", back_populates="loan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Loan(id={self.id}, member_id={self.member_id}, amount={self.amount}, status={self.status})>"


class LoanRepayment(Base):
    """Loan Repayment model - tracks individual loan repayments"""
    __tablename__ = "loan_repayments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    amount_paid = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.now, nullable=False)
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    loan = relationship("Loan", back_populates="repayments")

    def __repr__(self):
        return f"<LoanRepayment(id={self.id}, loan_id={self.loan_id}, amount_paid={self.amount_paid})>"


class Contribution(Base):
    """Contribution model - tracks member contributions"""
    __tablename__ = "contributions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    amount = Column(Float, nullable=False)
    contribution_date = Column(DateTime, default=datetime.now, nullable=False)
    contribution_type = Column(Enum(ContributionType), default=ContributionType.MONTHLY, nullable=False)
    month = Column(String(7), nullable=True)  # Format: YYYY-MM
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    member = relationship("Member", back_populates="contributions")

    def __repr__(self):
        return f"<Contribution(id={self.id}, member_id={self.member_id}, amount={self.amount})>"
