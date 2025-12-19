import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from .models import Base, Member, Loan, LoanRepayment, Contribution
from datetime import datetime

# Database configuration - SQLite for offline single-user app
DB_PATH = os.path.join(os.path.dirname(__file__), "loan_manager.db")

# Create SQLite engine with check_same_thread=False for Flet's async handling
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize the database - creates all tables if they don't exist"""
    Base.metadata.create_all(bind=engine)
    print(f"✓ Database initialized at: {DB_PATH}")


def get_session() -> Session:
    """Get a new database session"""
    return SessionLocal()


def close_session(session: Session):
    """Close a database session"""
    if session:
        session.close()


# ==================== MEMBER OPERATIONS ====================

def create_member(name: str, contact: str = None, email: str = None, status: str = "Active") -> Member:
    """Create a new member"""
    session = get_session()
    try:
        member = Member(name=name, contact=contact, email=email, status=status)
        session.add(member)
        session.commit()
        member_id = member.id
        session.refresh(member)
        return member
    except Exception as e:
        session.rollback()
        print(f"Error creating member: {e}")
        return None
    finally:
        close_session(session)


def get_all_members():
    """Get all members"""
    session = get_session()
    try:
        members = session.query(Member).all()
        return members
    finally:
        close_session(session)


def get_member_by_id(member_id: int) -> Member:
    """Get a member by ID"""
    session = get_session()
    try:
        member = session.query(Member).filter(Member.id == member_id).first()
        return member
    finally:
        close_session(session)


def update_member(member_id: int, **kwargs) -> Member:
    """Update member information"""
    session = get_session()
    try:
        member = session.query(Member).filter(Member.id == member_id).first()
        if member:
            for key, value in kwargs.items():
                if hasattr(member, key):
                    setattr(member, key, value)
            session.commit()
            session.refresh(member)
        return member
    except Exception as e:
        session.rollback()
        print(f"Error updating member: {e}")
        return None
    finally:
        close_session(session)


def delete_member(member_id: int) -> bool:
    """Delete a member"""
    session = get_session()
    try:
        member = session.query(Member).filter(Member.id == member_id).first()
        if member:
            session.delete(member)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error deleting member: {e}")
        return False
    finally:
        close_session(session)


# ==================== LOAN OPERATIONS ====================

def create_loan(member_id: int, amount: float, interest_rate: float = 0.0, end_date=None) -> Loan:
    """Create a new loan"""
    session = get_session()
    try:
        total_interest = (amount * interest_rate) / 100
        loan = Loan(
            member_id=member_id,
            amount=amount,
            interest_rate=interest_rate,
            total_interest=total_interest,
            end_date=end_date
        )
        session.add(loan)
        session.commit()
        session.refresh(loan)
        return loan
    except Exception as e:
        session.rollback()
        print(f"Error creating loan: {e}")
        return None
    finally:
        close_session(session)


def get_all_loans():
    """Get all loans"""
    session = get_session()
    try:
        loans = session.query(Loan).all()
        return loans
    finally:
        close_session(session)


def get_loans_by_member(member_id: int):
    """Get all loans for a specific member"""
    session = get_session()
    try:
        loans = session.query(Loan).filter(Loan.member_id == member_id).all()
        return loans
    finally:
        close_session(session)


def get_loan_by_id(loan_id: int) -> Loan:
    """Get a loan by ID"""
    session = get_session()
    try:
        loan = session.query(Loan).filter(Loan.id == loan_id).first()
        return loan
    finally:
        close_session(session)


def update_loan(loan_id: int, **kwargs) -> Loan:
    """Update loan information"""
    session = get_session()
    try:
        loan = session.query(Loan).filter(Loan.id == loan_id).first()
        if loan:
            for key, value in kwargs.items():
                if hasattr(loan, key):
                    setattr(loan, key, value)
            session.commit()
            session.refresh(loan)
        return loan
    except Exception as e:
        session.rollback()
        print(f"Error updating loan: {e}")
        return None
    finally:
        close_session(session)


def get_active_loans():
    """Get all active loans"""
    session = get_session()
    try:
        loans = session.query(Loan).filter(Loan.status == "Active").all()
        return loans
    finally:
        close_session(session)


# ==================== LOAN REPAYMENT OPERATIONS ====================

