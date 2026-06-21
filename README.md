# 剧本杀全栈平台

一个完整的剧本杀（谋杀之谜）在线平台，提供剧本管理、组局预约、DM（主持人）管理、评价系统和社区交流等功能。

## 项目介绍

本项目是一个前后端分离的剧本杀平台，旨在为剧本杀爱好者提供一个线上交流、预约和管理的平台。用户可以浏览剧本、发起或参与组局、评价剧本和DM，以及在社区分享体验。

## 功能列表

### 用户系统
- 用户注册、登录、个人信息管理
- 多种用户角色：普通玩家、DM、店家、管理员
- JWT 认证机制

### 剧本管理
- 剧本列表浏览、详情查看
- 剧本分类（悬疑、恐怖、情感、推理、欢乐、科幻、古风、现代）
- 难度分级（简单、中等、困难、专家）
- 剧本角色管理
- 评分和评价系统

### 游戏组局
- 发起组局、设置时间地点
- 招募玩家、人数管理
- 角色分配（随机/手动）
- 游戏状态管理（招募中、已满、进行中、已完成、已取消）
- 费用管理

### DM 管理
- DM 资质认证
- DM 排班管理
- DM 评分评价
- 擅长剧本类型标签

### 店家管理
- 店家信息管理
- 店铺剧本库
- 组局管理

### 评价系统
- 剧本评价
- DM 评价
- 游戏体验评价
- 匿名评价支持

### 社区功能
- 发帖交流（推荐、测评、二手交易）
- 评论互动
- 点赞、收藏

## 技术栈

### 后端
- **框架**: FastAPI 0.104.1
- **数据库**: SQLite（开发）/ PostgreSQL（生产）
- **ORM**: SQLAlchemy 2.0.23
- **数据验证**: Pydantic 2.5.2
- **认证**: JWT (python-jose) + Passlib (bcrypt)
- **服务器**: Uvicorn 0.24.0
- **数据库迁移**: Alembic 1.12.1

### 前端
- **框架**: Vue 3.4.0
- **路由**: Vue Router 4.2.5
- **状态管理**: Pinia 2.1.7
- **UI 组件库**: Element Plus 2.4.4
- **HTTP 客户端**: Axios 1.6.2
- **构建工具**: Vite 5.0.10
- **CSS 预处理器**: Sass 1.69.5

## 项目结构

```
.
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── crud/           # 数据操作
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── database.py     # 数据库连接
│   │   ├── models.py       # SQLAlchemy 模型
│   │   └── main.py         # 应用入口
│   ├── init_db.py          # 数据库初始化脚本
│   ├── requirements.txt    # Python 依赖
│   ├── .env                # 环境变量
│   └── script_kill.db      # SQLite 数据库
├── frontend/               # 前端项目
│   ├── src/
│   │   ├── api/            # API 接口
│   │   ├── assets/         # 静态资源
│   │   ├── router/         # 路由配置
│   │   ├── store/          # Pinia 状态
│   │   ├── App.vue         # 根组件
│   │   └── main.js         # 入口文件
│   ├── package.json        # NPM 依赖
│   ├── vite.config.js      # Vite 配置
│   └── index.html          # HTML 模板
├── start.sh                # 一键启动脚本
├── start_backend.sh        # 后端启动脚本
├── start_frontend.sh       # 前端启动脚本
├── docker-compose.yml      # Docker Compose 配置
└── README.md               # 项目说明
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 方式一：一键启动（推荐）

```bash
# 一键启动前后端
./start.sh
```

### 方式二：分别启动

#### 启动后端

```bash
# 进入后端目录
cd backend

# 安装依赖（首次运行）
pip install -r requirements.txt

# 初始化数据库（创建测试数据）
python init_db.py

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

或使用启动脚本：

```bash
./start_backend.sh
```

#### 启动前端

```bash
# 进入前端目录
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

或使用启动脚本：

```bash
./start_frontend.sh
```

### 方式三：Docker 启动

```bash
# 启动所有服务
docker-compose up -d

# 停止服务
docker-compose down
```

## 访问地址

- 前端应用: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- 备用 API 文档: http://localhost:8000/redoc

## 测试账号

数据库初始化后，可使用以下测试账号登录：

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123 | 管理员 | 系统管理员 |
| dm_user | dm123456 | DM | 主持人账号 |
| store_user | store123 | 店家 | 店铺管理员 |
| player1 | player123 | 玩家 | 普通玩家 |
| player2 | player123 | 玩家 | 普通玩家 |

## 数据库初始化

首次运行需要初始化数据库并创建测试数据：

```bash
cd backend
python init_db.py
```

初始化脚本会创建：
- 5 个测试用户（不同角色）
- 8 个不同类型的剧本
- 每个剧本包含 4-6 个角色
- 5 个组局（不同状态）
- 部分游戏参与者
- 若干评价和社区帖子

## API 接口

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息
- `PUT /api/auth/me` - 更新用户信息

### 剧本接口
- `GET /api/scripts/` - 获取剧本列表
- `POST /api/scripts/` - 创建剧本
- `GET /api/scripts/{id}` - 获取剧本详情
- `PUT /api/scripts/{id}` - 更新剧本
- `DELETE /api/scripts/{id}` - 删除剧本

### 游戏接口
- `GET /api/games/` - 获取游戏列表
- `POST /api/games/` - 创建游戏
- `GET /api/games/{id}` - 获取游戏详情
- `POST /api/games/{id}/join` - 加入游戏
- `POST /api/games/{id}/leave` - 离开游戏

### 其他接口
- DM 管理: `/api/dm/*`
- 评价系统: `/api/reviews/*`
- 社区: `/api/community/*`

## 开发说明

### 后端开发

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload
```

### 前端开发

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 环境变量配置

后端环境变量 (`backend/.env`)：

```env
# 数据库连接
DATABASE_URL=sqlite:///./script_kill.db

# JWT 配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## 常见问题

### 1. 端口被占用

如果 8000 或 5173 端口被占用，可以修改启动端口：

```bash
# 后端指定端口
uvicorn app.main:app --reload --port 8001

# 前端修改 vite.config.js 或使用
npm run dev -- --port 5174
```

### 2. 数据库文件损坏

删除 `backend/script_kill.db` 重新运行初始化脚本即可。

### 3. 依赖安装失败

建议使用国内镜像源：

```bash
# Python
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# NPM
npm install --registry=https://registry.npmmirror.com
```

## License

MIT
