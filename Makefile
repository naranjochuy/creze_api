
down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

restart:
	@
	make down
	make up

up:
	docker compose up --build --detach

test:
	docker compose exec creze-api python manage.py test

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  \033[92mup\033[0m                       Runs the app with docker compose."
	@echo "  \033[92mdown\033[0m                     Stops the app with docker containers."
	@echo "  \033[92mps\033[0m                       Shows running containers."
	@echo "  \033[92mrestart\033[0m                  Restart the app with docker compose and show the logs."
