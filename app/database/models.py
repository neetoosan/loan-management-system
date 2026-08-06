from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import hashlib

Base = declarative_base()


class UserRole(enum.Enum):
    ADMIN = "Admin"
    USER = "User"


class User(Base):
    """User model - stores user accounts for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # Store hashed password
    full_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role={self.role})>"

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash"""
        return self.password_hash == self.hash_password(password)


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
    MONTHLY = "MONTHLY"
    WEEKLY = "WEEKLY"
    VOLUNTARY = "VOLUNTARY"


class Member(Base):
    """Member model - stores information about group members"""
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    contact = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    ippis_number = Column(String(50), nullable=True)  # IPPIS number
    join_date = Column(DateTime, default=datetime.now, nullable=False)
    status = Column(Enum(MemberStatus), default=MemberStatus.ACTIVE, nullable=False)
    is_flagged = Column(Boolean, default=False, nullable=False)
    flagged_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    loans = relationship("Loan", back_populates="member", cascade="all, delete-orphan")
    contributions = relationship("Contribution", back_populates="member", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Member(id={self.id}, name='{self.name}', status={self.status})>"


class NonMember(Base):
    """Non-Member model - stores information about non-member loan recipients"""
    __tablename__ = "non_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    contact = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    ippis_number = Column(String(50), nullable=True)  # IPPIS number
    employer = Column(String(100), nullable=True)  # Employer information
    is_flagged = Column(Boolean, default=False, nullable=False)
    flagged_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    loans = relationship("Loan", back_populates="non_member", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<NonMember(id={self.id}, name='{self.name}')>"


class Loan(Base):
    """Loan model - stores loan information for members and non-members"""
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=True, index=True)
    non_member_id = Column(Integer, ForeignKey("non_members.id"), nullable=True, index=True)
    is_member = Column(Boolean, default=True, nullable=False)  # True for member, False for non-member
    amount = Column(Float, nullable=False)
    interest_rate = Column(Float, default=0.0, nullable=False)  # Interest rate in percentage
    batch_number = Column(String(50), nullable=True)
    cheque_number = Column(String(50), nullable=True)
    guarantor_name = Column(String(100), nullable=True)  # Guarantor's name
    guarantor_phone = Column(String(20), nullable=True)  # Guarantor's phone number
    start_date = Column(DateTime, default=datetime.now, nullable=False)
    end_date = Column(DateTime, nullable=True)
    status = Column(Enum(LoanStatus), default=LoanStatus.PENDING, nullable=False, index=True)
    total_interest = Column(Float, default=0.0, nullable=False)
    overdue_penalty = Column(Float, default=0.0, nullable=False)
    amount_repaid = Column(Float, default=0.0, nullable=False)
    notes = Column(String(500), nullable=True)  # Loan remarks/notes
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Compound index for overdue loan queries
    __table_args__ = (
        Index('ix_loans_status_member_enddate', 'status', 'is_member', 'end_date'),
    )

    # Relationships
    member = relationship("Member", back_populates="loans")
    non_member = relationship("NonMember", back_populates="loans")
    repayments = relationship("LoanRepayment", back_populates="loan", cascade="all, delete-orphan")
    refunds = relationship("LoanRefund", back_populates="loan", cascade="all, delete-orphan")
    topups = relationship("LoanTopUp", back_populates="loan", cascade="all, delete-orphan")
    penalties = relationship("LoanPenalty", back_populates="loan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Loan(id={self.id}, amount={self.amount}, status={self.status})>"


class LoanRepayment(Base):
    """Loan Repayment model - tracks individual loan repayments"""
    __tablename__ = "loan_repayments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False, index=True)
    amount_paid = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.now, nullable=False)
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    loan = relationship("Loan", back_populates="repayments")

    def __repr__(self):
        return f"<LoanRepayment(id={self.id}, loan_id={self.loan_id}, amount_paid={self.amount_paid})>"


class LoanRefund(Base):
    """Loan Refund model - tracks refunds for overpayments"""
    __tablename__ = "loan_refunds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False, index=True)
    refund_amount = Column(Float, nullable=False)  # Amount to refund back to client
    refund_date = Column(DateTime, default=datetime.now, nullable=False)
    status = Column(String(50), default="PENDING", nullable=False)  # PENDING, PROCESSED, CANCELLED
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    processed_date = Column(DateTime, nullable=True)

    # Relationships
    loan = relationship("Loan", back_populates="refunds")

    def __repr__(self):
        return f"<LoanRefund(id={self.id}, loan_id={self.loan_id}, refund_amount={self.refund_amount}, status={self.status})>"


class LoanTopUp(Base):
    """Loan Top-up model - tracks loan top-ups for audit trail"""
    __tablename__ = "loan_topups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False, index=True)
    topup_amount = Column(Float, nullable=False)  # Additional amount added to loan
    interest_rate = Column(Float, nullable=False)  # Interest rate applied to top-up
    interest_on_topup = Column(Float, nullable=False)  # Interest calculated on top-up amount
    topup_date = Column(DateTime, default=datetime.now, nullable=False)
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    loan = relationship("Loan", back_populates="topups")

    def __repr__(self):
        return f"<LoanTopUp(id={self.id}, loan_id={self.loan_id}, topup_amount={self.topup_amount})>"


class LoanPenalty(Base):
    """Loan penalty audit model - tracks manual overdue penalty changes"""
    __tablename__ = "loan_penalties"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False, index=True)
    previous_penalty = Column(Float, default=0.0, nullable=False)
    new_penalty = Column(Float, default=0.0, nullable=False)
    penalty_change = Column(Float, default=0.0, nullable=False)
    penalty_date = Column(DateTime, default=datetime.now, nullable=False)
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    loan = relationship("Loan", back_populates="penalties")

    def __repr__(self):
        return (
            f"<LoanPenalty(id={self.id}, loan_id={self.loan_id}, "
            f"penalty_change={self.penalty_change}, new_penalty={self.new_penalty})>"
        )


class Contribution(Base):
    """Contribution model - tracks member contributions"""
    __tablename__ = "contributions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    contribution_date = Column(DateTime, default=datetime.now, nullable=False)
    contribution_type = Column(Enum(ContributionType), default=ContributionType.MONTHLY, nullable=False)
    month = Column(String(7), nullable=True, index=True)  # Format: YYYY-MM
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    member = relationship("Member", back_populates="contributions")

    def __repr__(self):
        return f"<Contribution(id={self.id}, member_id={self.member_id}, amount={self.amount})>"
