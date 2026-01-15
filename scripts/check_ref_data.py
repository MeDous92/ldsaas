import os
from sqlmodel import Session, create_engine, select
from models import Country, City

# Connect to DB inside container (using the URL from docker-compose if we were inside, but here we need to exec)
# Actually, I can run this script INSIDE the container.

def check_data():
    try:
        from db import engine
        with Session(engine) as session:
            countries = session.exec(select(Country)).all()
            print(f"Countries found: {len(countries)}")
            for c in countries:
                print(f"- {c.name} (id={c.id})")
            
            cities = session.exec(select(City)).all()
            print(f"Cities found: {len(cities)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data()
