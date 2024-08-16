FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y \
	git \
	default-jre \ 
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \ 
	"escriptorium-connector @ git+https://gitlab.com/oeshera/escriptorium_python_connector" \
	escriptorium-collate

CMD [ "sleep", "infinity" ]