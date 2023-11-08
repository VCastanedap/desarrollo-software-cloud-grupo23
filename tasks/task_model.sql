CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES users(id),
    original_filename varchar(255),
    converted_filename varchar(255),
    original_filepath varchar(255),
    converted_filepath varchar(255),
    conversion_format varchar(20),
    status varchar(20) default 'unavailable',
    creation_date timestamp
);
