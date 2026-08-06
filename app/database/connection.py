import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from .models import Base, Member, NonMember, Loan, LoanRepayment, LoanRefund, LoanTopUp, LoanPenalty, Contribution, LoanStatus, User
from datetime import datetime, timedelta
from components.error_handler import error_logger

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
    try:
        Base.metadata.create_all(bind=engine)
        # Migrate: add is_flagged and flagged_date columns if missing
        insp = inspect(engine)
        for table_name in ("members", "non_members"):
            existing_cols = {c["name"] for c in insp.get_columns(table_name)}
            with engine.begin() as conn:
                if "is_flagged" not in existing_cols:
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN is_flagged BOOLEAN DEFAULT 0 NOT NULL"))
                if "flagged_date" not in existing_cols:
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN flagged_date DATETIME"))
        # Migrate: add notes column to loans table if missing
        loan_cols = {c["name"] for c in insp.get_columns("loans")}
        if "notes" not in loan_cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE loans ADD COLUMN notes VARCHAR(500)"))
        if "overdue_penalty" not in loan_cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE loans ADD COLUMN overdue_penalty FLOAT DEFAULT 0 NOT NULL"))
        error_logger.info(f"Database initialized successfully at: {DB_PATH}")
        print(f"[OK] Database initialized at: {DB_PATH}")
    except Exception as e:
        error_logger.exception(f"Failed to initialize database at {DB_PATH}: {str(e)}")
        print(f"[ERROR] Failed to initialize database: {str(e)}")
        raise


def reset_all_data():
    """Drop all tables and recreate them — a true database reset"""
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        error_logger.info("Database reset: all tables dropped and recreated")
        print("[OK] Database fully reset — all data deleted")
    except Exception as e:
        error_logger.exception(f"Database reset failed: {str(e)}")
        print(f"[ERROR] Database reset failed: {str(e)}")
        raise


def get_session() -> Session:
    """Get a new database session"""
    return SessionLocal()


def close_session(session: Session):
    """Close a database session"""
    if session:
        session.close()


def get_loan_total_due_amount(loan) -> float:
    """Calculate the total amount due for a loan, including manual overdue penalty."""
    return (
        (loan.amount or 0.0)
        + (loan.total_interest or 0.0)
        + (getattr(loan, "overdue_penalty", 0.0) or 0.0)
    )


def get_loan_balance_amount(loan) -> float:
    """Calculate the remaining balance for a loan."""
    return max(0.0, get_loan_total_due_amount(loan) - (loan.amount_repaid or 0.0))


# ==================== MEMBER OPERATIONS ====================

def create_member(name: str, contact: str = None, email: str = None, ippis_number: str = None, status = None) -> Member:
    """Create a new member"""
    from database.models import MemberStatus
    session = get_session()
    try:
        if status is None or isinstance(status, str):
            status = MemberStatus.ACTIVE
        elif isinstance(status, MemberStatus):
            pass  # Already a MemberStatus enum
        
        member = Member(name=name, contact=contact, email=email, ippis_number=ippis_number, status=status)
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


# ==================== NON-MEMBER OPERATIONS ====================

def create_non_member(name: str, contact: str = None, email: str = None, ippis_number: str = None, employer: str = None) -> NonMember:
    """Create a new non-member"""
    session = get_session()
    try:
        non_member = NonMember(name=name, contact=contact, email=email, ippis_number=ippis_number, employer=employer)
        session.add(non_member)
        session.commit()
        session.refresh(non_member)
        return non_member
    except Exception as e:
        session.rollback()
        print(f"Error creating non-member: {e}")
        return None
    finally:
        close_session(session)


def get_all_non_members():
    """Get all non-members"""
    session = get_session()
    try:
        non_members = session.query(NonMember).all()
        return non_members
    finally:
        close_session(session)


def get_non_member_by_id(non_member_id: int) -> NonMember:
    """Get a non-member by ID"""
    session = get_session()
    try:
        non_member = session.query(NonMember).filter(NonMember.id == non_member_id).first()
        return non_member
    finally:
        close_session(session)


def update_non_member(non_member_id: int, **kwargs) -> NonMember:
    """Update non-member information"""
    session = get_session()
    try:
        non_member = session.query(NonMember).filter(NonMember.id == non_member_id).first()
        if non_member:
            for key, value in kwargs.items():
                if hasattr(non_member, key):
                    setattr(non_member, key, value)
            session.commit()
            session.refresh(non_member)
        return non_member
    except Exception as e:
        session.rollback()
        print(f"Error updating non-member: {e}")
        return None
    finally:
        close_session(session)


def delete_non_member(non_member_id: int) -> bool:
    """Delete a non-member"""
    session = get_session()
    try:
        non_member = session.query(NonMember).filter(NonMember.id == non_member_id).first()
        if non_member:
            session.delete(non_member)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error deleting non-member: {e}")
        return False
    finally:
        close_session(session)


# ==================== LOAN OPERATIONS ====================

