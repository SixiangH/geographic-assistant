# Render Deployment / Render 部署

Deploy the committed application as a single Python Web Service. The built React assets in `app/static/ui/` are served by FastAPI; no separate frontend host or Node runtime is needed. `.python-version` pins Python 3.11.16. `render.yaml` specifies the Free plan, Singapore region, dependency install, dynamic `$PORT` start command and `/api/status` health check.

将应用部署为单个 Python Web Service。FastAPI 提供 `app/static/ui/` 中已构建的 React 资源，不需要单独前端平台或 Node 运行时。`.python-version` 固定 Python 3.11.16，`render.yaml` 配置 Free、新加坡区域、依赖安装、动态 `$PORT` 启动命令及 `/api/status` 健康检查。

Set `OPENAI_API_KEY` only in Render's environment settings; never upload `.env`. Use `OPENAI_MODEL=gpt-4o-mini` and `ONLINE_LOOKUP_ENABLED=true`. `/api/status` confirms whether a key is configured, but only actual analysis confirms model connectivity and permissions. Validate live AI recognition, summary and quiz on the deployed URL, plus encyclopedia lookup and browser persistence.

仅在 Render 环境设置中保存 `OPENAI_API_KEY`，不上传 `.env`。使用 `OPENAI_MODEL=gpt-4o-mini`、`ONLINE_LOOKUP_ENABLED=true`。`/api/status` 只说明已配置密钥，实际分析才验证模型连接及权限。必须在部署网址验证识别、摘要、小测、百科检索与浏览器持久化。

Up to eight independent analysis/quiz jobs run concurrently. Duplicate request keys share a lock and cached result; short cache locks do not serialize network calls. Summary and quiz generation overlap. Excess workload produces a retry notice after waiting for a slot; exact simultaneous capacity remains dependent on free CPU and the model account's rate limits. No guarantee of unlimited classroom concurrency is made.

最多八个独立分析/小测任务并发。相同请求共享锁和缓存，短时间缓存锁不串行化网络调用。摘要和小测生成重叠执行。容量不足时等待后提示重试，实际同时使用能力仍取决于免费 CPU 和模型账户限流，不保证无限并发。

The free service sleeps after 15 idle minutes and wakes in about one minute. Open and test it shortly before presentation. Render's local disk is ephemeral; only temporary public-source cache is affected. Bundled knowledge and ten readings are redeployed from GitHub. History, Saved and learning progress remain in each user's browser at the deployed origin. Existing localhost browser records do not transfer automatically. Hosting is free within plan limits; OpenAI usage is billed separately.

免费服务闲置十五分钟后休眠，唤醒约一分钟。演示前提前打开并测试。Render 本地磁盘为临时存储，只影响临时公开来源缓存；内置知识和十份材料从 GitHub 重新部署。History、Saved 和学习进度保存在各用户线上域名对应的浏览器中，localhost 记录不自动迁移。托管在免费额度内免费，OpenAI 调用另外计费。

References / 参考：[FastAPI deployment](https://render.com/docs/deploy-fastapi), [Free limits](https://render.com/docs/free), [Python version](https://render.com/docs/python-version).
