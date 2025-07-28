# Clearnet Forum

This repository provides code for a simulated clearnet cyber-crime forum, designed as an educational tool for learning about cyber threat intelligence, open-source intelligence (OSINT), and web scraping in a safe, legal, and controlled environment. The forum mimics real-world scenarios to help users practice data collection and analysis techniques.

To get started, download and install [Docker](https://docs.docker.com/compose/install/).

## Tech-stack

- Frontend
    - HTML5
    - CSS
    - JavaScript
- Backend
    - Python Flask
    - Jinja2 templating engine
    - SQLite3 


## Running Docker

If you are using Ubuntu 24.04 or later, you can set up and run the forum with the following commands:

```bash
sudo docker compose build
sudo docker compose up -d
```

These commands build the Docker environment and start the forum in the background.

## Accessing the Site

Once the Docker container is running, access the forum by navigating to the following URL in your browser:

```plaintext
http://127.0.0.1:5000
```

## Note

> The automated data population scripts rely on a cron job configured within the Docker environment. Running the site outside of Docker will prevent these scripts from executing, as they depend on the container's configuration.
