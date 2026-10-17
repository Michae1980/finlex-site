# 问财答税 · FinLex 文档站

「问财答税（FinLex）」的对外文档站：**可核对出处的会计准则 / 税法法条 / 案例检索与联想解读**。

结构参考 [walkinglabs/learn-harness-engineering](https://github.com/walkinglabs/learn-harness-engineering)（MIT）的课程站形态：Markdown 内容 + VitePress + GitHub Actions 自动部署 GitHub Pages。

## 目录结构

```
finlex-site/
├── README.md
├── package.json
├── docs/
│   ├── index.md              # 首页（hero + 特性卡）
│   ├── .vitepress/config.mts # 站点配置（导航 / 侧栏 / 中文界面）
│   ├── guide/                # 指南：关于 / 快速开始 / 合规边界
│   ├── chapters/             # 章节：会计准则篇 / 税法条文篇 / 案例研读篇
│   ├── cases/                # 案例研讨
│   ├── resources/            # 资源：引用格式 / 官方数据源
│   └── 同类项目调研.md        # 立项调研留痕
└── .github/workflows/
    └── deploy-pages.yml      # push 到 main 自动构建并部署 GitHub Pages
```

## 本地运行

```bash
npm install
npm run docs:dev      # 本地预览 http://localhost:5173
npm run docs:build    # 构建静态站（输出 docs/.vitepress/dist）
npm run docs:preview  # 预览构建产物
```

## 发布到 GitHub Pages

1. 在 GitHub 新建仓库（建议名 `finlex-site`，公开仓库）；
2. 推送本目录到该仓库 `main` 分支；
3. 仓库 Settings → Pages → Source 选择 **GitHub Actions**；
4. 之后每次 push 到 `main`，`deploy-pages.yml` 自动构建并部署。

访问地址：`https://<用户名>.github.io/<仓库名>/`（站点 `base` 由工作流自动按仓库名注入）。

## 内容纪律

- **有出处才发布**：引用格式见 [docs/resources/citation.md](docs/resources/citation.md)；
- **对外隐私**：任何页面不得出现本机路径、内部工具名、采集过程；来源只写官方机构名 + 官网 URL；
- **合规红线**：不构成法律意见 / 鉴证 / 审计结论；不承诺节税；免责声明常驻 [docs/guide/compliance.md](docs/guide/compliance.md)。

## 同类项目调研（立项留痕）

完整台账见 [docs/同类项目调研.md](docs/同类项目调研.md)。

| 项 | 结论 |
|----|------|
| 检索日期 | 2026-10-17 |
| 查询词（多组） | tax law knowledge base documentation site / tax accounting knowledge base website / tax knowledge base vitepress / 会计 税法 知识库 / 税法 文档 等（详见台账） |
| 高契合同类 | **无**（中文财税知识站 + VitePress 形态未检出可比项目） |
| 结论 | **自建**；结构只读借鉴 walkinglabs/learn-harness-engineering（MIT，API 核实 ⭐19988 / 2026-10-01 有提交），不复用其代码 |
