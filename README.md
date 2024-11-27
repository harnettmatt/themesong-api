# ThemeSong
## Local Setup
1. Install and launch Postgres app: https://postgresapp.com/downloads.html
2. Add the following to your .zshrc
```sh
# Postgres
export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"
```
3. Install Pyenv: https://github.com/pyenv/pyenv?tab=readme-ov-file#installation
4. Install python version listed in `.python-version` by running command:
```sh
pyenv install
```
5. Install pipenv: `pip install pipenv`
6. Install dependencies
```sh
pipenv install --dev
```
7.
## Remote Setup
1. Build db and API docker containers and launch app by running:
```sh
make rebuild
```
2. Make sure you can navigate to the Swagger docs:
```sh
make docs
```
3. Install ngrok: https://dashboard.ngrok.com/get-started/setup/macos
4. Make API available publicly:
```sh
ngrok http http://localhost:8000
```
5.