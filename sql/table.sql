-- 创建数据库
CREATE DATABASE IF NOT EXISTS talent_flow;
USE talent_flow;

# -- 创建包含经纬度的城市信息表
# CREATE TABLE IF NOT EXISTS city_info (
#     id INT PRIMARY KEY AUTO_INCREMENT,
#     city_name VARCHAR(50) NOT NULL COMMENT '城市名称',
#     count INT NOT NULL COMMENT '数量统计值',
#     longitude DECIMAL(10, 6) NOT NULL COMMENT '经度（保留6位小数）',
#     latitude DECIMAL(10, 6) NOT NULL COMMENT '纬度（保留6位小数）',
#     country VARCHAR(30) NOT NULL COMMENT '所属国家'
# );
#
# -- 插入10条包含经纬度的城市数据
# INSERT INTO city_info (city_name, count, longitude, latitude, country) VALUES
# ('北京', 120, 116.407400, 39.904200, '中国'),
# ('上海', 150, 121.473700, 31.230400, '中国'),
# ('广州', 90, 113.280700, 23.125100, '中国'),
# ('深圳', 110, 114.068300, 22.545500, '中国'),
# ('纽约', 85, -74.006000, 40.712800, '美国'),
# ('伦敦', 75, -0.127600, 51.507200, '英国'),
# ('东京', 130, 139.691700, 35.689500, '日本'),
# ('巴黎', 60, 2.352200, 48.856600, '法国'),
# ('悉尼', 45, 151.209300, -33.868800, '澳大利亚'),
# ('迪拜', 70, 55.270800, 25.204800, '阿联酋');

create table country_info(
    id int not null auto_increment primary key ,
    country char(25) not null ,
    cntry char(3) not null,
    count int not null default 0,
    longitude decimal(10, 6),
    latitude decimal(10, 6)
);


CREATE TABLE talent_persons (
    id INT PRIMARY KEY AUTO_INCREMENT,
    authfull VARCHAR(255) NOT NULL,
    inst_name VARCHAR(255),
    cntry CHAR(3),
    np6023 INT,
    firstyr int,
    lastyr int,
    rank_ns INT,
    nc9623_ns INT,
    h23_ns INT,
    hm23_ns DECIMAL(8,4),
    nps_ns INT,
    ncs_ns INT,
    cpsf_ns INT,
    ncsf_ns INT,
    npsfl_ns INT,
    ncsfl_ns INT,
    c_ns DECIMAL(8,4),
    npciting_ns INT,
    cprat_ns DECIMAL(8,4),
    np6023_cited9623_ns INT,
    self_pct DECIMAL(5,2),
    rank_all INT,
    nc9623_all INT,
    h23_all INT,
    hm23_all DECIMAL(8,4),
    nps_all INT,
    ncs_all INT,
    cpsf_all INT,
    ncsf_all INT,
    npsfl_all INT,
    ncsfl_all INT,
    c_all DECIMAL(8,4),
    npciting_all INT,
    cprat_all DECIMAL(8,4),
    np6023_cited9623_all INT,
    np6023_rw INT,
    nc9623_to_rw INT,
    nc9623_rw INT,
    sm_subfield_1 VARCHAR(255),
    sm_subfield_1_frac DECIMAL(6,4),
    sm_subfield_2 VARCHAR(255),
    sm_subfield_2_frac DECIMAL(6,4),
    sm_field VARCHAR(255),
    sm_field_frac DECIMAL(6,4),
    rank_sm_subfield_1 INT,
    rank_sm_subfield_1_ns INT,
    sm_subfield_1_count INT
);


