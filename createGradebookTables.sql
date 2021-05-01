CREATE TABLE students (
  s_id INT NOT NULL AUTO_INCREMENT,
  s_last_name VARCHAR(120),
  s_first_name VARCHAR(120),
  s_major VARCHAR(45),
  s_email VARCHAR(120),
  PRIMARY KEY (s_id)
);

CREATE TABLE class (
  c_id INT NOT NULL AUTO_INCREMENT,
  c_name VARCHAR(45),
  c_prof VARCHAR(120),
  PRIMARY KEY (c_id)
);

CREATE TABLE assignment (
  a_id INT NOT NULL AUTO_INCREMENT,
  a_name VARCHAR(120),
  a_grade DOUBLE(4, 2),
  s_id INT,
  c_id INT,
  PRIMARY KEY (a_id),
  CONSTRAINT fk_sid_cid FOREIGN KEY (s_id, c_id)
                        REFERENCES studentClass(s_id, c_id)
);

CREATE TABLE studentClass (
  s_id INT,
  c_id INT,
  FOREIGN KEY (s_id) REFERENCES students (s_id),
  FOREIGN KEY (c_id) REFERENCES class (c_id),
  PRIMARY KEY(s_id, c_id)
);

INSERT INTO students 
VALUES 
(1, 'Eccleston', 'Shaw', 'Biology','seccleston@umbc.edu'),
(2, 'Arterbury', 'Brion', 'Chemical Engineering', 'barterbury@umbc.edu'),
(3, 'Samuel', 'Annalise', 'Information Systems', 'asamuel@umbc.edu'),
(4, 'Ayers', 'Lissa', 'Accounting', 'layers@umbc.edu');
