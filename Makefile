source-up:
	cd shared && docker network create olist_network || true
	docker-compose up -d postgres_olist

# Этап 1
stage1-up: source-up
	cd stage1-plpgsql && docker-compose up -d

stage1-down:
	cd stage1-plpgsql && docker-compose down
