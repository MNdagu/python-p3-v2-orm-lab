from __init__ import CURSOR, CONN
from department import Department
from employee import Employee

class Review:
    all_reviews = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return f"<Review id={self.id} year={self.year} summary={self.summary} employee_id={self.employee_id}>"

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if isinstance(value, int) and value >= 2000:
            self._year = value
        else:
            raise ValueError("Year must be an integer and >= 2000")

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if isinstance(value, str) and len(value) > 0:
            self._summary = value
        else:
            raise ValueError("Summary must be a non-empty string")

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        query = "SELECT id FROM employees WHERE id = ?"
        CURSOR.execute(query, (value,))
        if CURSOR.fetchone():
            self._employee_id = value
        else:
            raise ValueError("employee_id must be a valid Employee ID")

    @classmethod
    def create_table(cls):
        query = """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INTEGER,
            summary TEXT,
            employee_id INTEGER
        )
        """
        CURSOR.execute(query)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        query = "DROP TABLE IF EXISTS reviews"
        CURSOR.execute(query)
        CONN.commit()

    def save(self):
        if self.id is None:
            query = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
            """
            CURSOR.execute(query, (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
            Review.all_reviews[self.id] = self
        else:
            self.update()

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """
        Given a row from the database, this method either returns the existing
        Review instance (if it exists in the `all_reviews` cache) or creates a
        new Review instance from the data.
        """
        sql = """
            SELECT * FROM reviews
        """
        
        id_, year, summary, employee_id = row
        
        row = CURSOR.execute(sql).fetchone()
        print("Retrieved row:", row)
        

        # Check if the review with this id already exists in the cache
        if id_ in cls.all_reviews:
            # Return the cached review instance
            return cls.all_reviews[id_]
        else:
            # Create a new Review instance and add it to the cache
            review = cls(year, summary, employee_id, id=id_)
            cls.all_reviews[id_] = review
            return review
        
       
        
        
    @classmethod
    def find_by_id(cls, review_id):
        query = "SELECT * FROM reviews WHERE id = ?"
        CURSOR.execute(query, (review_id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        query = """
        UPDATE reviews
        SET year = ?, summary = ?, employee_id = ?
        WHERE id = ?
        """
        CURSOR.execute(query, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        query = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(query, (self.id,))
        CONN.commit()
        if self.id in Review.all_reviews:
            del Review.all_reviews[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM reviews"
        CURSOR.execute(query)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]