def create_loan(member_id: int, amount: float, interest_rate: float = 0.0, end_date=None, 
                is_member: bool = True, batch_number: str = None, cheque_number: str = None,
                non_member_id: int = None, guarantor_name: str = None, guarantor_phone: str = None, 
                start_date=None, duration_months: int = 12) -> Loan:
    """Create a new loan
    
    Args:
        member_id: ID of member (if is_member=True)
        amount: Loan principal amount
        interest_rate: Interest rate as percentage
        is_member: True for member (flat-rate), False for non-member (monthly)
        duration_months: Loan duration in months (default 12)
    """
    session = get_session()
    try:
        # Use provided start_date or default to now
        if start_date is None:
            start_date = datetime.now()
        
        # Ensure duration_months is valid
        if duration_months <= 0:
            duration_months = 12
        
        # Calculate total interest based on member type
        total_interest = calculate_interest(amount, interest_rate, is_member, duration_months)
        
        # Calculate end_date if not provided
        if end_date is None:
            end_date = start_date + timedelta(days=30 * duration_months)
        
        loan = Loan(
            member_id=member_id,
            amount=amount,
            interest_rate=interest_rate,
            total_interest=total_interest,
            is_member=is_member,
            batch_number=batch_number,
            cheque_number=cheque_number,
            non_member_id=non_member_id,
            guarantor_name=guarantor_name,
            guarantor_phone=guarantor_phone,
            start_date=start_date,
            end_date=end_date,
            status=LoanStatus.ACTIVE
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


def delete_loan(loan_id: int) -> bool:
    """Delete a loan and all associated repayments/refunds (via cascade)"""
    session = get_session()
    try:
        loan = session.query(Loan).filter(Loan.id == loan_id).first()
        if loan:
            session.delete(loan)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error deleting loan: {e}")
        return False
    finally:
        close_session(session)


# ==================== LOAN REPAYMENT OPERATIONS ====================

def get_repayments_by_loan(loan_id: int):
    """Get all repayments for a loan"""
    session = get_session()
    try:
        repayments = session.query(LoanRepayment).filter(LoanRepayment.loan_id == loan_id).all()
        return repayments
    finally:
        close_session(session)


def record_repayment(loan_id: int, amount_paid: float, payment_date=None, notes: str = None) -> LoanRepayment:
    """Record a loan repayment and update loan status"""
    from database.models import LoanRepayment
    session = get_session()
    try:
        if payment_date is None:
            payment_date = datetime.now()
        
        # Create repayment record
        repayment = LoanRepayment(
            loan_id=loan_id,
            amount_paid=amount_paid,
            payment_date=payment_date,
            notes=notes
        )
        session.add(repayment)
        
        # Update loan's amount_repaid
        loan = session.query(Loan).filter(Loan.id == loan_id).first()
        if loan:
            loan.amount_repaid += amount_paid
            total_due = get_loan_total_due_amount(loan)
            
            # Update loan status to PAID if fully repaid
            if loan.amount_repaid >= total_due:
                loan.status = LoanStatus.PAID
        
        session.commit()
        session.refresh(repayment)
        return repayment
    except Exception as e:
        session.rollback()
        print(f"Error recording repayment: {e}")
        return None
    finally:
        close_session(session)


def get_refunds_by_loan(loan_id: int):
    """Get all refunds for a loan"""
    from database.models import LoanRefund
    session = get_session()
    try:
        refunds = session.query(LoanRefund).filter(LoanRefund.loan_id == loan_id).all()
        return refunds
    finally:
        close_session(session)


def create_refund(loan_id: int, refund_amount: float, refund_date=None, notes: str = None) -> 'LoanRefund':
    """Create a refund record for overpayment"""
    from database.models import LoanRefund
    session = get_session()
    try:
        if refund_date is None:
            refund_date = datetime.now()
        
        refund = LoanRefund(
            loan_id=loan_id,
            refund_amount=refund_amount,
            refund_date=refund_date,
            status="PENDING",
            notes=notes
        )
        session.add(refund)
        session.commit()
        session.refresh(refund)
        return refund
    except Exception as e:
        session.rollback()
        print(f"Error creating refund: {e}")
        return None
    finally:
        close_session(session)


def process_refund(refund_id: int, partial_amount: float = None) -> 'LoanRefund':
    """Mark a refund as processed. If partial_amount is given, process only that portion
    and create a new PENDING refund for the remainder."""
    from database.models import LoanRefund
    session = get_session()
    try:
        refund = session.query(LoanRefund).filter(LoanRefund.id == refund_id).first()
        if refund:
            if partial_amount is not None and 0 < partial_amount < refund.refund_amount:
                remainder = refund.refund_amount - partial_amount
                # Update original to partial amount and mark processed
                refund.refund_amount = partial_amount
                refund.status = "PROCESSED"
                refund.processed_date = datetime.now()
                refund.notes = (refund.notes or "") + f" | Partial refund (₦{partial_amount:,.2f} of ₦{partial_amount + remainder:,.2f})"
                # Create new pending refund for remainder
                remainder_refund = LoanRefund(
                    loan_id=refund.loan_id,
                    refund_amount=remainder,
                    refund_date=datetime.now(),
                    status="PENDING",
                    notes=f"Remaining balance from partial refund #{refund.id}",
                )
                session.add(remainder_refund)
            else:
                refund.status = "PROCESSED"
                refund.processed_date = datetime.now()
            session.commit()
            session.refresh(refund)
        return refund
    except Exception as e:
        session.rollback()
        print(f"Error processing refund: {e}")
        return None
    finally:
        close_session(session)


# ==================== LOAN TOP-UP OPERATIONS ====================

def record_loan_topup(
    loan_id: int,
    topup_amount: float,
    interest_rate: float,
    interest_on_topup: float,
    topup_date=None,
    notes: str = None,
    due_date_extension_months: int = 0,
) -> 'LoanTopUp':
    """Record a loan top-up transaction"""
    session = get_session()
    try:
        if topup_date is None:
            topup_date = datetime.now()
        
        topup = LoanTopUp(
            loan_id=loan_id,
            topup_amount=topup_amount,
            interest_rate=interest_rate,
            interest_on_topup=interest_on_topup,
            topup_date=topup_date,
            notes=notes
        )
        session.add(topup)
        
        # Update the loan with new amounts
        loan = session.query(Loan).filter(Loan.id == loan_id).first()
        if loan:
            loan.amount += topup_amount
            loan.total_interest += interest_on_topup
            if due_date_extension_months and due_date_extension_months > 0:
                base_end_date = loan.end_date or topup_date
                loan.end_date = base_end_date + timedelta(days=30 * due_date_extension_months)
            loan.updated_at = datetime.now()
        
        session.commit()
        session.refresh(topup)
        return topup
    except Exception as e:
        session.rollback()
        print(f"Error recording loan top-up: {e}")
        return None
    finally:
        close_session(session)


def get_topups_by_loan(loan_id: int):
    """Get all top-ups for a loan"""
    session = get_session()
    try:
        topups = session.query(LoanTopUp).filter(LoanTopUp.loan_id == loan_id).order_by(LoanTopUp.topup_date.desc()).all()
        return topups
    finally:
        close_session(session)


def get_topup_by_id(topup_id: int) -> 'LoanTopUp':
    """Get a specific top-up by ID"""
    session = get_session()
    try:
        topup = session.query(LoanTopUp).filter(LoanTopUp.id == topup_id).first()
        return topup
    finally:
        close_session(session)


def record_loan_penalty_change(
    loan_id: int,
    new_penalty: float,
    penalty_date=None,
    notes: str = None,
) -> 'LoanPenalty':
    """Set the current overdue penalty and create an audit record for the change."""
    session = get_session()
    try:
        if penalty_date is None:
            penalty_date = datetime.now()

        loan = session.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            return None

        previous_penalty = (getattr(loan, "overdue_penalty", 0.0) or 0.0)
        penalty_change = new_penalty - previous_penalty

        penalty_record = LoanPenalty(
            loan_id=loan_id,
            previous_penalty=previous_penalty,
            new_penalty=new_penalty,
            penalty_change=penalty_change,
            penalty_date=penalty_date,
            notes=notes,
        )
        session.add(penalty_record)

        loan.overdue_penalty = new_penalty
        loan.updated_at = datetime.now()

        session.commit()
        session.refresh(penalty_record)
        return penalty_record
    except Exception as e:
        session.rollback()
        print(f"Error recording loan penalty change: {e}")
        return None
    finally:
        close_session(session)


def get_penalties_by_loan(loan_id: int):
    """Get all manual overdue penalty changes for a loan."""
    session = get_session()
    try:
        penalties = (
            session.query(LoanPenalty)
            .filter(LoanPenalty.loan_id == loan_id)
            .order_by(LoanPenalty.penalty_date.desc())
            .all()
        )
        return penalties
    finally:
        close_session(session)


# ==================== CONTRIBUTION OPERATIONS ====================

def record_contribution(member_id: int, amount: float, contribution_type: str = "MONTHLY", month: str = None, notes: str = None, contribution_date=None) -> Contribution:
    """Record a contribution"""
    session = get_session()
    try:
        # Use provided contribution_date or default to now
        if contribution_date is None:
            contribution_date = datetime.now()
        
        if not month:
            month = datetime.now().strftime("%Y-%m")
        
        contribution = Contribution(
            member_id=member_id,
            amount=amount,
            contribution_type=contribution_type,
            contribution_date=contribution_date,
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


def get_member_summary_stats():
    """Get contribution totals and active loan counts for ALL members in 2 queries (not N+1).
    Returns: dict of {member_id: {'total_contributions': float, 'active_loans': int}}
    """
    session = get_session()
    try:
        from sqlalchemy import func
        
        # 1 query: contribution totals grouped by member
        contrib_rows = (
            session.query(Contribution.member_id, func.sum(Contribution.amount))
            .group_by(Contribution.member_id)
            .all()
        )
        
        # 1 query: active loan counts grouped by member
        loan_rows = (
            session.query(Loan.member_id, func.count(Loan.id))
            .filter(Loan.status == LoanStatus.ACTIVE, Loan.is_member == True)
            .group_by(Loan.member_id)
            .all()
        )
        
        result = {}
        for member_id, total in contrib_rows:
            if member_id not in result:
                result[member_id] = {'total_contributions': 0.0, 'active_loans': 0}
            result[member_id]['total_contributions'] = total or 0.0
        
        for member_id, count in loan_rows:
            if member_id not in result:
                result[member_id] = {'total_contributions': 0.0, 'active_loans': 0}
            result[member_id]['active_loans'] = count or 0
        
        return result
    finally:
        close_session(session)


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
    """Get count of active loans (excludes Paid and Defaulted loans)"""
    session = get_session()
    try:
        count = session.query(Loan).filter(Loan.status == LoanStatus.ACTIVE).count()
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


# ==================== MONTHLY PAYMENT HELPERS ====================

def get_all_active_borrowers():
    """Get all members and non-members who have at least one ACTIVE loan.
    Returns list of dicts: {ippis, name, is_member, member_id/non_member_id, loan_id, amount, total_interest, amount_repaid}"""
    session = get_session()
    try:
        from sqlalchemy.orm import joinedload
        active_loans = session.query(Loan).filter(Loan.status == LoanStatus.ACTIVE).all()
        borrowers = []
        for loan in active_loans:
            if loan.is_member and loan.member:
                borrowers.append({
                    'ippis': loan.member.ippis_number,
                    'name': loan.member.name,
                    'is_member': True,
                    'member_id': loan.member_id,
                    'loan_id': loan.id,
                    'loan_amount': loan.amount,
                    'total_interest': loan.total_interest or 0,
                    'total_due': loan.amount + (loan.total_interest or 0),
                    'amount_repaid': loan.amount_repaid or 0,
                    'balance': (loan.amount + (loan.total_interest or 0)) - (loan.amount_repaid or 0),
                })
            elif not loan.is_member and loan.non_member:
                borrowers.append({
                    'ippis': loan.non_member.ippis_number,
                    'name': loan.non_member.name,
                    'is_member': False,
                    'non_member_id': loan.non_member_id,
                    'loan_id': loan.id,
                    'loan_amount': loan.amount,
                    'total_interest': loan.total_interest or 0,
                    'total_due': loan.amount + (loan.total_interest or 0),
                    'amount_repaid': loan.amount_repaid or 0,
                    'balance': (loan.amount + (loan.total_interest or 0)) - (loan.amount_repaid or 0),
                })
        return borrowers
    except Exception as e:
        error_logger.error(f"Error getting active borrowers: {e}")
        return []
    finally:
        close_session(session)


def get_monthly_repayments(month: str):
    """Get all LoanRepayments made in a given month (format: YYYY-MM).
    Returns list of repayment records."""
    session = get_session()
    try:
        from sqlalchemy import extract
        year, mon = int(month.split('-')[0]), int(month.split('-')[1])
        repayments = session.query(LoanRepayment).filter(
            extract('year', LoanRepayment.payment_date) == year,
            extract('month', LoanRepayment.payment_date) == mon,
        ).all()
        return repayments
    except Exception as e:
        error_logger.error(f"Error getting monthly repayments: {e}")
        return []
    finally:
        close_session(session)


# ==================== INTEREST CALCULATION ====================

def calculate_interest(amount: float, rate: float, is_member: bool, months: int = 1) -> float:
    """
    Calculate interest based on member type.
    
    Members: Flat-rate simple interest (rate applied once, not multiplied by duration)
    - Formula: total_interest = (amount × rate) / 100
    
    Non-members: Monthly interest (rate applied per month)
    - Formula: total_interest = (amount × rate × months) / 100
    
    Args:
        amount: Loan amount
        rate: Interest rate as percentage (e.g., 5 for 5%)
        is_member: True for member (flat-rate), False for non-member (monthly)
        months: Number of months (only used for non-members, default 1)
    
    Returns:
        Total interest calculated
    """
    if is_member:
        # Members: Flat-rate simple interest (NOT multiplied by duration)
        # Example: ₦50,000 at 5% = ₦2,500 interest (fixed, regardless of duration)
        total_interest = (amount * rate) / 100
    else:
        # Non-members: Monthly interest (compounded/accumulated over months)
        # Example: ₦50,000 at 2% per month for 12 months = ₦12,000 interest
        monthly_rate = rate  # Assume the rate parameter is already in monthly terms
        months_for_calc = months if months > 0 else 1
        total_interest = (amount * monthly_rate * months_for_calc) / 100
    
    return total_interest


# ==================== USER AUTHENTICATION ====================

def create_user(username: str, email: str, password: str, full_name: str = None, role: str = "USER") -> User:
    """Create a new user account"""
    from database.models import UserRole
    session = get_session()
    try:
        # Check if username or email already exists
        existing_user = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            raise ValueError(f"Username or email already exists")
        
        user_role = UserRole[role.upper()] if isinstance(role, str) else role
        
        user = User(
            username=username,
            email=email,
            password_hash=User.hash_password(password),
            full_name=full_name,
            role=user_role,
            is_active=True
        )
        session.add(user)
        session.commit()
        print(f"[OK] User '{username}' created successfully")
        return user
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Failed to create user: {str(e)}")
        raise
    finally:
        session.close()


def get_user_by_username(username: str) -> User:
    """Get user by username"""
    session = get_session()
    try:
        user = session.query(User).filter(User.username == username).first()
        return user
    finally:
        session.close()


def authenticate_user(username: str, password: str) -> tuple[bool, str]:
    """Authenticate user with username and password
    
    Returns:
        (success: bool, message: str)
    """
    session = get_session()
    try:
        user = session.query(User).filter(User.username == username).first()
        
        if not user:
            return False, "User not found"
        
        if not user.is_active:
            return False, "User account is inactive"
        
        if not user.verify_password(password):
            return False, "Invalid password"
        
        return True, f"Login successful. Welcome {user.full_name or user.username}!"
    except Exception as e:
        return False, f"Authentication error: {str(e)}"
    finally:
        session.close()


def update_user(user_id: int, username: str = None, email: str = None, full_name: str = None, password: str = None) -> User:
    """Update user account details"""
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        if username and username != user.username:
            # Check if username is already in use
            existing = session.query(User).filter(User.username == username).first()
            if existing:
                raise ValueError("Username already in use")
            user.username = username
        
        if email and email != user.email:
            # Check if email is already in use
            existing = session.query(User).filter(User.email == email).first()
            if existing:
                raise ValueError("Email already in use")
            user.email = email
        
        if full_name:
            user.full_name = full_name
        
        if password:
            user.password_hash = User.hash_password(password)
        
        user.updated_at = datetime.now()
        session.commit()
        print(f"[OK] User '{user.username}' updated successfully")
        return user
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Failed to update user: {str(e)}")
        raise
    finally:
        session.close()


def get_all_users() -> list:
    """Get all users"""
    session = get_session()
    try:
        users = session.query(User).all()
        return users
    finally:
        session.close()


def delete_user(user_id: int) -> bool:
    """Delete a user account"""
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        session.delete(user)
        session.commit()
        print(f"[OK] User deleted successfully")
        return True
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Failed to delete user: {str(e)}")
        raise
    finally:
        session.close()


# ==================== ADVANCED LOAN MANAGEMENT ====================

def can_member_take_loan(member_id: int) -> tuple:
    """
    Check if a member can take a loan based on business rules
    Returns: (bool, str) - (can_take_loan, reason_if_not)
    """
    session = get_session()
    try:
        member = session.query(Member).filter(Member.id == member_id).first()
        
        if not member:
            return False, "Member not found"
        
        # Rule 1: Member must be ACTIVE
        if member.status.value != "Active":
            return False, f"Member status is {member.status.value}. Only ACTIVE members can take loans."
        
        # Rule 2: Check for existing active loans (optional - can have multiple)
        active_loans = session.query(Loan).filter(
            Loan.member_id == member_id,
            Loan.status == LoanStatus.ACTIVE
        ).all()
        
        # For now, allow multiple active loans but log them
        if len(active_loans) > 0:
            print(f"[INFO] Member {member.name} has {len(active_loans)} active loan(s)")
        
        return True, "Member is eligible for loan"
    
    except Exception as e:
        print(f"Error checking member loan eligibility: {e}")
        return False, f"Error: {str(e)}"
    finally:
        close_session(session)


def calculate_loan_details(amount: float, interest_rate: float, duration_months: int, is_member: bool = True) -> dict:
    """
    Calculate comprehensive loan details
    
    Args:
        amount: Principal loan amount
        interest_rate: Interest rate as percentage (e.g., 5 for 5%)
        duration_months: Number of months for the loan
        is_member: True for member (flat-rate), False for non-member (monthly compound)
    
    Returns: {
        'principal': float,
        'interest_rate_percentage': float,
        'total_interest': float,
        'total_due': float,
        'monthly_payment': float,
        'duration_months': int
    }
    """
    try:
        # Validate inputs
        if amount <= 0:
            raise ValueError("Loan amount must be greater than 0")
        if interest_rate < 0 or interest_rate > 100:
            raise ValueError("Interest rate must be between 0 and 100")
        if duration_months <= 0:
            raise ValueError("Duration must be greater than 0 months")
        
        # Convert decimal to percentage if needed
        rate = interest_rate
        if rate < 1:
            rate = rate * 100
        
        # Calculate total interest based on member type
        total_interest = calculate_interest(amount, rate, is_member, duration_months)
        
        # Calculate total due (principal + interest)
        total_due = amount + total_interest
        
        # Calculate monthly payment (equal installments)
        monthly_payment = total_due / duration_months
        
        return {
            'principal': amount,
            'interest_rate_percentage': rate,
            'total_interest': total_interest,
            'total_due': total_due,
            'monthly_payment': monthly_payment,
            'duration_months': duration_months
        }
    except Exception as e:
        print(f"Error calculating loan details: {e}")
        raise


def create_loan_with_validation(member_id: int, amount: float, interest_rate: float, 
                                duration_months: int, start_date=None, batch_number: str = None,
                                cheque_number: str = None, guarantor_name: str = None,
                                guarantor_phone: str = None, is_member: bool = True) -> tuple:
    """
    Create a loan with full validation and business rules
    
    Args:
        member_id: ID of the member borrowing
        amount: Loan amount
        interest_rate: Interest rate as percentage
        duration_months: Loan duration in months
        start_date: Loan issue date (defaults to now)
        batch_number: Batch number reference
        cheque_number: Cheque number reference
        guarantor_name: Guarantor's name
        guarantor_phone: Guarantor's phone
        is_member: Whether this is a member loan (True for flat-rate, False for monthly)
    
    Returns: (success: bool, loan_object_or_error_message, additional_info: dict)
    """
    session = get_session()
    try:
        # Step 1: Check if member can take loan
        can_take, reason = can_member_take_loan(member_id)
        if not can_take:
            return False, reason, {}
        
        # Step 2: Validate loan details (use is_member flag for correct calculation)
        loan_details = calculate_loan_details(amount, interest_rate, duration_months, is_member)
        
        # Step 3: Create loan object
        if start_date is None:
            start_date = datetime.now()
        
        end_date = start_date + timedelta(days=30 * duration_months)
        
        loan = Loan(
            member_id=member_id,
            amount=amount,
            interest_rate=loan_details['interest_rate_percentage'],
            total_interest=loan_details['total_interest'],
            amount_repaid=0.0,
            is_member=True,  # This is always True for this function (it's for members)
            batch_number=batch_number,
            cheque_number=cheque_number,
            guarantor_name=guarantor_name,
            guarantor_phone=guarantor_phone,
            start_date=start_date,
            end_date=end_date,
            status=LoanStatus.ACTIVE
        )
        
        session.add(loan)
        session.commit()
        session.refresh(loan)
        
        return True, loan, {
            'loan_id': loan.id,
            'total_due': loan_details['total_due'],
            'monthly_payment': loan_details['monthly_payment'],
            'status': 'ACTIVE'
        }
    
    except Exception as e:
        session.rollback()
        print(f"Error creating loan: {e}")
        return False, str(e), {}
    finally:
        close_session(session)


def process_repayment_advanced(loan_id: int, amount_paid: float, payment_date=None, 
                              notes: str = None) -> dict:
    """
    Advanced repayment processing with overpayment handling and status updates
    Returns: {
        'success': bool,
        'message': str,
        'repayment_id': int (if success),
        'loan_status': str,
        'balance_remaining': float,
        'refund_created': bool,
        'refund_amount': float,
        'loan_fully_paid': bool
    }
    """
    session = get_session()
    try:
        if payment_date is None:
            payment_date = datetime.now()
        
        # Get the loan
        loan = session.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            return {
                'success': False,
                'message': f'Loan ID {loan_id} not found',
                'repayment_id': None,
                'loan_status': None,
                'balance_remaining': 0,
                'refund_created': False,
                'refund_amount': 0,
                'loan_fully_paid': False
            }
        
        # Validate payment amount
        if amount_paid <= 0:
            return {
                'success': False,
                'message': 'Payment amount must be greater than 0',
                'repayment_id': None,
                'loan_status': loan.status.value,
                'balance_remaining': get_loan_balance_amount(loan),
                'refund_created': False,
                'refund_amount': 0,
                'loan_fully_paid': False
            }
        
        total_due = get_loan_total_due_amount(loan)
        current_balance = total_due - loan.amount_repaid
        
        # Create repayment record
        repayment = LoanRepayment(
            loan_id=loan_id,
            amount_paid=amount_paid,
            payment_date=payment_date,
            notes=notes
        )
        session.add(repayment)
        
        # Update loan amount_repaid
        loan.amount_repaid += amount_paid
        
        refund_created = False
        refund_amount = 0
        loan_fully_paid = False
        new_status = loan.status.value
        
        # Check for overpayment
        if loan.amount_repaid > total_due:
            refund_amount = loan.amount_repaid - total_due
            
            # Create refund record
            refund = LoanRefund(
                loan_id=loan_id,
                refund_amount=refund_amount,
                refund_date=payment_date,
                status="PENDING",
                notes=f"Overpayment refund from payment on {payment_date.strftime('%Y-%m-%d')}: {notes}" if notes else "Overpayment refund"
            )
            session.add(refund)
            refund_created = True
            
            loan.status = LoanStatus.PAID
            new_status = LoanStatus.PAID.value
            loan_fully_paid = True
        
        # Check if loan is fully paid
        elif loan.amount_repaid >= total_due:
            new_status = LoanStatus.PAID.value
            loan_fully_paid = True
            loan.status = LoanStatus.PAID
        
        else:
            # Still active - update to ACTIVE status explicitly
            new_status = LoanStatus.ACTIVE.value
            loan.status = LoanStatus.ACTIVE
        
        # Commit all changes
        session.commit()
        session.refresh(repayment)
        
        balance_remaining = max(0, total_due - loan.amount_repaid)
        
        return {
            'success': True,
            'message': f'Repayment of ₦{amount_paid:.2f} recorded successfully',
            'repayment_id': repayment.id,
            'loan_status': new_status,
            'balance_remaining': balance_remaining,
            'refund_created': refund_created,
            'refund_amount': refund_amount,
            'loan_fully_paid': loan_fully_paid
        }
    
    except Exception as e:
        session.rollback()
        print(f"Error processing repayment: {e}")
        return {
            'success': False,
            'message': f'Error: {str(e)}',
            'repayment_id': None,
            'loan_status': None,
            'balance_remaining': 0,
            'refund_created': False,
            'refund_amount': 0,
            'loan_fully_paid': False
        }
    finally:
        close_session(session)


def get_loan_summary(loan_id: int) -> dict:
    """
    Get comprehensive loan summary with all calculations
    """
    session = get_session()
    try:
        loan = session.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            return {}
        
        total_due = get_loan_total_due_amount(loan)
        balance_remaining = max(0, total_due - loan.amount_repaid)
        
        # Get all repayments
        repayments = session.query(LoanRepayment).filter(LoanRepayment.loan_id == loan_id).all()
        
        # Get all refunds
        refunds = session.query(LoanRefund).filter(LoanRefund.loan_id == loan_id).all()
        
        # Calculate days overdue if applicable
        days_overdue = 0
        if loan.end_date and loan.status == LoanStatus.ACTIVE:
            today = datetime.now().date()
            end_date = loan.end_date.date() if isinstance(loan.end_date, datetime) else loan.end_date
            if today > end_date:
                days_overdue = (today - end_date).days
        
        return {
            'loan_id': loan.id,
            'member_id': loan.member_id,
            'principal_amount': loan.amount,
            'interest_rate': loan.interest_rate,
            'total_interest': loan.total_interest,
            'total_due': total_due,
            'amount_repaid': loan.amount_repaid,
            'balance_remaining': balance_remaining,
            'percentage_paid': (loan.amount_repaid / total_due * 100) if total_due > 0 else 0,
            'status': loan.status.value,
            'start_date': loan.start_date,
            'end_date': loan.end_date,
            'days_overdue': days_overdue,
            'is_overdue': days_overdue > 0,
            'batch_number': loan.batch_number,
            'cheque_number': loan.cheque_number,
            'repayment_count': len(repayments),
            'total_repayments': sum(r.amount_paid for r in repayments),
            'refund_count': len(refunds),
            'total_refunded': sum(r.refund_amount for r in refunds)
        }
    except Exception as e:
        print(f"Error getting loan summary: {e}")
        return {}
    finally:
        close_session(session)


def get_member_loan_status(member_id: int) -> dict:
    """
    Get comprehensive loan status for a member
    Shows all active/paid loans, total debt, etc.
    """
    session = get_session()
    try:
        member = session.query(Member).filter(Member.id == member_id).first()
        if not member:
            return {}
        
        all_loans = session.query(Loan).filter(Loan.member_id == member_id).all()
        
        active_loans = [l for l in all_loans if l.status == LoanStatus.ACTIVE]
        paid_loans = [l for l in all_loans if l.status == LoanStatus.PAID]
        defaulted_loans = [l for l in all_loans if l.status == LoanStatus.DEFAULTED]
        
        total_borrowed = sum(l.amount for l in all_loans)
        total_repaid = sum(l.amount_repaid for l in all_loans)
        total_debt = sum(get_loan_balance_amount(l) for l in active_loans)
        
        return {
            'member_id': member_id,
            'member_name': member.name,
            'member_status': member.status.value,
            'total_loans': len(all_loans),
            'active_loans': len(active_loans),
            'paid_loans': len(paid_loans),
            'defaulted_loans': len(defaulted_loans),
            'total_borrowed': total_borrowed,
            'total_repaid': total_repaid,
            'total_outstanding_debt': total_debt,
            'can_take_loan': member.status.value == "Active"
        }
    except Exception as e:
        print(f"Error getting member loan status: {e}")
        return {}
    finally:
        close_session(session)


def get_overdue_loans_list() -> list:
    """
    Get all loans that are overdue (end_date passed but status is still ACTIVE)
    """
    session = get_session()
    try:
        today = datetime.now()
        overdue_loans = session.query(Loan).filter(
            Loan.status == LoanStatus.ACTIVE,
            Loan.end_date < today
        ).all()
        
        return overdue_loans
    except Exception as e:
        print(f"Error getting overdue loans: {e}")
        return []
    finally:
        close_session(session)


def update_overdue_non_member_interest() -> list:
    """
    Recalculate and update interest for overdue NON-MEMBER loans.
    
    Non-member loans use monthly interest: (amount × rate × months) / 100
    When a loan is overdue, extra months beyond the end_date are added to the
    duration so the total_interest keeps growing until the borrower pays up.
    
    Member loans are NOT affected — their interest stays flat-rate.
    
    Returns:
        List of dicts with updated loan info [{loan_id, old_interest, new_interest, extra_months}]
    """
    session = get_session()
    updated = []
    try:
        today = datetime.now()
        
        # Only non-member, active loans that are past their end_date
        overdue_loans = session.query(Loan).filter(
            Loan.status == LoanStatus.ACTIVE,
            Loan.is_member == False,
            Loan.end_date < today,
            Loan.end_date.isnot(None),
        ).all()
        
        for loan in overdue_loans:
            # Skip if already fully paid (safety check)
            total_due = get_loan_total_due_amount(loan)
            if loan.amount_repaid >= total_due:
                continue
            
            # Calculate original duration in months
            start = loan.start_date
            end = loan.end_date
            if isinstance(start, datetime) and isinstance(end, datetime):
                original_months = max(1, (end - start).days // 30)
            else:
                original_months = 12  # fallback
            
            # Calculate extra overdue months
            if isinstance(end, datetime):
                extra_days = (today - end).days
            else:
                extra_days = (today - datetime.combine(end, datetime.min.time())).days
            extra_months = max(0, extra_days // 30)
            
            if extra_months <= 0:
                continue
            
            # Recalculate total interest with extended duration
            total_months = original_months + extra_months
            new_total_interest = (loan.amount * loan.interest_rate * total_months) / 100
            
            # Only update if interest increased
            if new_total_interest > loan.total_interest:
                old_interest = loan.total_interest
                loan.total_interest = new_total_interest
                loan.updated_at = today
                
                updated.append({
                    "loan_id": loan.id,
                    "old_interest": old_interest,
                    "new_interest": new_total_interest,
                    "extra_months": extra_months,
                    "total_months": total_months,
                })
        
        if updated:
            session.commit()
            print(f"✓ Updated interest for {len(updated)} overdue non-member loan(s)")
        
        return updated
    except Exception as e:
        session.rollback()
        print(f"Error updating overdue non-member interest: {e}")
        return []
    finally:
        close_session(session)


def update_single_loan_overdue_interest(loan_id: int) -> dict:
    """
    Recalculate interest for a single overdue non-member loan.
    Used when viewing individual loan details.
    
    Returns:
        Dict with update info or empty dict if no update needed
    """
    session = get_session()
    try:
        today = datetime.now()
        loan = session.query(Loan).filter(Loan.id == loan_id).first()
        
        if not loan:
            return {}
        
        # Only applies to non-member, active, overdue loans
        if loan.is_member or loan.status != LoanStatus.ACTIVE:
            return {}
        if not loan.end_date or loan.end_date >= today:
            return {}
        
        # Calculate original duration
        start = loan.start_date
        end = loan.end_date
        if isinstance(start, datetime) and isinstance(end, datetime):
            original_months = max(1, (end - start).days // 30)
        else:
            original_months = 12
        
        # Calculate extra overdue months
        if isinstance(end, datetime):
            extra_days = (today - end).days
        else:
            extra_days = (today - datetime.combine(end, datetime.min.time())).days
        extra_months = max(0, extra_days // 30)
        
        if extra_months <= 0:
            return {}
        
        total_months = original_months + extra_months
        new_total_interest = (loan.amount * loan.interest_rate * total_months) / 100
        
        if new_total_interest > loan.total_interest:
            old_interest = loan.total_interest
            loan.total_interest = new_total_interest
            loan.updated_at = today
            session.commit()
            
            return {
                "loan_id": loan.id,
                "old_interest": old_interest,
                "new_interest": new_total_interest,
                "extra_months": extra_months,
                "total_months": total_months,
            }
        
        return {}
    except Exception as e:
        session.rollback()
        print(f"Error updating single loan overdue interest: {e}")
        return {}
    finally:
        close_session(session)


def check_and_flag_overdue_borrowers():
    """Flag members/non-members who have any loan overdue by 90+ days.
    Once flagged, the flag is permanent (persists even after all loans are paid)."""
    session = get_session()
    try:
        today = datetime.now()
        cutoff = today - timedelta(days=90)

        overdue_loans = session.query(Loan).filter(
            Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.DEFAULTED]),
            Loan.end_date < cutoff,
            Loan.end_date.isnot(None),
        ).all()

        flagged_count = 0
        for loan in overdue_loans:
            if loan.member_id:
                member = session.query(Member).filter(Member.id == loan.member_id).first()
                if member and not member.is_flagged:
                    member.is_flagged = True
                    member.flagged_date = today
                    flagged_count += 1
            elif loan.non_member_id:
                nm = session.query(NonMember).filter(NonMember.id == loan.non_member_id).first()
                if nm and not nm.is_flagged:
                    nm.is_flagged = True
                    nm.flagged_date = today
                    flagged_count += 1

        if flagged_count:
            session.commit()
            print(f"✓ Flagged {flagged_count} borrower(s) with 90+ day overdue loans")
        return flagged_count
    except Exception as e:
        session.rollback()
        print(f"Error flagging overdue borrowers: {e}")
        return 0
    finally:
        close_session(session)
