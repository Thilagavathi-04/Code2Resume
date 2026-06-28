import re

DATABASE_INDICATORS = {
    "MongoDB": [r"mongodb", r"mongoose", r"MONGODB_URI", r"\.model\("],
    "PostgreSQL": [r"postgresql", r"postgres", r"psycopg", r"asyncpg", r"DATABASE_URL.*postgres"],
    "MySQL": [r"mysql", r"mysql2", r"pymysql"],
    "SQLite": [r"sqlite", r"\.db\b", r"\.sqlite3\b"],
    "Redis": [r"redis", r"REDIS_URL", r"ioredis"],
    "Neo4j": [r"neo4j", r"cypher"],
    "Supabase": [r"supabase", r"SUPABASE_URL"],
    "Firebase Firestore": [r"firestore", r"firebase.*database"],
    "Milvus": [r"milvus"],
    "Pinecone": [r"pinecone", r"PINECONE_API_KEY"],
    "FAISS": [r"faiss"],
    "Qdrant": [r"qdrant"],
    "ChromaDB": [r"chromadb", r"chroma"],
    "Elasticsearch": [r"elasticsearch", r"elastic"],
    "DynamoDB": [r"dynamodb", r"boto3.*dynamo"],
    "Cassandra": [r"cassandra"],
    "MariaDB": [r"mariadb"],
    "CouchDB": [r"couchdb"],
    "InfluxDB": [r"influxdb"],
    "TimescaleDB": [r"timescaledb"],
}


def analyze_databases(tree: list, dependencies: dict, readme: str, tech_stack: dict) -> dict:
    relational = []
    nosql = []
    vector_db = []
    time_series = []

    relational_names = {"PostgreSQL", "MySQL", "SQLite", "MariaDB"}
    nosql_names = {"MongoDB", "Redis", "Neo4j", "CouchDB", "DynamoDB", "Cassandra", "Elasticsearch"}
    vector_names = {"Milvus", "Pinecone", "FAISS", "Qdrant", "ChromaDB", "Supabase", "Firebase Firestore"}
    ts_names = {"TimescaleDB", "InfluxDB"}

    all_deps = []
    for cat in dependencies.values():
        if isinstance(cat, list):
            all_deps.extend(cat)
    dep_text = " ".join(all_deps).lower()

    all_tech = []
    for cat in tech_stack.values():
        if isinstance(cat, list):
            all_tech.extend(cat)
    tech_text = " ".join(all_tech).lower()

    readme_lower = readme.lower() if readme else ""
    all_paths = [item.get("path", "") for item in tree or []]
    path_text = " ".join(all_paths).lower()

    combined = f"{dep_text} {tech_text} {readme_lower} {path_text}"

    for db_name, patterns in DATABASE_INDICATORS.items():
        for pattern in patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                if db_name in relational_names and db_name not in relational:
                    relational.append(db_name)
                elif db_name in nosql_names and db_name not in nosql:
                    nosql.append(db_name)
                elif db_name in vector_names and db_name not in vector_db:
                    vector_db.append(db_name)
                elif db_name in ts_names and db_name not in time_series:
                    time_series.append(db_name)
                break

    return {
        "relational": relational[:5],
        "nosql": nosql[:5],
        "vector_databases": vector_db[:5],
        "time_series": time_series[:3],
        "total_databases": len(relational) + len(nosql) + len(vector_db) + len(time_series),
        "has_vector_store": len(vector_db) > 0,
    }