def record_repayment(loan_id: int, amount_paid: float, notes: str = None) -> LoanRepayment:
    """Record a loan repayment"""
    session = get_session()
    try:
        repayment = LoanRepayment(loan_id=loan_id, amount_paid=amount_paid, notes=notes)
        session.add(repayment)
        
        # Update loan's amount_repaid
        loan = session.query(Loan).filter(Loan.id == loan_id).first()
        if loan:
            loan.amount_repaid += amount_paid
            # Check if loan is fully paid
            if loan.amount_repaid >= (loan.amount + loan.total_interest):
                loan.status = "Paid"
                loan.end_date = datetime.now()
        
        session.commit()
        session.refresh(repayment)
        return repayment
    except Exception as e:
        session.rollback()
        print(f"Error recording repayment: {e}")
        return None
    finally:
        close_session(session)


def get_repayments_by_loan(loan_id: int):
    """Get all repayments for a loan"""
    session = get_session()
    try:
        repayments = session.query(LoanRepayment).filter(LoanRepayment.loan_id == loan_id).all()
        return repayments
    finally:
        close_session(session)


# ==================== CONTRIBUTION OPERATIONS ====================

def record_contribution(member_id: int, amount: float, contribution_type: str = "Monthly", month: str = None, notes: str = None) -> Contribution:
    """Record a contribution"""
    session = get_session()
    try:
        if not month:
            month = datetime.now().strftime("%Y-%m")
        
        contribution = Contribution(
            member_id=member_id,
            amount=amount,
            contribution_type=contribution_type,
            month=month,
            notes=notes
        )
        session.add(contribution)
        session.commit()
        session.refresh(contribution)
        return contribution
    except Exception as e:
        session.rollback()
        print(f"Error recording contribution: {e}")
        return None
    finally:
        close_session(session)


def get_all_contributions():
    """Get all contributions"""
    session = get_session()
    try:
        contributions = session.query(Contribution).all()
        return contributions
    finally:
        close_session(session)


def get_contributions_by_member(member_id: int):
    """Get all contributions for a member"""
    session = get_session()
    try:
        contributions = session.query(Contribution).filter(Contribution.member_id == member_id).all()
        return contributions
    finally:
        close_session(session)


def get_contributions_by_month(month: str):
    """Get all contributions for a specific month (YYYY-MM format)"""
    session = get_session()
    try:
        contributions = session.query(Contribution).filter(Contribution.month == month).all()
        return contributions
    finally:
        close_session(session)


# ==================== STATISTICS OPERATIONS ====================

def get_total_contributions():
    """Get total contributions across all members"""
    session = get_session()
    try:
        from sqlalchemy import func
        total = session.query(func.sum(Contribution.amount)).scalar()
        return total or 0.0
    finally:
        close_session(session)


def get_total_loans_issued():
    """Get total amount of loans issued"""
    session = get_session()
    try:
        from sqlalchemy import func
        total = session.query(func.sum(Loan.amount)).scalar()
        return total or 0.0
    finally:
        close_session(session)


def get_active_loans_count():
    """Get count of active loans"""
    session = get_session()
    try:
        count = session.query(Loan).filter(Loan.status == "Active").count()
        return count
    finally:
        close_session(session)


def get_total_members():
    """Get total number of members"""
    session = get_session()
    try:
        count = session.query(Member).count()
        return count
    finally:
        close_session(session)


def get_recent_activities(limit: int = 10):
    """Get recent activities (contributions and repayments)"""
    session = get_session()
    try:
        from sqlalchemy import union_all
        
        # Get recent contributions
        contributions = session.query(
            Contribution.id,
            Contribution.member_id,
            Contribution.amount,
            Contribution.contribution_date.label("date"),
            Contribution.created_at,
            "Contribution" .label("type")
        )
        
        # Get recent repayments
        repayments = session.query(
            LoanRepayment.id,
            Loan.member_id,
            LoanRepayment.amount_paid.label("amount"),
            LoanRepayment.payment_date.label("date"),
            LoanRepayment.created_at,
            "Repayment".label("type")
        ).join(Loan, LoanRepayment.loan_id == Loan.id)
        
        # Combine and sort by created_at
        activities = session.query(contributions.union_all(repayments)).order_by(
            "-created_at"
        ).limit(limit).all()
        
        return activities
    except Exception as e:
        print(f"Error getting recent activities: {e}")
        return []
    finally:
        close_session(session)
