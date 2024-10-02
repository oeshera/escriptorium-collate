FROM python:3.12-slim-bullseye

# Install packages
RUN apt-get update && apt-get install -y \
	git \
	openjdk-11-jdk \
	openjdk-11-jre \
	ant \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

# Fix certificate issues
RUN apt-get update && \
	apt-get install ca-certificates-java && \
	apt-get clean && \
	update-ca-certificates -f;

RUN pip install --no-cache-dir \ 
	"escriptorium-connector @ git+https://gitlab.com/oeshera/escriptorium_python_connector" \
	escriptorium-collate

CMD [ "sleep", "infinity" ]