import bcrypt
from pymongo import MongoClient, errors
import getpass

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_user():
    print("=== MongoDB User Creation ===")
    
    # Connection setup
    while True:
        connection_string = input("MongoDB URI [default: mongodb://localhost:27017]: ").strip() or "mongodb://localhost:27017"
        
        try:
            client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')  # Test connection
            print("✓ Connected to MongoDB")
            break
        except errors.ServerSelectionTimeoutError:
            print(f"× Could not connect to {connection_string}")
            print("1. Ensure MongoDB is running")
            print("2. Check your connection string")
            retry = input("Try again? (y/n): ").lower()
            if retry != 'y':
                return

    db_name = input("Database name [default: job_assistant]: ").strip() or "job_assistant"
    db = client[db_name]
    
    # Create users collection if not exists
    if "users" not in db.list_collection_names():
        db.create_collection("users")
        print(f"Created 'users' collection in {db_name} database")

    # User creation
    print("\n=== Create New User ===")
    while True:
        username = input("Username: ").strip()
        if username:
            break
        print("Username cannot be empty!")

    email = input("Email: ").strip()
    name = input("Full Name: ").strip()

    while True:
        password = getpass.getpass("Password: ").strip()
        confirm = getpass.getpass("Confirm Password: ").strip()
        
        if len(password) < 8:
            print("Password must be at least 8 characters")
        elif password != confirm:
            print("Passwords don't match!")
        else:
            break

    # Check if user exists
    if db.users.find_one({"username": username}):
        print(f"Error: Username '{username}' already exists!")
        return

    # Create user document
    user = {
        "username": username,
        "email": email,
        "name": name,
        "password": hash_password(password)
    }

    # Insert into database
    try:
        db.users.insert_one(user)
        print(f"\n✓ Successfully created user: {username}")
        print(f"Database: {db_name}")
        print(f"Collection: users")
    except Exception as e:
        print(f"Error creating user: {str(e)}")

if __name__ == "__main__":
    create_user()