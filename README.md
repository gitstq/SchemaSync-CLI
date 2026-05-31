<div align="center">

# 🔄 SchemaSync-CLI

**A lightweight, developer-friendly database schema migration tool**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-Coming%20Soon-orange.svg)](https://pypi.org)

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="english"></a>
## 🇺🇸 English

### 🎉 Introduction

**SchemaSync-CLI** is a lightweight database schema migration tool designed for developers who want a simple yet powerful way to manage database schema versions across SQLite, PostgreSQL, and MySQL.

**Why SchemaSync?**
- 🚀 **Zero Configuration** - Works out of the box with sensible defaults
- 📝 **Git-like Workflow** - Version control for your database schema
- 🔄 **Safe Migrations** - Automatic backups and dry-run mode
- 🎯 **Multi-Database** - One tool for SQLite, PostgreSQL, and MySQL
- 💡 **Developer Friendly** - Clean CLI with helpful error messages

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🗄️ **Multi-Database Support** | SQLite, PostgreSQL, MySQL with unified interface |
| 📦 **Migration Management** | Create, apply, and rollback migrations easily |
| 💾 **Automatic Backups** | Backup before every migration for safety |
| 🔍 **Dry Run Mode** | Preview changes before applying them |
| 📊 **Status Tracking** | Clear view of applied and pending migrations |
| ⚙️ **Flexible Configuration** | YAML/JSON config files or environment variables |

### 🚀 Quick Start

#### Installation

```bash
pip install schemasync-cli
```

For PostgreSQL support:
```bash
pip install schemasync-cli[postgresql]
```

For MySQL support:
```bash
pip install schemasync-cli[mysql]
```

For all databases:
```bash
pip install schemasync-cli[all]
```

#### Initialize Project

```bash
# Navigate to your project directory
cd myproject

# Initialize SchemaSync
schemasync init
```

This creates:
- `migrations/` - Directory for migration files
- `backups/` - Directory for database backups
- `schemasync.yaml` - Configuration file

#### Create Your First Migration

```bash
schemasync create "add users table"
```

Edit the generated migration file:

```python
def upgrade():
    return """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(255) NOT NULL UNIQUE,
        email VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

def downgrade():
    return """
    DROP TABLE users;
    """
```

#### Apply Migrations

```bash
# Check status
schemasync status

# Apply all pending migrations
schemasync migrate

# Or preview first (dry run)
schemasync migrate --dry-run
```

#### Rollback (if needed)

```bash
# Rollback last migration
schemasync rollback

# Rollback multiple migrations
schemasync rollback --steps 3

# Rollback to specific version
schemasync rollback --to 20250101000000
```

### 📖 Configuration

Create `schemasync.yaml` in your project root:

```yaml
database:
  driver: sqlite        # sqlite, postgresql, mysql
  host: localhost       # for PostgreSQL/MySQL
  port: 5432           # for PostgreSQL/MySQL
  name: mydatabase.db   # database name or file path
  user: dbuser         # for PostgreSQL/MySQL
  password: dbpass     # for PostgreSQL/MySQL

migrations:
  directory: migrations
  table_name: schema_migrations
  backup_before_migrate: true
  backup_directory: backups

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

Or use environment variables:
```bash
export SCHEMASYNC_DB_DRIVER=postgresql
export SCHEMASYNC_DB_HOST=localhost
export SCHEMASYNC_DB_NAME=mydb
export SCHEMASYNC_DB_USER=user
export SCHEMASYNC_DB_PASSWORD=pass
```

### 📚 Available Commands

| Command | Description |
|---------|-------------|
| `schemasync init` | Initialize migration environment |
| `schemasync create <description>` | Create a new migration |
| `schemasync status` | Show migration status |
| `schemasync migrate` | Run pending migrations |
| `schemasync migrate --dry-run` | Preview migrations |
| `schemasync rollback` | Rollback migrations |
| `schemasync history` | Show migration history |
| `schemasync config` | Show current configuration |

### 💡 Design Philosophy

SchemaSync follows these principles:

1. **Simplicity First** - Easy to learn, easy to use
2. **Safety by Default** - Backups and dry-run for peace of mind
3. **Database Agnostic** - Same commands work across all supported databases
4. **Version Control Friendly** - Migration files are plain Python, perfect for Git

### 📦 Project Type

This is a **CLI Tool/Library** project. No executable releases are required.

Install via pip:
```bash
pip install schemasync-cli
```

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
## 🇨🇳 简体中文

### 🎉 项目介绍

**SchemaSync-CLI** 是一个轻量级数据库Schema迁移工具，专为需要简单但强大的方式来管理SQLite、PostgreSQL和MySQL数据库Schema版本的开发者设计。

**为什么选择 SchemaSync？**
- 🚀 **零配置** - 开箱即用，合理的默认设置
- 📝 **类Git工作流** - 为数据库Schema提供版本控制
- 🔄 **安全迁移** - 自动备份和试运行模式
- 🎯 **多数据库支持** - 一个工具支持多种数据库
- 💡 **开发者友好** - 清晰的CLI界面和有用的错误提示

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🗄️ **多数据库支持** | SQLite、PostgreSQL、MySQL统一接口 |
| 📦 **迁移管理** | 轻松创建、应用和回滚迁移 |
| 💾 **自动备份** | 每次迁移前自动备份，确保安全 |
| 🔍 **试运行模式** | 在应用前预览变更 |
| 📊 **状态追踪** | 清晰查看已应用和待处理的迁移 |
| ⚙️ **灵活配置** | 支持YAML/JSON配置文件或环境变量 |

### 🚀 快速开始

#### 安装

```bash
pip install schemasync-cli
```

PostgreSQL支持：
```bash
pip install schemasync-cli[postgresql]
```

MySQL支持：
```bash
pip install schemasync-cli[mysql]
```

所有数据库：
```bash
pip install schemasync-cli[all]
```

#### 初始化项目

```bash
# 进入项目目录
cd myproject

# 初始化 SchemaSync
schemasync init
```

这会创建：
- `migrations/` - 迁移文件目录
- `backups/` - 数据库备份目录
- `schemasync.yaml` - 配置文件

#### 创建第一个迁移

```bash
schemasync create "add users table"
```

编辑生成的迁移文件：

```python
def upgrade():
    return """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(255) NOT NULL UNIQUE,
        email VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

def downgrade():
    return """
    DROP TABLE users;
    """
```

#### 应用迁移

```bash
# 查看状态
schemasync status

# 应用所有待处理的迁移
schemasync migrate

# 或先预览（试运行）
schemasync migrate --dry-run
```

#### 回滚（如需要）

```bash
# 回滚上一个迁移
schemasync rollback

# 回滚多个迁移
schemasync rollback --steps 3

# 回滚到指定版本
schemasync rollback --to 20250101000000
```

### 📖 配置说明

在项目根目录创建 `schemasync.yaml`：

```yaml
database:
  driver: sqlite        # sqlite, postgresql, mysql
  host: localhost       # PostgreSQL/MySQL用
  port: 5432           # PostgreSQL/MySQL用
  name: mydatabase.db   # 数据库名称或文件路径
  user: dbuser         # PostgreSQL/MySQL用
  password: dbpass     # PostgreSQL/MySQL用

migrations:
  directory: migrations
  table_name: schema_migrations
  backup_before_migrate: true
  backup_directory: backups

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

或使用环境变量：
```bash
export SCHEMASYNC_DB_DRIVER=postgresql
export SCHEMASYNC_DB_HOST=localhost
export SCHEMASYNC_DB_NAME=mydb
export SCHEMASYNC_DB_USER=user
export SCHEMASYNC_DB_PASSWORD=pass
```

### 📚 可用命令

| 命令 | 描述 |
|------|------|
| `schemasync init` | 初始化迁移环境 |
| `schemasync create <描述>` | 创建新迁移 |
| `schemasync status` | 显示迁移状态 |
| `schemasync migrate` | 运行待处理的迁移 |
| `schemasync migrate --dry-run` | 预览迁移 |
| `schemasync rollback` | 回滚迁移 |
| `schemasync history` | 显示迁移历史 |
| `schemasync config` | 显示当前配置 |

### 💡 设计理念

SchemaSync 遵循以下原则：

1. **简洁优先** - 易于学习，易于使用
2. **默认安全** - 备份和试运行模式让您安心
3. **数据库无关** - 相同命令适用于所有支持的数据库
4. **版本控制友好** - 迁移文件是纯Python，完美适配Git

### 📦 项目类型

这是一个 **CLI工具/库** 项目。不需要发布可执行文件。

通过pip安装：
```bash
pip install schemasync-cli
```

### 🤝 贡献指南

欢迎贡献！请随时提交Pull Request。

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交变更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 📄 开源协议

本项目采用 MIT 协议 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

<a name="繁體中文"></a>
## 🇹🇼 繁體中文

### 🎉 專案介紹

**SchemaSync-CLI** 是一個輕量級資料庫Schema遷移工具，專為需要簡單但強大的方式來管理SQLite、PostgreSQL和MySQL資料庫Schema版本的開發者設計。

**為什麼選擇 SchemaSync？**
- 🚀 **零配置** - 開箱即用，合理的預設設定
- 📝 **類Git工作流** - 為資料庫Schema提供版本控制
- 🔄 **安全遷移** - 自動備份和試運行模式
- 🎯 **多資料庫支援** - 一個工具支援多種資料庫
- 💡 **開發者友善** - 清晰的CLI介面和有用的錯誤提示

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🗄️ **多資料庫支援** | SQLite、PostgreSQL、MySQL統一介面 |
| 📦 **遷移管理** | 輕鬆建立、應用和回滾遷移 |
| 💾 **自動備份** | 每次遷移前自動備份，確保安全 |
| 🔍 **試運行模式** | 在應用前預覽變更 |
| 📊 **狀態追蹤** | 清晰查看已應用和待處理的遷移 |
| ⚙️ **靈活配置** | 支援YAML/JSON設定檔或環境變數 |

### 🚀 快速開始

#### 安裝

```bash
pip install schemasync-cli
```

PostgreSQL支援：
```bash
pip install schemasync-cli[postgresql]
```

MySQL支援：
```bash
pip install schemasync-cli[mysql]
```

所有資料庫：
```bash
pip install schemasync-cli[all]
```

#### 初始化專案

```bash
# 進入專案目錄
cd myproject

# 初始化 SchemaSync
schemasync init
```

這會建立：
- `migrations/` - 遷移檔案目錄
- `backups/` - 資料庫備份目錄
- `schemasync.yaml` - 設定檔

#### 建立第一個遷移

```bash
schemasync create "add users table"
```

編輯產生的遷移檔案：

```python
def upgrade():
    return """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(255) NOT NULL UNIQUE,
        email VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

def downgrade():
    return """
    DROP TABLE users;
    """
```

#### 應用遷移

```bash
# 查看狀態
schemasync status

# 應用所有待處理的遷移
schemasync migrate

# 或先預覽（試運行）
schemasync migrate --dry-run
```

#### 回滾（如需要）

```bash
# 回滾上一個遷移
schemasync rollback

# 回滾多個遷移
schemasync rollback --steps 3

# 回滾到指定版本
schemasync rollback --to 20250101000000
```

### 📖 配置說明

在專案根目錄建立 `schemasync.yaml`：

```yaml
database:
  driver: sqlite        # sqlite, postgresql, mysql
  host: localhost       # PostgreSQL/MySQL用
  port: 5432           # PostgreSQL/MySQL用
  name: mydatabase.db   # 資料庫名稱或檔案路徑
  user: dbuser         # PostgreSQL/MySQL用
  password: dbpass     # PostgreSQL/MySQL用

migrations:
  directory: migrations
  table_name: schema_migrations
  backup_before_migrate: true
  backup_directory: backups

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

或使用環境變數：
```bash
export SCHEMASYNC_DB_DRIVER=postgresql
export SCHEMASYNC_DB_HOST=localhost
export SCHEMASYNC_DB_NAME=mydb
export SCHEMASYNC_DB_USER=user
export SCHEMASYNC_DB_PASSWORD=pass
```

### 📚 可用命令

| 命令 | 描述 |
|------|------|
| `schemasync init` | 初始化遷移環境 |
| `schemasync create <描述>` | 建立新遷移 |
| `schemasync status` | 顯示遷移狀態 |
| `schemasync migrate` | 執行待處理的遷移 |
| `schemasync migrate --dry-run` | 預覽遷移 |
| `schemasync rollback` | 回滾遷移 |
| `schemasync history` | 顯示遷移歷史 |
| `schemasync config` | 顯示目前配置 |

### 💡 設計理念

SchemaSync 遵循以下原則：

1. **簡潔優先** - 易於學習，易於使用
2. **預設安全** - 備份和試運行模式讓您安心
3. **資料庫無關** - 相同命令適用於所有支援的資料庫
4. **版本控制友善** - 遷移檔案是純Python，完美適配Git

### 📦 專案類型

這是一個 **CLI工具/庫** 專案。不需要發布可執行檔案。

透過pip安裝：
```bash
pip install schemasync-cli
```

### 🤝 貢獻指南

歡迎貢獻！請隨時提交Pull Request。

1. Fork 倉庫
2. 建立特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 📄 開源協議

本專案採用 MIT 協議 - 查看 [LICENSE](LICENSE) 檔案了解詳情。
