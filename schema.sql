CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE workouts (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    workout_date TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE sets (
    id SERIAL PRIMARY KEY,
    workout_id INT NOT NULL REFERENCES workouts(id),
    exercise_id INT NOT NULL REFERENCES exercises(id),
    reps INT NOT NULL,
    weight NUMERIC(6,2) NOT NULL
);

