# movie-rental-system

######_this project wouldn't have been possible without the help of [parthiv](https://github.com/blip100), my senior at college. so thanks to him._


as the title suggests, this is a web application for managing movie rentals, with support for user, staff, and manager roles, and email notifications.

### features include:
- user authentication (signup, login, logout)
- browse, search, and rent movies
- email notifications and receipt generation
- role based access (user, staff, and manager)

### tech-stack used:
- __backend:__ python and flask
- __frontend:__ html and css (occasionally bootstrap)
- __database:__ sqlite
- __email:__ smtp

### setup instructions:

#### 1. clone the repo
`git clone https://github.com/yourusername/movie-rental-system.git`
`cd movie-rental-flask`

#### 2. create and activate a virtual environment
`python -m venv venv`
`source venv/bin/activate`

#### 3. install dependencies
`pip install -r requirements.txt`

#### 4. configure environment variables
create is a `.env` file in the root dierectory to store sensitive information such as email credentials, secret key, etc.

#### 5. run the application
`python app.py`
