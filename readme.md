#### 数据库任务任务清单表和目标网站配置表

```mysql
CREATE TABLE `crawl_tasks` (
  `id` BIGINT AUTO_INCREMENT,
  `site_id` SMALLINT NOT NULL COMMENT '网站ID',
  `url` VARCHAR(1000) NOT NULL,
  `method` ENUM('GET','POST') DEFAULT 'GET',
  `payload` TEXT COMMENT 'POST数据',
  `use_selenium` TINYINT(1) DEFAULT 0,
  `parser_module` VARCHAR(50) NOT NULL,
  `priority` TINYINT DEFAULT 1 COMMENT '1-5优先级',
  `retry_count` TINYINT DEFAULT 0,
  `meta_data` JSON,
  `status` ENUM('pending','processing','failed','completed') DEFAULT 'pending',
  `create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY(`id`),
  INDEX `idx_site_status` (`site_id`, `status`),
  INDEX `idx_priority` (`priority`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `site_config` (
  `site_id` SMALLINT AUTO_INCREMENT,
  `site_name` VARCHAR(50) NOT NULL,
  `domain` VARCHAR(100) NOT NULL,
  `request_interval` INT DEFAULT 1000 COMMENT '毫秒',
  `concurrent_limit` TINYINT DEFAULT 3,
  `need_js` TINYINT(1) DEFAULT 0,
  `need_proxy` TINYINT(1) DEFAULT 1,
  `cookie_strategy` ENUM('none','persist','rotate') DEFAULT 'none',
  `headers_template` JSON,
  PRIMARY KEY(`site_id`)
);
```