create table accounts(user_id int not null auto_increment primary key,
                      username varchar(50),
                      email varchar(100),
                      password varchar(100),
                      unique(email)
                    );

create table books(book_id int not null auto_increment primary key,
                   book_name varchar(50),
                   author varchar(50),
                   book_desc varchar(500)
                   );

create table clothes(clothes_id int not null auto_increment primary key,
                   gender varchar(50),
                   category varchar(50),
                   other varchar(500)
                   );

create table user_session
   (session_id int not null auto_increment primary key,
    user_id    int not null,
    login_date date,
    status     varchar(10) enum('active','inactive')
   );
