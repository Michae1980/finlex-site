import { defineConfig } from 'vitepress'

// GitHub Pages 项目站需要仓库名前缀；本地预览默认 '/'。
// 与 deploy-pages.yml 中的 DOCS_BASE 环境变量配套。
const base = process.env.DOCS_BASE ?? '/'

export default defineConfig({
  base,
  lang: 'zh-CN',
  title: '问财答税',
  description: '可核对出处的会计准则 / 税法法条 / 案例检索与联想解读',
  cleanUrls: true,
  themeConfig: {
    nav: [
      { text: '指南', link: '/guide/about' },
      { text: '章节', link: '/chapters/' },
      { text: '案例', link: '/cases/' },
      { text: '资源', link: '/resources/citation' }
    ],
    sidebar: {
      '/guide/': [
        {
          text: '指南',
          items: [
            { text: '关于问财答税', link: '/guide/about' },
            { text: '快速开始', link: '/guide/start' },
            { text: '免责声明与合规边界', link: '/guide/compliance' }
          ]
        }
      ],
      '/chapters/': [
        {
          text: '章节',
          items: [
            { text: '章节总览', link: '/chapters/' },
            { text: '会计准则篇', link: '/chapters/accounting' },
            { text: '税法条文篇', link: '/chapters/tax' },
            { text: '案例研读篇', link: '/chapters/cases' }
          ]
        }
      ],
      '/cases/': [
        {
          text: '案例',
          items: [{ text: '案例研讨', link: '/cases/' }]
        }
      ],
      '/resources/': [
        {
          text: '资源',
          items: [
            { text: '引用格式规范', link: '/resources/citation' },
            { text: '官方数据源', link: '/resources/sources' }
          ]
        }
      ]
    },
    outline: { level: [2, 3], label: '本页目录' },
    docFooter: { prev: '上一页', next: '下一页' },
    lastUpdated: { text: '最后更新' },
    search: { provider: 'local' },
    footer: {
      message: '本站内容仅供参考，不构成法律意见、鉴证或审计结论',
      copyright: '问财答税（FinLex）'
    }
  }
})
