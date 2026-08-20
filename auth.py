import psycopg2
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"

def create_token(username):
    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]      # the username you stored in "sub"
    except JWTError:
        return None                # invalid or expired token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_connection():
    return psycopg2.connect(dbname="workout_app", user="keegantu", host="localhost", port="5432")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(attempt, stored_hash):
    return pwd_context.verify(attempt, stored_hash)

def sign_up(user_name, email, password):
    conn = get_connection()
    cursor = conn.cursor()

    password_hash = hash_password(password)

    query = """
        INSERT INTO users (username, email, password_hash)
        VALUES (%s, %s, %s)
    """
    cursor.execute(query, (user_name, email, password_hash))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"User {user_name} created")
    

# sign_up("keegan", "keegan@example.com", "squats123")

def log_in(username, password):
    # add error handling for nonexistent users
    conn = get_connection()
    cur = conn.cursor()

    password_query = """
        SELECT password_hash FROM users WHERE username = %s
    """

    cur.execute(password_query, (username,))

    result = cur.fetchone()
    hashed_user_password = result[0]
                                  

    conn.commit()
    cur.close()
    conn.close()

    if pwd_context.verify(
        password, hashed_user_password):
            return True
    else:
        return False
    
    



def addWorkout(username):
    conn = get_connection()
    cur = conn.cursor()

    user_id_query = "SELECT id FROM users WHERE username = %s"

    cur.execute(user_id_query, (username,))
    user_id = cur.fetchone()[0]

    insert_query = """
        INSERT INTO workouts (user_id)
        VALUES(%s)
        RETURNING id
    """
    cur.execute(insert_query, (user_id,))
    workout_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    print(f"{username} added a new workout")
    return workout_id


def addSet(workout_id, exercise_id, reps, weight):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        INSERT INTO sets (workout_id, exercise_id, reps, weight)
        VALUES(%s, %s, %s, %s)
        RETURNING id
    """

    cur.execute(query, (workout_id, exercise_id, reps, weight))
    set_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    print(f"Set added to workout")




def volume_over_time(username, exercise_id):
    conn = get_connection()
    cur = conn.cursor()

    user_id_query = """
        SELECT id FROM users WHERE username = %s
    """

    cur.execute(user_id_query, (username,))
    user_id = cur.fetchone()[0]

    volume_query = """
        SELECT workout_date, SUM(weight * reps)
        FROM sets 
        INNER JOIN workouts on sets.workout_id = workouts.id
        WHERE workouts.user_id = %s AND exercise_id = %s
        GROUP BY workout_date
        ORDER BY workout_date
    """

    cur.execute(volume_query,(user_id, exercise_id))
    volume = cur.fetchall()

    cur.close()
    conn.close()

    print(volume)

    return volume




def estimated_1rm_over_time(username, exercise_id):
    conn = get_connection()
    cur = conn.cursor()

    user_id_query = """
        SELECT id FROM users WHERE username = %s
    """

    cur.execute(user_id_query, (username,))
    user_id = cur.fetchone()[0]

    estimated_1rm_over_time_query = """
        SELECT workout_date, MAX(weight * (1 + reps/30.0))
        FROM sets 
        INNER JOIN workouts on sets.workout_id = workouts.id
        WHERE workouts.user_id = %s AND exercise_id = %s
        GROUP BY workout_date
        ORDER BY workout_date
    """

    cur.execute(estimated_1rm_over_time_query,(user_id, exercise_id))
    estimated_1rm_over_time = cur.fetchall()

    cur.close()
    conn.close()

    print(estimated_1rm_over_time)

    return estimated_1rm_over_time

def maxWeight(username, exercise_id):
    conn = get_connection()
    cur = conn.cursor()

    user_id_query = """
            SELECT id FROM users WHERE username = %s
        """
    cur.execute(user_id_query, (username,))
    user_id = cur.fetchone()[0]

    max_weight_query = """
            SELECT Max(weight) FROM sets
            INNER JOIN workouts on sets.workout_id = workouts.id
            WHERE workouts.user_id = %s AND exercise_id = %s
        """

    cur.execute(max_weight_query, (user_id, exercise_id))
    max_weight = cur.fetchone()[0]

    cur.close()
    conn.close()

    return max_weight


def percent_increase(username, exercise_id, from_date):
    #latest_percent = result[-1][2]

    conn = get_connection()
    cur = conn.cursor()

    user_id_query = """
            SELECT id FROM users WHERE username = %s
            """
    cur.execute(user_id_query, (username,))
    user_id = cur.fetchone()[0]

    percent_increase_query = """
        WITH baseline_volume AS (
            SELECT workout_date, SUM(weight * reps) AS base_vol
            FROM sets
            INNER JOIN workouts ON sets.workout_id = workouts.id
            WHERE workouts.user_id = %s AND exercise_id = %s AND workout_date >= %s
            GROUP BY workout_date
        )
        SELECT
            workout_date,
            base_vol,
            (base_vol - FIRST_VALUE(base_vol) OVER (ORDER BY workout_date))
                / FIRST_VALUE(base_vol) OVER (ORDER BY workout_date) * 100 AS percent_increase
        FROM baseline_volume
        ORDER BY workout_date      
    """

    cur.execute(percent_increase_query, (user_id, exercise_id, from_date, from_date))
    result = cur.fetchall()

    cur.close()
    conn.close()

    return result

def get_workouts(username):
    conn = get_connection()
    cur = conn.cursor()

    user_id_query = """
        SELECT id FROM users WHERE username = %s
        """
    cur.execute(user_id_query, (username,))
    user_id = cur.fetchone()[0]

    get_workouts_query = """
        SELECT id, workout_date
        FROM workouts
        WHERE user_id = %s
        ORDER BY workout_date DESC
    """

    cur.execute(get_workouts_query, (user_id,))
    result = cur.fetchall()
    cur.close()
    conn.close()

    return result

def get_sets(workout_id):
    conn = get_connection()
    cur = conn.cursor()

    get_sets_query = """
        SELECT exercises.name, exercise_id, reps, weight
        FROM sets
        INNER JOIN exercises ON sets.exercise_id = exercises.id
        WHERE workout_id = %s
        """

    cur.execute(get_sets_query, (workout_id,))
    result = cur.fetchall()
    cur.close()
    conn.close()

    return result

def get_exercises():
    conn = get_connection()
    cur = conn.cursor()

    get_exercise_query = "SELECT * FROM exercises"

    cur.execute(get_exercise_query)
    result = cur.fetchall()
    cur.close()
    conn.close()

    return result

def get_total_vol_leaderboard():
    conn = get_connection()
    cur = conn.cursor()

    get_vol_leaderboard_query = """
        WITH vol_table AS (
            SELECT username, SUM(weight * reps) AS vol
            FROM sets INNER JOIN workouts ON sets.workout_id = workouts.id
            INNER JOIN users ON workouts.user_id = users.id
            GROUP BY username
        )
        SELECT username, vol, 
        RANK() OVER (ORDER BY vol DESC) AS vol_ranking
        FROM vol_table
        """

    cur.execute(get_vol_leaderboard_query)
    result = cur.fetchall()

    cur.close()
    conn.close()

    return result

print(get_total_vol_leaderboard())
