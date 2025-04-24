use bookstore;

CREATE USER 'otheruser'@'%' IDENTIFIED BY '123456';
GRANT all privileges ON bookstore.* TO 'otheruser'@'%';
FLUSH PRIVILEGES;
