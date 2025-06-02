---
title: Configure an external database
slug: /configuration-custom-database
---
Langflow's default database is [SQLite](https://www.sqlite.org/docs.html), but you can configure Langflow to use PostgreSQL or MySQL instead.

This guide walks you through setting up an external database for Langflow by replacing the default SQLite connection string `sqlite:///./langflow.db` with PostgreSQL or MySQL.

## Prerequisites

Choose one of the following databases:
* A [PostgreSQL](https://www.pgadmin.org/download/) database
* A [MySQL](https://dev.mysql.com/downloads/) database

## Connect Langflow to an external database

### PostgreSQL

To connect Langflow to PostgreSQL, follow these steps.

1. Find your PostgreSQL database's connection string.
It looks like `postgresql://user:password@host:port/dbname`.

### MySQL

To connect Langflow to MySQL, follow these steps.

1. Find your MySQL database's connection string.
It looks like `mysql://user:password@host:port/dbname`.

## Database connection setup

For both PostgreSQL and MySQL, the setup process is similar:

1. Obtain your database connection string in the appropriate format:
   - **PostgreSQL**: `postgresql://user:password@host:port/dbname`
   - **MySQL**: `mysql://user:password@host:port/dbname`

The hostname in your connection string depends on how you're running your database.
- If you're running the database directly on your machine, use `localhost`.
- If you're running the database in Docker Compose, use the service name, such as `postgres` or `mysql`.
- If you're running the database in a separate Docker container with `docker run`, use the container's IP address or network alias.

2. Create a `.env` file for configuring Langflow.
```
touch .env
```

3. To set the database URL environment variable, add it to your `.env` file:

**For PostgreSQL:**
```text
LANGFLOW_DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
```

**For MySQL:**
```text
LANGFLOW_DATABASE_URL="mysql://user:password@localhost:3306/dbname"
```

:::tip
The Langflow project includes a [`.env.example`](https://github.com/langflow-ai/langflow/blob/main/.env.example) file to help you get started.
You can copy the contents of this file into your own `.env` file and replace the example values with your own preferred settings.
Replace the value for `LANGFLOW_DATABASE_URL` with your database connection string.
:::

4. Install the appropriate database dependencies:

**For PostgreSQL:**
```bash
uv pip install "langflow[postgresql]"
```

**For MySQL:**
```bash
uv pip install "langflow[mysql]"
```

5. Run Langflow with the `.env` file:
```bash
uv run langflow run --env-file .env
```

6. In Langflow, create traffic by running a flow.
7. Inspect your database deployment's tables and activity.
New tables and traffic are created.

## Example docker-compose.yml configurations

### PostgreSQL example

The Langflow project includes a [docker-compose.yml](https://github.com/langflow-ai/langflow/blob/main/docker_example/docker-compose.yml) file for quick deployment with PostgreSQL.

This configuration launches Langflow and PostgreSQL containers in the same Docker network, ensuring proper connectivity between services. It also sets up persistent volumes for both Langflow and PostgreSQL data.

To start the services, navigate to the `/docker_example` directory, and then run `docker-compose up`.

```yaml
services:
  langflow:
    image: langflowai/langflow:latest    # or another version tag on https://hub.docker.com/r/langflowai/langflow
    pull_policy: always                   # set to 'always' when using 'latest' image
    ports:
      - "7860:7860"
    depends_on:
      - postgres
    environment:
      - LANGFLOW_DATABASE_URL=postgresql://langflow:langflow@postgres:5432/langflow
      # This variable defines where the logs, file storage, monitor data, and secret keys are stored.
      - LANGFLOW_CONFIG_DIR=app/langflow
    volumes:
      - langflow-data:/app/langflow

  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: langflow
      POSTGRES_PASSWORD: langflow
      POSTGRES_DB: langflow
    ports:
      - "5432:5432"
    volumes:
      - langflow-postgres:/var/lib/postgresql/data

volumes:
  langflow-postgres:    # Persistent volume for PostgreSQL data
  langflow-data:        # Persistent volume for Langflow data
```

### MySQL example

Here's an example docker-compose.yml configuration for Langflow with MySQL:

```yaml
services:
  langflow:
    image: langflowai/langflow:latest    # or another version tag on https://hub.docker.com/r/langflowai/langflow
    pull_policy: always                   # set to 'always' when using 'latest' image
    ports:
      - "7860:7860"
    depends_on:
      - mysql
    environment:
      - LANGFLOW_DATABASE_URL=mysql://langflow:langflow@mysql:3306/langflow
      # This variable defines where the logs, file storage, monitor data, and secret keys are stored.
      - LANGFLOW_CONFIG_DIR=app/langflow
    volumes:
      - langflow-data:/app/langflow

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_USER: langflow
      MYSQL_PASSWORD: langflow
      MYSQL_DATABASE: langflow
    ports:
      - "3306:3306"
    volumes:
      - langflow-mysql:/var/lib/mysql
    command: --default-authentication-plugin=mysql_native_password

volumes:
  langflow-mysql:     # Persistent volume for MySQL data
  langflow-data:      # Persistent volume for Langflow data
```

:::note
Docker Compose creates an isolated network for all services defined in the docker-compose.yml file. This ensures that the services can communicate with each other using their service names as hostnames, for example, `postgres` or `mysql` in the database URL. If you were to run the database separately using `docker run`, it would be in a different network and Langflow wouldn't be able to connect to it using the service name.
:::

## Deploy multiple Langflow instances with a shared database

To configure multiple Langflow instances that share the same database, modify your `docker-compose.yml` file to include multiple Langflow services.

Use environment variables for more centralized configuration management:

### PostgreSQL multi-instance setup

1. Update your `.env` file with values for your PostgreSQL database:
```text
POSTGRES_USER=langflow
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=langflow
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
LANGFLOW_CONFIG_DIR=app/langflow
LANGFLOW_PORT_1=7860
LANGFLOW_PORT_2=7861
LANGFLOW_HOST=0.0.0.0
```

### MySQL multi-instance setup

1. Update your `.env` file with values for your MySQL database:
```text
MYSQL_USER=langflow
MYSQL_PASSWORD=your_secure_password
MYSQL_DATABASE=langflow
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_HOST=mysql
MYSQL_PORT=3306
LANGFLOW_CONFIG_DIR=app/langflow
LANGFLOW_PORT_1=7860
LANGFLOW_PORT_2=7861
LANGFLOW_HOST=0.0.0.0
```

## Multi-instance docker-compose configuration

For both PostgreSQL and MySQL, you can use the following pattern:
2. Reference these variables in your `docker-compose.yml`:
```yaml
services:
  postgres:
    image: postgres:16
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    ports:
      - "${POSTGRES_PORT}:5432"
    volumes:
      - langflow-postgres:/var/lib/postgresql/data

  langflow-1:
    image: langflowai/langflow:latest
    pull_policy: always
    ports:
      - "${LANGFLOW_PORT_1}:7860"
    depends_on:
      - postgres
    environment:
      - LANGFLOW_DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
      - LANGFLOW_CONFIG_DIR=${LANGFLOW_CONFIG_DIR}
      - LANGFLOW_HOST=${LANGFLOW_HOST}
      - PORT=7860
    volumes:
      - langflow-data-1:/app/langflow

  langflow-2:
    image: langflowai/langflow:latest
    pull_policy: always
    ports:
      - "${LANGFLOW_PORT_2}:7860"
    depends_on:
      - postgres
    environment:
      - LANGFLOW_DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
      - LANGFLOW_CONFIG_DIR=${LANGFLOW_CONFIG_DIR}
      - LANGFLOW_HOST=${LANGFLOW_HOST}
      - PORT=7860
    volumes:
      - langflow-data-2:/app/langflow

volumes:
  langflow-postgres:
  langflow-data-1:
  langflow-data-2:
```

3. Deploy the file with `docker-compose up`.
You can access the first Langflow instance at `http://localhost:7860`, and the second Langflow instance at `http://localhost:7861`.

4. To confirm both instances are using the same database, run the `docker exec` command to start `psql` in your PostgreSQL container.
Your container name may vary.
```bash
docker exec -it docker-test-postgres-1 psql -U langflow -d langflow
```

5. Query the database for active connections:
```sql
langflow=# SELECT * FROM pg_stat_activity WHERE datname = 'langflow';
```

6. Examine the query results for multiple connections with different `client_addr` values, for example `172.21.0.3` and `172.21.0.4`.

Since each Langflow instance runs in its own container on the Docker network, using different incoming IP addresses confirms that both instances are actively connected to the PostgreSQL database.

7. To quit psql, type `quit`.