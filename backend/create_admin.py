import getpass
from sqlalchemy.orm import sessionmaker
from app.db.database import engine, Base
from app.db.models import User
from app.core.security import get_password_hash

def create_admin_user():
    """
    Creates an administrative user in the database.
    """
    print("--- Create Admin User ---")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Get user input
    username = input("Enter admin username: ")
    password = getpass.getpass("Enter admin password: ")
    
    # Check if user already exists
    existing_user = session.query(User).filter(User.username == username).first()
    if existing_user:
        print(f"Error: User '{username}' already exists.")
        session.close()
        return

    # Create new admin user
    hashed_password = get_password_hash(password)
    admin_user = User(
        username=username,
        hashed_password=hashed_password,
        is_admin=1
    )
    
    session.add(admin_user)
    session.commit()
    
    print(f"\nAdmin user '{username}' created successfully!")
    session.close()

if __name__ == "__main__":
    create_admin_user()
