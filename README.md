# 提肛小助手 (Kegel Exercise Helper)

一款现代化的PC端提肛运动辅助软件，帮助久坐办公族养成健康习惯。基于linux.do社区讨论需求开发，解决现有软件"简陋、定制性不够"的问题。

## ✨ 功能特性

- ⏰ **智能定时提醒** - 可自定义间隔，支持工作时间限制
- 🎯 **可视化动作指导** - 呼吸节奏动画，专业动作要领
- 📊 **运动数据统计** - 今日/周/月统计，连续天数记录
- 🎨 **现代化界面设计** - Vue3 + Element Plus，流畅动画效果
- 🔧 **丰富的个性化设置** - 运动参数、提醒方式、界面主题
- 💻 **适合办公环境使用** - 系统托盘，快捷键，隐蔽操作
- 🏆 **成就系统** - 运动里程碑，激励持续锻炼
- 🖥️ **跨平台支持** - Web版本 + 桌面应用

## 🛠️ 技术栈

### 后端
- **Python 3.8+** + FastAPI - 高性能API框架
- **SQLAlchemy** - ORM数据库操作
- **APScheduler** - 定时任务调度
- **Pydantic** - 数据验证和序列化

### 前端
- **Vue3** + **TypeScript** - 现代化前端框架
- **Vite** - 快速构建工具
- **Element Plus** - 企业级UI组件库
- **Pinia** - 状态管理
- **Axios** - HTTP客户端

### 桌面化
- **Tauri** - 轻量级桌面应用框架
- **Rust** - 系统层集成
- 系统托盘、通知、快捷键支持

### 动画效果
- **CSS3** 硬件加速动画
- 自定义Vue组件动画
- 呼吸引导、进度指示、奖励效果

## 📁 项目结构

```
tg-helper/
├── backend/                 # Python后端
│   ├── api/                # API路由
│   ├── models/             # 数据模型
│   ├── services/           # 业务服务
│   ├── utils/              # 工具函数
│   ├── main.py             # 应用入口
│   ├── requirements.txt    # Python依赖
│   └── start.py            # 启动脚本
├── frontend/               # Vue3前端
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── stores/         # 状态管理
│   │   ├── utils/          # 工具函数
│   │   └── types/          # 类型定义
│   ├── package.json        # 前端依赖
│   └── vite.config.ts      # Vite配置
├── src-tauri/              # Tauri配置
│   ├── src/                # Rust源码
│   ├── Cargo.toml          # Rust依赖
│   └── tauri.conf.json     # Tauri配置
├── test-integration.md     # 测试指南
├── DEPLOYMENT.md           # 部署指南
└── README.md               # 项目说明
```

## 🚀 快速开始

### 环境要求
- **Python**: 3.8+ (推荐 3.9+)
- **Node.js**: 16+ (推荐 18+)
- **Rust**: 1.70+ (仅桌面应用需要)

### 1. 克隆项目
```bash
git clone https://github.com/hmhm2022/kegel-helper.git
cd kegel-helper
```

### 2. 后端开发
```bash
cd backend
pip install -r requirements.txt
python start.py
```
后端服务: http://localhost:8000

### 3. 前端开发
```bash
cd frontend
npm install
npm run dev
```
前端应用: http://localhost:3000

### 4. 桌面应用开发
```bash
# 安装Tauri CLI
npm install -g @tauri-apps/cli

# 启动桌面应用
npm run tauri:dev
```

## 📱 应用截图

### 主界面
- 运动统计概览
- 快速开始按钮
- 提醒状态控制

### 运动指导页面
- 呼吸节奏动画
- 进度指示器
- 动作要领说明

### 设置页面
- 提醒参数配置
- 运动参数调整
- 界面主题选择

### 统计页面
- 运动数据图表
- 成就系统
- 历史记录

## 🎯 核心功能详解

### 智能提醒系统
- 自定义提醒间隔（5-120分钟）
- 工作时间限制功能
- 多种通知方式（系统通知、音效）
- 全局快捷键支持（Ctrl+Shift+K）

### 运动指导
- 专业的动作要领说明
- 呼吸节奏可视化引导
- 可调节的运动参数（时长3-30秒，次数5-50次）
- 实时进度反馈

### 数据统计
- 今日/本周/本月/总计运动次数
- 连续运动天数记录
- 运动趋势图表（开发中）
- 个人运动历史

### 成就系统
- 初学者、坚持者、百次达人等成就
- 里程碑奖励动画
- 激励性文字和积分系统

## 🔧 开发进度

- [x] **项目规划和技术选型** - 完成技术栈选择和架构设计
- [x] **项目初始化和环境搭建** - 完成前后端项目结构创建
- [x] **后端API开发** - 完成所有核心API接口和业务逻辑
- [x] **前端界面开发** - 完成所有页面和组件开发
- [x] **动画效果实现** - 完成呼吸引导、进度指示、奖励动画
- [x] **Tauri桌面应用集成** - 完成系统托盘、通知、快捷键功能
- [/] **功能测试和优化** - 进行中，完善测试用例和性能优化

## 📋 测试指南

详细的测试指南请参考 [test-integration.md](./test-integration.md)

### 快速测试
```bash
# 后端逻辑验证
cd backend && python verify_logic.py

# 前端组件测试
cd frontend && npm run test

# 桌面应用测试
npm run tauri:dev
```

## 🚀 部署指南

详细的部署指南请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

### 生产构建
```bash
# 前端构建
cd frontend && npm run build

# 桌面应用构建
npm run tauri:build
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范
- 遵循现有代码风格
- 添加适当的注释和文档
- 确保测试通过
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- 感谢 [linux.do](https://linux.do) 社区的需求启发
- 感谢所有开源项目的贡献者
- 感谢测试和反馈的用户们

## 📞 联系我们

- 项目地址: [GitHub Repository](https://github.com/hmhm2022/kegel-helper)
- 问题反馈: [Issues](https://github.com/hmhm2022/kegel-helper/issues)
- 功能建议: [Discussions](https://github.com/hmhm2022/kegel-helper/discussions)

---

**健康提示**: 提肛运动有助于改善盆底肌肉功能，但请根据个人身体状况适量运动。如有不适，请咨询医生。
