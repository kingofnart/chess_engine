# Chess Game
This project is a chess game where you can choose to play against a bot using either random moves or a minimax algorithm, or use in pass-and-play mode. Create an account and log in, play a game, then check out your interactive game history.

## How it's made:
The frontend is written in HTML, CSS, JavaScript. The backend is written in Python using Flask framework. Other tech used includes Selenium for testing, Docker for containerization, PostgreSQL for the database, as well as a CI pipeline using Docker Compose and GitHub Actions.

## How it works:
First a user logs in or creates a new account. The game is rendered using HTML and CSS with JavaScript handling user interaction such as button clicks to change game settings, start, resign and reset the game, as well as making move by either clicking or dragging and dropping. When a move is input on the board, the backend receives the input and determines if the move is valid or not. If it's valid, the move will be applied and rendered on the screen, timers switched, and an indicator is toggled to show it's the other color's turn. Otherwise the squares selected for the move are flashed and the game continues waiting for input. The 'Game History' button navigates the user to another page showing their previously played games with time stamps, and allow them to move forward and backward through the moves. 

## How to use:
Download the source code and make sure you have [PostgreSQL](https://www.postgresql.org/download/) installed. Now you need to set up your PostgreSQL database and use the credentials you make in a compose.override.yaml file. First access the Postgres shell: `sudo -u postgres psql` and create a new database: `CREATE DATABASE your_database;` then create a username and password: `CREATE USER your_username WITH ENCRYPTED PASSWORD your_password;` grant privileges to the user on the database: `GRANT ALL PRIVILEGES ON DATABASE your_database TO your_username;` and finally exit the Postgres shell: `\q`. Next generate a sha256 hash with secret key of your choosing: `echo -n "your_secret_key" | openssl dgst -sha256` and save the output (referenced as 'hashed_secret_key' below). Now you need to create a file named compose.override.yaml in the root directory chess_engine/ and enter the contents:
```
services:
  db:
    environment:
      - POSTGRES_DB=your_database
      - POSTGRES_USER=your_username
      - POSTGRES_PASSWORD=your_password

  app:
    environment:
      - POSTGRES_DB=your_database
      - POSTGRES_USER=your_username
      - POSTGRES_PASSWORD=your_password
      - DATABASE_URL=postgres://your_username:your_password@localhost:5432/your_database
      - CHESS_DB_SECRET_KEY=hashed_secret_key

  test:
    environment:
      - POSTGRES_DB=your_database
      - POSTGRES_USER=your_username
      - POSTGRES_PASSWORD=your_password
      - DATABASE_URL=postgres://your_username:your_password@localhost:5432/your_database
      - CHESS_DB_SECRET_KEY=hashed_secret_key
```
You also need to have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed to build the Docker containers. Finally run `docker compose up --build` in the root directory, then go to http://localhost:8000/ in your browser and start interacting with the game!