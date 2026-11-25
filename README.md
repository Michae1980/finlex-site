# 财税法规通

「财税法规通」对外静态知识站：**可核对出处的会计准则 / 税法法条 / 审计准则 / 实务案例检索与交叉联想平台**。

界面与工程范式借鉴 `formula-graph`（零第三方依赖 Python 构建校验 + 静态单页渐进式网页应用 PWA + GitHub Pages 自动发布），并针对财税长文本阅读场景采用「左侧 36% 导航目录 + 右侧 64% 法条原文主阅读区」可拖拽分栏布局。

## 目录结构

```text
finlex-site/
├── .github/workflows/deploy-pages.yml  # GitHub Pages 自动校验、构建与发布工作流
├── scripts/
│   ├── build_prototype.py              # 从 finlex.db 脱敏导出索引、全库正文语料与单文档分片
│   ├── build_site.py                   # 构建正式 site/ PWA 目录（支持本地同步与 --ci 模式）
│   └── validate.py                     # 零依赖静态站完整性与隐私合规校验器
├── prototype/
│   ├── template.html                   # 前端交互模板（卡片列表 / 台账表格 / 聚焦图谱 / 主阅读区）
│   ├── pwa/                            # PWA 清单、Service Worker 与应用图标源码
│   └── index.html                      # 本地双击离线预览入口
└── site/                               # 可直接托管部署的正式静态网站 + PWA 输出目录
    ├── index.html
    ├── manifest.webmanifest
    ├── sw.js
    ├── icon.svg / icon-192.png / icon-512.png
    └── data/
        ├── index.js                    # 首屏轻量法规索引与 405 条关联边（~321 KB）
        ├── fulltext.js                 # 按需加载的全库 5,417 条条文正文语料
        └── docs/doc_<id>.js            # 210 份按需加载的单文档条文分片
```

## 本地运行与构建

- **直接离线双击查看**：用现代浏览器打开 `site/index.html`（或 `prototype/index.html`），无需本地服务器即可完整使用。
- **本地预览 PWA 安装与离线缓存**：
  ```bash
  python3 -m http.server -d site 8080
  ```
  浏览器打开 `http://localhost:8080`，点击顶部「⬇ 安装桌面版」可安装为独立桌面应用。
- **从 `finlex.db` 同步最新数据并校验构建**（仅需 Python 3.9+，零第三方依赖）：
  ```bash
  python3 scripts/build_site.py && python3 scripts/validate.py
  ```

## 自动发布到 GitHub Pages

1. 将本仓库推送至 GitHub 的 `main` 分支（含 `site/data/` 脱敏静态分片）；
2. 在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**；
3. 每次推送到 `main`，`.github/workflows/deploy-pages.yml` 自动运行 `python3 scripts/build_site.py --ci` 与 `python3 scripts/validate.py`，校验通过后发布 `site/`。

## 内容与合规纪律

- **有出处才发布**：标准引用格式 `《文件名》（文号）第X条`，正文每条提供一键复制标准引用按钮与官网原文链接；
- **对外隐私红线**：构建与校验阶段强制剥离内部备注与本机路径，保证 0 隐私泄漏；
- **合规边界**：全站常驻免责声明，不构成法律意见、涉税鉴证或审计结论；实务案例恒置底并标注「案例参考，非规范依据」。
