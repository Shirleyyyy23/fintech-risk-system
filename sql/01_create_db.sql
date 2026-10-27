-- 01_create_db.sql
-- 创建金融风控系统数据库（在 Navicat 或 MySQL CLI 执行一次即可）

CREATE DATABASE IF NOT EXISTS fintech_risk
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE fintech_risk;

-- 后续星型模型在 dw_credit.sql / dw_aml.sql 中建立，本文件只负责建库。
SELECT 'Database fintech_risk ready.' AS status;
