# ML FastAPI Project

This project is a machine learning application built using FastAPI, a modern web framework for building APIs with Python. The application serves machine learning models via RESTful APIs, enabling seamless integration with other systems.

## Features

- **FastAPI Framework**: High-performance API development.
- **Docker**: Containerized by docker
- **Alembic**: Managing database migrations
- **PostgreSQL**: Relational database management
- **Model Serving**: Deploy and serve machine learning models.
- **Scalability**: Easily scalable for production use.
- **Interactive Documentation**: Auto-generated Swagger UI and ReDoc.
- **CI/CD pipeline**: This is backed up with deployable CI/CD
- **Redis/Kafka/websockets**: Real time data integration for model training


## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- scikit-learn (or other ML libraries as needed)
- Docker

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/ml_fastapi.git
    cd ml_fastapi
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Start the FastAPI server using the Makefile:
    ```bash
    make run
    ```

2. To contenarize 
    ``` bash 
    make docker-build
    ```

3. Run the container 
    ``` bash 
    make docker-run
    ```
4. Stop the container 
    ``` bash 
    make docker-stop
    ```

5. Logs for the container 
    ``` bash 
    make docker-logs
    ```

6. Migrate the database
    ``` bash 
    make docker-migrate
    ```

2. Access the API documentation:
    - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
    - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

3. Interact with the API to send data and receive predictions.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [scikit-learn](https://scikit-learn.org/)
