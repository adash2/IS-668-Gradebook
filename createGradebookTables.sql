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
  a_grade DOUBLE,
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

INSERT INTO class
VALUES
(1, 'IS 668', 'Dr. Paul Comitz'),
(2, 'IS 672', 'Dr. Agusto Casas'),
(3, 'IS 698', 'Dr. George Karabatis'),
(4, 'IS 633', 'Dr. Zhiyuan Chen');

INSERT INTO assignment
VALUES 
(1, 'Assignment 1', 98.5, 3, 1),
(2, 'Assignment 2', 76.8, 2, 2),
(3, 'Assignment 3', 94.5, 1, 3),
(4, 'Assignment 4', 100, 4, 4);
 
INSERT INTO studentClass
VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4);
