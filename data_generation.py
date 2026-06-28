import random
from decimal import Decimal
import psycopg2
from psycopg2.extras import execute_values
from faker import Faker

# Database credentials configuration
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "steam_clone",
    "user": "postgres",
    "password": "not-real",
}

# Initializing Faker generator engine
fake = Faker()

# Configuration variables for data scale
NUM_USERS = 50_000
NUM_GAMES = 75_000
NUM_USER_GAMES = 1_500_000
NUM_TRANSACTIONS = 125_000

# --- GENERATE DATA SETS VIA FAKER ---

# 1. Games Dataset
GAMES = []
game_genres = ["RPG", "Action", "Strategy", "FPS", "Simulation", "Sports", "Indie"]
for game_id in range(1, NUM_GAMES + 1):
    game_name = f"{fake.word().capitalize()} {random.choice(['Quest', 'Championship', 'Simulator', 'Evolution', 'Unleashed'])}"
    game_description = f"An epic {random.choice(game_genres)} game featuring {fake.bs()}."[:255]
    release_date = fake.date_between(start_date="-5y", end_date="today")

    # 15% chance to be free-to-play, otherwise a price up to $59.99
    price_val = 0.00 if random.random() < 0.15 else round(random.uniform(4.99, 59.99), 2)
    price = Decimal(str(price_val))

    GAMES.append((game_id, game_name, game_description, release_date, price))

# 2. Users Dataset
USERS = []
for user_id in range(1, NUM_USERS + 1):
    name = fake.user_name()[:50]
    password = fake.sha256()
    email = fake.email()[:100]
    balance = Decimal(str(round(random.uniform(0.00, 250.00), 2)))

    USERS.append((user_id, name, password, email, balance))

# 3. User Games & Library Data Datasets
USER_GAMES = []
USER_GAMES_DATA = []
tracked_combinations = set()

for ug_id in range(1, NUM_USER_GAMES + 1):
    # Ensure unique pairings of user and game to prevent duplicate library rows
    while True:
        user_id = random.randint(1, NUM_USERS)
        game_id = random.randint(1, NUM_GAMES)
        if (user_id, game_id) not in tracked_combinations:
            tracked_combinations.add((user_id, game_id))
            break

    USER_GAMES.append((ug_id, user_id, game_id))

    time_played = random.randint(0, 12000)  # Up to 200 hours played
    date_purchase = fake.date_between(start_date="-3y", end_date="today")

    USER_GAMES_DATA.append((ug_id, time_played, date_purchase))

# 4. Transactions Dataset
TRANSACTIONS = []
for tx_id in range(1, NUM_TRANSACTIONS + 1):
    user_id = random.randint(1, NUM_USERS)
    amount = Decimal(str(round(random.uniform(5.00, 100.00), 2)))
    card_details = f"{fake.credit_card_provider()} ending in {fake.credit_card_number()[-4:]}"[:200]

    TRANSACTIONS.append((tx_id, user_id, amount, card_details))


# --- DATABASE OPERATIONS ---

def table_exists(cursor, table_name: str) -> bool:
    cursor.execute(
        """
        select exists (
            select 1
            from information_schema.tables
            where table_schema = 'public'
              and table_name = %s
        );
        """,
        (table_name,),
    )
    return cursor.fetchone()[0]


def validate_schema(cursor) -> None:
    required_tables = ["users", "games", "user_games", "user_games_data", "transactions"]
    missing_tables = [table for table in required_tables if not table_exists(cursor, table)]

    if missing_tables:
        raise RuntimeError(
            "Missing tables: "
            + ", ".join(missing_tables)
            + ". Create the schema before running this script."
        )


def clear_tables(cursor) -> None:
    cursor.execute(
        """
        truncate table
            transactions,
            user_games_data,
            user_games,
            games,
            users
        restart identity cascade;
        """
    )


def insert_games(cursor) -> None:
    execute_values(
        cursor,
        """
        insert into games (game_id, game_name, game_description, release_date, price)
        values %s;
        """,
        GAMES,
    )


def insert_users(cursor) -> None:
    execute_values(
        cursor,
        """
        insert into users (user_id, name, password, email, balance)
        values %s;
        """,
        USERS,
    )


def insert_user_games(cursor) -> None:
    execute_values(
        cursor,
        """
        insert into user_games (user_games_id, user_id, game_id)
        values %s;
        """,
        USER_GAMES,
    )


def insert_user_games_data(cursor) -> None:
    execute_values(
        cursor,
        """
        insert into user_games_data (user_games_id, time_played, date_purchase)
        values %s;
        """,
        USER_GAMES_DATA,
    )


def insert_transactions(cursor) -> None:
    execute_values(
        cursor,
        """
        insert into transactions (transaction_id, user_id, amount, card_details)
        values %s;
        """,
        TRANSACTIONS,
    )


def print_summary(cursor) -> None:
    cursor.execute("select count(*) from users;")
    users_count = cursor.fetchone()[0]

    cursor.execute("select count(*) from games;")
    games_count = cursor.fetchone()[0]

    cursor.execute("select count(*) from user_games;")
    user_games_count = cursor.fetchone()[0]

    cursor.execute("select count(*) from user_games_data;")
    user_games_data_count = cursor.fetchone()[0]

    cursor.execute("select count(*) from transactions;")
    transactions_count = cursor.fetchone()[0]

    print("Seed completed successfully.")
    print(f"Users inserted: {users_count}")
    print(f"Games inserted: {games_count}")
    print(f"User games connections inserted: {user_games_count}")
    print(f"User games metadata inserted: {user_games_data_count}")
    print(f"Transactions inserted: {transactions_count}")


def main() -> None:
    connection = psycopg2.connect(**DB_CONFIG)

    try:
        with connection:
            with connection.cursor() as cursor:
                validate_schema(cursor)
                clear_tables(cursor)
                insert_games(cursor)
                insert_users(cursor)
                insert_user_games(cursor)
                insert_user_games_data(cursor)
                insert_transactions(cursor)
                print_summary(cursor)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
