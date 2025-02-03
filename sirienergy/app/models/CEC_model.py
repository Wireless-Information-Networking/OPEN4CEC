import redis
import json
from app.config import Config
import hashlib
import sys

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class RedisModel:
    def __init__(self):
        """
        Initializes the RedisModel class by creating a connection to the Redis server.
        
        Input: None
        Output: None
        """
        self.client = redis.StrictRedis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            decode_responses=True
        )
        
    def create_user(self, user_name, user_email, user_password):
        """
        Creates a new user in the Redis database with the provided user details.
        
        Input:
            user_name (str): The name of the user.
            user_email (str): The email of the user (used as a unique key).
            user_password (str): The password of the user (will be hashed).
        
        Output:
            dict: A message confirming the user creation.
        """
        key = f"user:{user_email}"

        # Define user data
        user_document = {
            "user_name": user_name,
            "user_email": user_email,
            "user_password": hash_password(user_password),  # Use the stable hash function
            "user_consumption": {},  # Initialize as an object
            "user_production": {}    # Initialize as an object
        }

        # Save to Redis
        self.client.execute_command('JSON.SET', key, '.', json.dumps(user_document))

        return {"message": f"User '{user_name}' with e-mail {user_email} has been successfully created."}

    def add_consumption(self, user_email, date, hour, value):
        """
        Adds a consumption record for a user on a specific date and hour.
        
        Input:
            user_email (str): The email of the user (used as a unique key).
            date (str): The date of the consumption record.
            hour (str): The hour of the consumption record.
            value (float): The consumption value to be added.
        
        Output:
            dict: A message confirming the consumption record addition.
        """
        key = f"user:{user_email}"
        base_path = "$.user_consumption"

        # Initialize user_consumption if it doesn't exist
        try:
            existing_data = self.client.execute_command('JSON.GET', key, base_path)
            if existing_data is None or existing_data == "[]":
                self.client.execute_command('JSON.SET', key, base_path, "{}")
        except Exception as e:
            raise ValueError(f"Failed to initialize consumption: {e}")

        # Initialize date if it doesn't exist
        try:
            date_path = f"{base_path}.{date}"
            existing_date = self.client.execute_command('JSON.GET', key, date_path)
            if existing_date is None or existing_date == "[]":
                self.client.execute_command('JSON.SET', key, date_path, "{}")
        except Exception as e:
            raise ValueError(f"Failed to initialize date: {e}")

        # Increment or set the specific hour value
        try:
            hour_path = f"{base_path}.{date}.{hour}"
            increment = self.client.execute_command('JSON.NUMINCRBY', key, hour_path, value)
            if increment is None or increment == "[]":
                self.client.execute_command('JSON.SET', key, hour_path, value)
        except Exception as e:
            raise ValueError(f"Failed to update consumption value: {e}")

        return {"message": f"Consumption of {value} added for {date} at {hour}."}

    def add_production(self, user_email, date, hour, value):
        """
        Adds a production record for a user on a specific date and hour.
        
        Input:
            user_email (str): The email of the user (used as a unique key).
            date (str): The date of the production record.
            hour (str): The hour of the production record.
            value (float): The production value to be added.
        
        Output:
            dict: A message confirming the production record addition.
        """
        key = f"user:{user_email}"
        base_path = "$.user_production"

        # Initialize user_production if it doesn't exist
        try:
            existing_data = self.client.execute_command('JSON.GET', key, base_path)
            if existing_data is None or existing_data == "[]":
                self.client.execute_command('JSON.SET', key, base_path, "{}")
        except Exception as e:
            raise ValueError(f"Failed to initialize production: {e}")

        # Initialize date if it doesn't exist
        try:
            date_path = f"{base_path}.{date}"
            existing_date = self.client.execute_command('JSON.GET', key, date_path)
            if existing_date is None or existing_date == "[]":
                self.client.execute_command('JSON.SET', key, date_path, "{}")
        except Exception as e:
            raise ValueError(f"Failed to initialize date: {e}")

        # Increment or set the specific hour value
        try:
            hour_path = f"{base_path}.{date}.{hour}"
            increment = self.client.execute_command('JSON.NUMINCRBY', key, hour_path, value)
            if increment is None or increment == "[]":
                self.client.execute_command('JSON.SET', key, hour_path, value)
        except Exception as e:
            raise ValueError(f"Failed to update production value: {e}")

        return {"message": f"Production of {value} added for {date} at {hour}."}
    
    def get_user(self, user_email):
        """
        Retrieves the user data from the Redis database based on the user's email.
        
        Input:
            user_email (str): The email of the user (used as a unique key).
        
        Output:
            dict: The user data in JSON format, or None if the user does not exist.
        """
        key = f"user:{user_email}"
        json_data = self.client.execute_command('JSON.GET', key)
        print(f"""[CEC Model] (get_user)
                  Key: {key}, Query result: {json_data}""", file=sys.stderr)
        if json_data is None:
            return None
        else:
            return json.loads(json_data)

    def get_production_day(self, user_email, date):
        """
        Retrieves the production record for a user on a specific date.
        
        Input:
            user_email (str): The email of the user (used as a unique key).
            date (str): The date of the production record.
        
        Output:
            dict: The production data for the specified date, or a default empty structure if no data exists.
        """
        key = f"user:{user_email}"
        base_path = "$.user_production"
        date_path = f"{base_path}.{date}"
        try:
            date_path = f"{base_path}.{date}"
            existing_date = self.client.execute_command('JSON.GET', key, date_path)
            print(f"""[CEC Model] (get_production_day)
                  Key: {key}, Path: {date_path}, Query result: {existing_date}""", file=sys.stderr)
            if existing_date is None or existing_date == "[]":
                default_struct = [{}]
                return default_struct
            else:
                production = self.client.execute_command('JSON.GET', key, date_path)
                return json.loads(production)
        except Exception as e:
            raise ValueError(f"Failed to initialize date: {e}")
        
    def get_consumption_day(self, user_email, date):
        """
        Retrieves the consumption record for a user on a specific date.
        
        Input:
            user_email (str): The email of the user (used as a unique key).
            date (str): The date of the consumption record.
        
        Output:
            dict: The consumption data for the specified date, or a default empty structure if no data exists.
        """
        key = f"user:{user_email}"
        base_path = "$.user_consumption"
        date_path = f"{base_path}.{date}"
        try:
            date_path = f"{base_path}.{date}"
            existing_date = self.client.execute_command('JSON.GET', key, date_path)
            print(f"""[CEC Model] (get_consumption_day)
                  Key: {key}, Path: {date_path}, Query result: {existing_date}""", file=sys.stderr)
            if existing_date is None or existing_date == "[]":
                default_struct = [{}]
                return default_struct
            else:
                consumption = self.client.execute_command('JSON.GET', key, date_path)
                return json.loads(consumption)
        except Exception as e:
            raise ValueError(f"Failed to initialize date: {e}") 

    
