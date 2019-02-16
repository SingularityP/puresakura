DROP database IF EXISTS puresakura;

CREATE DATABASE puresakura;

USE puresakura;

CREATE TABLE users(
    `id` varchar(50) not null,
    `email` varchar(50) not null,
    `passwd` varchar(50) not null,
    `admin` bool not null,
    `name` varchar(50) not null,
    `created_at` real not null,
	UNIQUE KEY `idx_email` (`email`),
	KEY `idx_created_at` (`created_at`),
	PRIMARY KEY (`id`)
) engine=innodb default charset=utf8;

CREATE TABLE blogs(
	`id` varchar(50) not null,
	`user_id` varchar(50) not null,
	`user_name` varchar(50) not null,
	`name` varchar(50) not null,
	`summary` varchar(200) not null,
	`content` mediumtext not null,
	`created_at` real not null,
	`readers` int not null,
	`sort` int not null,
	KEY `idx_created_at` (`created_at`),
	PRIMARY KEY (`id`)
) engine=innodb default charset=utf8;

CREATE TABLE comments(
	`id` varchar(50) not null,
	`blog_id` varchar(50) not null,
	`user_id` varchar(50) not null,
	`user_name` varchar(50) not null,
	`content` text not null,
	`created_at` real not null,
	KEY `idx_created_at` (`created_at`),
	KEY `idx_blog_id` (`blog_id`),
	PRIMARY KEY (`id`)
) engine=innodb default charset=utf8;

CREATE TABLE replies(
	`id` varchar(50) not null,
	`user_id` varchar(50) not null,
	`user_name` varchar(50) not null,
	`target_cmid` varchar(50) not null,
	`target_name` varchar(50) not null,
	`content` text not null,
	`created_at` real not null,
	KEY `idx_created_at` (`created_at`),
	PRIMARY KEY (`id`)
) engine=innodb default charset=utf8;

INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('001', '10010', 'Sakura', 'Title 1', 'Summary 1', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 2400000, 0, 1);
INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('002', '10011', 'Jack', 'Title 2', 'Summary 2', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 2402343, 0, 1);
INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('003', '10012', 'Ben', 'Title 3', 'Summary 3', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 2405234, 0, 1);
INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('004', '10013', 'Jane', 'Title 4', 'Summary 4', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 24005344, 0, 1);
INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('005', '10014', 'Ken', 'Title 5', 'Summary 5', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 24034532, 0, 1);

INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('006', '10010', 'Aen', 'Title 6', 'Summary 6', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 24012423, 0, 1);
INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('007', '10011', 'Cen', 'Title 7', 'Summary 7', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 2402343, 0, 1);
INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('008', '10012', 'Den', 'Title 8', 'Summary 8', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 2405234, 0, 1);
INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('009', '10013', 'Een', 'Title 9', 'Summary 9', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 21345343, 0, 1);
INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('010', '10014', 'Fen', 'Title 10', 'Summary 10', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 53421123, 0, 1);

INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('011', '10010', 'Neo', 'Title 11', 'Summary 11', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 2400000, 0, 1);
INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('012', '10011', 'Trinity', 'Title 12', 'Summary 12', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 2402343, 0, 1);
INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('013', '10012', 'Christina', 'Title 13', 'Summary 13', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 2405234, 0, 1);
INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('014', '10013', 'Obama', 'Title 14', 'Summary 14', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 24005344, 0, 1);
INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('015', '10014', 'Trump', 'Title 15', 'Summary 15', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 24034532, 0, 1);

INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('016', '10016', 'Gen', 'Title 16', 'Summary 16', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 24012343, 0, 1);
INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('017', '10017', 'Hen', 'Title 17', 'Summary 17', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 24346543, 0, 1);
INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('018', '10018', 'Ien', 'Title 18', 'Summary 18', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 2405463, 0, 1);
INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('019', '10019', 'Jen', 'Title 19', 'Summary 19', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 21342143, 0, 1);
INSERT INTO blogs (id, user_id, user_name, name, summary, content, created_at, readers, sort) VALUES ('020', '10020', 'Len', 'Title 20', 'Summary 20', 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Qui dolorum, neque, praesentium modi repudiandae sit repellendus sint excepturi suscipit nam et, porro beatae placeat a eligendi delectus unde fuga doloremque.', 5534531123, 0, 1);