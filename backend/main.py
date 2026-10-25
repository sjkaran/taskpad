import sqlite3 as db
class DbHandler:
    def __init__(self, filename: str="taskdb.db"):
        self.filename = filename
        self.conn = db.connect(self.filename)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.conn.cursor()

    def initialize_tables(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS goals(
                gid INTEGER PRIMARY KEY AUTOINCREMENT,
                gname TEXT NOT NULL,
                type INTEGER CHECK (type>0 AND type <=3),
                expiry TEXT,
                pp INTEGER NOT NULL,
                np INTEGER NOT NULL,
                status TEXT,
                gridloc TEXT
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks(
                tid INTEGER PRIMARY KEY AUTOINCREMENT,
                tname TEXT NOT NULL,
                expiry TEXT,
                type INTEGER CHECK (type BETWEEN 1 AND 3),
                points INTEGER NOT NULL,
                gid INTEGER,
                gridloc TEXT,
                FOREIGN KEY (gid) REFERENCE goals(id)
            );
            """
        )

        self.cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS rituals(
                        rid INTEGER PRIMARY KEY AUTOINCREMENT,
                        rname TEXT NOT NULL,
                        gid INTEGER,
                        freq INTEGER CHECK (freq BETWEEN 1 AND 30),
                        type INTEGER CHECK (freq BETWEEN 1 AND 3),
                        duration TEXT,
                        points INTEGER NOT NULL,
                        gridloc TEXT,
                        FOREIGN KEY (gid) REFERENCE goals(gid)
                    );
                    """
                )
        self.cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS ftasks (
                        tid INTEGER PRIMARY KEY,
                        tname TEXT NOT NULL,
                        status INTEGER CHECK (status BETWEEN 0 AND 1),
                        gid INTEGER,
                        points INTEGER,
                        doe TEXT NOT NULL,
                        FOREIGN KEY (gid) REFERENCE goals(gid)
                        )
                    """
                )

        self.cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS frituals (
                        rid PRIMARY KEY,
                        gid INTEGER,
                        points INTEGER NOT NULL,
                        STATUS INTEGER CHECK (staus BETWEEN 0 AND 1),
                        doe TEXT NOT NULL,
                        FOREIGN KEY (gid) REFERENCE goals(gid)
                    )
                    """
                )

        self.conn.commit()
        print("Database schema verified/initiated successfully.")


class main(DbHandler):
    def __init__(self):
        super().__init__()
        super().initialize_tables()
        pass

    # functions to operates the project backend - data processing, algorithms etc.

