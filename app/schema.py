instructions = [
    'SET FOREIGN_KEY_CHECKS=0;',
    'DROP TABLE IF EXISTS collection;',
    'SET FOREIGN_KEY_CHECKS=1;',
    """
    CREATE TABLE collection (
        id INT PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(100) UNIQUE NOT NULL,
        fabrication_period VARCHAR(50) NOT NULL,
        release_date DATE NOT NULL
    );
    """,
]